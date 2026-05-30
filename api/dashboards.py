from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.models import DashboardData, DashboardMunicipioData
from core.db import get_db

router = APIRouter()

@router.get("/")
def dashboardd(db: Session = Depends(get_db)) -> DashboardData:
    
    query_total_contratos = """
        SELECT count(*) AS total_homologado
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.uf = 'PB'
    """
    total_contratos = db.execute(text(query_total_contratos)).scalar() or 0.0

    query_total_estado = """
        SELECT SUM(r.valor_homologado_total) AS total_homologado
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.uf = 'PB'
    """
    total_estado = db.execute(text(query_total_estado)).scalar() or 0.0

    query_orgaos = """
        SELECT e.orgao_nome, COUNT(DISTINCT e.numero_controle_pncp) AS total_editais
        FROM editais e
        WHERE e.uf = 'PB'
        GROUP BY e.orgao_cnpj, e.orgao_nome
        ORDER BY total_editais DESC
        LIMIT 10
    """
    orgaos_mais_contratam = [
        {"orgao": row.orgao_nome, "contratos": row.total_editais}
        for row in db.execute(text(query_orgaos))
    ]

    query_mun_gastam = """
        SELECT e.municipio, SUM(r.valor_homologado_total) AS total_homologado
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.uf = 'PB'
        GROUP BY e.municipio
        ORDER BY total_homologado DESC
        LIMIT 10
    """
    municipios_mais_gastam = [
        {"municipio": row.municipio, "gasto": row.total_homologado or 0.0}
        for row in db.execute(text(query_mun_gastam))
    ]

    query_mun_contratam = """
        SELECT e.municipio, COUNT(DISTINCT e.numero_controle_pncp) AS total_editais
        FROM editais e
        WHERE e.uf = 'PB'
        GROUP BY e.municipio
        ORDER BY total_editais DESC
        LIMIT 10
    """
    municipios_mais_contratam = [
        {"municipio": row.municipio, "contratos": row.total_editais}
        for row in db.execute(text(query_mun_contratam))
    ]

    query_mod_contratam = """
        SELECT e.modalidade_nome, COUNT(DISTINCT e.numero_controle_pncp) AS total_editais
        FROM editais e
        WHERE e.uf = 'PB'
        GROUP BY e.modalidade_nome
        ORDER BY total_editais DESC
    """
    modalidades_mais_contratam = [
        {"modalidade": row.modalidade_nome, "quantidade": row.total_editais}
        for row in db.execute(text(query_mod_contratam))
    ]

    query_mod_gastam = """
        SELECT e.modalidade_nome, SUM(r.valor_homologado_total) AS total_gasto
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.uf = 'PB'
        GROUP BY e.modalidade_nome
        ORDER BY total_gasto DESC
    """
    modalidades_mais_gastam = [
        {"modalidade": row.modalidade_nome, "valor": row.total_gasto or 0.0}
        for row in db.execute(text(query_mod_gastam))
    ]

    query_evolucao_gastos = """
        SELECT strftime('%Y-%m', e.data_encerramento) AS mes, SUM(r.valor_homologado_total) AS total_gasto
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.uf = 'PB' AND e.data_encerramento IS NOT NULL AND e.data_encerramento >= date('now', '-12 months')
        GROUP BY mes
        ORDER BY mes ASC
    """
    evolucao_gastos_ano = [
        {"mes": row.mes, "valor": row.total_gasto or 0.0}
        for row in db.execute(text(query_evolucao_gastos))
    ]

    return {
        "total_contratos": total_contratos,
        "total_estado": total_estado,
        "orgaos_mais_contratam": orgaos_mais_contratam,
        "municipios_mais_contratam": municipios_mais_contratam,
        "municipios_mais_gastam": municipios_mais_gastam,
        "modalidades_mais_contratam": modalidades_mais_contratam,
        "modalidades_mais_gastam": modalidades_mais_gastam,
        "evolucao_gastos_ano": evolucao_gastos_ano,
    }

@router.get("/{municipio_ibge_id}")
async def municipio_dashboard(municipio_ibge_id: str) -> DashboardMunicipioData:
    return {
        "contratos_pelo_municipio": 1200,
        "gasto_pelo_municipio": 35000000.0,
        "orgaos_mais_contratam": [
            {"orgao": "Secretaria de Saúde", "contratos": 450},
            {"orgao": "Secretaria de Educação", "contratos": 320},
            {"orgao": "Gabinete do Prefeito", "contratos": 150},
            {"orgao": "Secretaria de Obras", "contratos": 110},
            {"orgao": "Secretaria de Segurança", "contratos": 85},
        ],
        "maiores_contratos_ultimo_ano": [
            {"contrato": "Construção de Hospital", "valor": 15000000.0},
            {"contrato": "Reforma de Escolas", "valor": 8500000.0},
            {"contrato": "Compra de Medicamentos", "valor": 4200000.0},
            {"contrato": "Pavimentação", "valor": 3800000.0},
            {"contrato": "Merenda Escolar", "valor": 2900000.0},
        ],
        "evolucao_gastos_mes": [
            {"mes": "Janeiro", "valor": 2500000.0},
            {"mes": "Fevereiro", "valor": 3200000.0},
            {"mes": "Março", "valor": 2800000.0},
            {"mes": "Abril", "valor": 4100000.0},
            {"mes": "Maio", "valor": 3900000.0},
        ],
        "modalidades_mais_contratam": [
            {"modalidade": "Pregão Eletrônico", "quantidade": 520},
            {"modalidade": "Dispensa de Licitação", "quantidade": 140},
            {"modalidade": "Inexigibilidade", "quantidade": 85},
            {"modalidade": "Concorrência", "quantidade": 45},
            {"modalidade": "Tomada de Preços", "quantidade": 20},
        ],
        "modalidades_mais_gastam": [
            {"modalidade": "Pregão Eletrônico", "valor": 120000000.0},
            {"modalidade": "Concorrência", "valor": 80000000.0},
            {"modalidade": "Dispensa de Licitação", "valor": 15000000.0},
            {"modalidade": "Inexigibilidade", "valor": 10000000.0},
            {"modalidade": "Tomada de Preços", "valor": 5000000.0},
        ]
    }
