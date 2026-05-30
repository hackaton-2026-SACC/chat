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

@router.get("/{municipio}")
def municipio_dashboard(municipio: str, db: Session = Depends(get_db)) -> DashboardMunicipioData:
    
    # 1. Busca todos os municipios distintos na base para fazer match tolerante a acentos
    query_all_mun = "SELECT DISTINCT municipio FROM editais WHERE uf = 'PB' AND municipio IS NOT NULL AND municipio != ''"
    all_mun_rows = db.execute(text(query_all_mun)).fetchall()
    
    import unicodedata
    def normalize(val: str) -> str:
        val = val.strip().lower()
        val = "".join(c for c in unicodedata.normalize('NFD', val) if unicodedata.category(c) != 'Mn')
        return val.replace("-", "").replace(" ", "")
        
    normalized_target = normalize(municipio)
    matched_municipio = municipio
    
    for row in all_mun_rows:
        db_mun = row[0]
        if normalize(db_mun) == normalized_target:
            matched_municipio = db_mun
            break

    query_contratos_mun = """
        SELECT count(*) AS total_contratos
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.municipio = :municipio AND e.uf = 'PB'
    """
    contratos_pelo_municipio = db.execute(text(query_contratos_mun), {"municipio": matched_municipio}).scalar() or 0

    query_gasto_mun = """
        SELECT SUM(r.valor_homologado_total) AS gasto_pelo_municipio
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.municipio = :municipio AND e.uf = 'PB'
    """
    gasto_pelo_municipio = db.execute(text(query_gasto_mun), {"municipio": matched_municipio}).scalar() or 0.0

    query_orgaos = """
        SELECT e.orgao_nome, COUNT(DISTINCT e.numero_controle_pncp) AS total_editais
        FROM editais e
        WHERE e.municipio = :municipio AND e.uf = 'PB'
        GROUP BY e.orgao_cnpj, e.orgao_nome
        ORDER BY total_editais DESC
        LIMIT 10
    """
    orgaos_mais_contratam = [
        {"orgao": row.orgao_nome, "contratos": row.total_editais}
        for row in db.execute(text(query_orgaos), {"municipio": matched_municipio})
    ]

    query_maiores_contratos = """
        SELECT e.orgao_nome, e.objeto, e.data_encerramento, SUM(r.valor_homologado_total) AS total_homologado
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.municipio = :municipio AND e.uf = 'PB' AND e.data_encerramento >= date('now', '-12 months')
        GROUP BY e.numero_controle_pncp
        ORDER BY total_homologado DESC
        LIMIT 10
    """
    maiores_contratos_ultimo_ano = [
        {"contrato": row.objeto, "valor": row.total_homologado or 0.0}
        for row in db.execute(text(query_maiores_contratos), {"municipio": matched_municipio})
    ]

    query_evolucao_gastos = """
        SELECT strftime('%Y-%m', e.data_encerramento) AS mes, SUM(r.valor_homologado_total) AS total_gasto
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.municipio = :municipio AND e.uf = 'PB' AND e.data_encerramento IS NOT NULL AND e.data_encerramento >= date('now', '-12 months')
        GROUP BY mes
        ORDER BY mes ASC
    """
    evolucao_gastos_mes = [
        {"mes": row.mes, "valor": row.total_gasto or 0.0}
        for row in db.execute(text(query_evolucao_gastos), {"municipio": matched_municipio})
    ]

    query_mod_contratam = """
        SELECT e.modalidade_nome, COUNT(DISTINCT e.numero_controle_pncp) AS total_editais
        FROM editais e
        WHERE e.municipio = :municipio AND e.uf = 'PB'
        GROUP BY e.modalidade_nome
        ORDER BY total_editais DESC
    """
    modalidades_mais_contratam = [
        {"modalidade": row.modalidade_nome, "quantidade": row.total_editais}
        for row in db.execute(text(query_mod_contratam), {"municipio": matched_municipio})
    ]

    query_mod_gastam = """
        SELECT e.modalidade_nome, SUM(r.valor_homologado_total) AS total_gasto
        FROM resultados_itens r
        JOIN itens i ON r.numero_controle_pncp = i.numero_controle_pncp AND r.numero_item = i.numero_item
        JOIN editais e ON i.numero_controle_pncp = e.numero_controle_pncp
        WHERE e.municipio = :municipio AND e.uf = 'PB'
        GROUP BY e.modalidade_nome
        ORDER BY total_gasto DESC
    """
    modalidades_mais_gastam = [
        {"modalidade": row.modalidade_nome, "valor": row.total_gasto or 0.0}
        for row in db.execute(text(query_mod_gastam), {"municipio": matched_municipio})
    ]

    return {
        "contratos_pelo_municipio": contratos_pelo_municipio,
        "gasto_pelo_municipio": gasto_pelo_municipio,
        "orgaos_mais_contratam": orgaos_mais_contratam,
        "maiores_contratos_ultimo_ano": maiores_contratos_ultimo_ano,
        "evolucao_gastos_mes": evolucao_gastos_mes,
        "modalidades_mais_contratam": modalidades_mais_contratam,
        "modalidades_mais_gastam": modalidades_mais_gastam,
        "nome_real": matched_municipio
    }
