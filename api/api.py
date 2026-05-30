from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dashboardd():
    return {
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
        "modalidades_gastos": [
            {"modalidade": "Pregão Eletrônico", "valor": 120000000.0},
            {"modalidade": "Concorrência", "valor": 80000000.0},
            {"modalidade": "Dispensa de Licitação", "valor": 15000000.0},
            {"modalidade": "Inexigibilidade", "valor": 10000000.0},
            {"modalidade": "Tomada de Preços", "valor": 5000000.0},
        ],
        "evolucao_gastos_ano": [
            {"mes": "2020", "valor": 100000000.0},
            {"mes": "2021", "valor": 120000000.0},
            {"mes": "2022", "valor": 150000000.0},
            {"mes": "2023", "valor": 180000000.0},
            {"mes": "2024", "valor": 130000000.0},
        ]
    }
