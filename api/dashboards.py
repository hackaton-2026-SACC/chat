from fastapi import APIRouter
from api.models import DashboardData, DashboardMunicipioData

router = APIRouter()

@router.get("/")
async def dashboardd() -> DashboardData:
    return {
        "orgaos_mais_contratam": [
            {"orgao": "Secretaria de Saúde", "contratos": 450},
            {"orgao": "Secretaria de Educação", "contratos": 320},
            {"orgao": "Gabinete do Prefeito", "contratos": 150},
            {"orgao": "Secretaria de Obras", "contratos": 110},
            {"orgao": "Secretaria de Segurança", "contratos": 85},
        ],
        "municipios_mais_contratam": [
            {"municipio": "São Paulo", "contratos": 1500},
            {"municipio": "Rio de Janeiro", "contratos": 1200},
            {"municipio": "Belo Horizonte", "contratos": 950},
            {"municipio": "Curitiba", "contratos": 800},
            {"municipio": "Porto Alegre", "contratos": 750},
        ],
        "municipios_mais_gastam": [
            {"municipio": "São Paulo", "gasto": 50000000.0},
            {"municipio": "Rio de Janeiro", "gasto": 45000000.0},
            {"municipio": "Brasília", "gasto": 40000000.0},
            {"municipio": "Belo Horizonte", "gasto": 35000000.0},
            {"municipio": "Curitiba", "gasto": 30000000.0},
        ],
        "modalidades_mais_contratam": [
            {"modalidade": "Pregão Eletrônico", "valor": 120000000.0},
            {"modalidade": "Concorrência", "valor": 80000000.0},
            {"modalidade": "Dispensa de Licitação", "valor": 15000000.0},
            {"modalidade": "Inexigibilidade", "valor": 10000000.0},
            {"modalidade": "Tomada de Preços", "valor": 5000000.0},
        ],
        "modalidades_mais_gastam": [
            {"modalidade": "Pregão Eletrônico", "valor": 120000000.0},
            {"modalidade": "Concorrência", "valor": 80000000.0},
            {"modalidade": "Dispensa de Licitação", "valor": 15000000.0},
            {"modalidade": "Inexigibilidade", "valor": 10000000.0},
            {"modalidade": "Tomada de Preços", "valor": 5000000.0},
        ],
        "evolucao_gastos_ano": [
            {"mes": "Janeiro", "valor": 2500000.0},
            {"mes": "Fevereiro", "valor": 3200000.0},
            {"mes": "Março", "valor": 2800000.0},
            {"mes": "Abril", "valor": 4100000.0},
            {"mes": "Maio", "valor": 3900000.0},
        ]
    }

@router.get("/{municipio_ibge_id}")
async def municipio_dashboard(municipio_ibge_id: str) -> DashboardMunicipioData:
    return {
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
