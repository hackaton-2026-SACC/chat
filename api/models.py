from typing_extensions import TypedDict

class DashboardData(TypedDict):
    total_contratos: int
    total_estado: float
    orgaos_mais_contratam: list[dict[str, str | int]]
    municipios_mais_gastam: list[dict[str, str | float]]
    municipios_mais_contratam: list[dict[str, str | int]]
    modalidades_mais_contratam: list[dict[str, str | float]]
    modalidades_mais_gastam: list[dict[str, str | float]]
    evolucao_gastos_ano: list[dict[str, str | float]]

class DashboardMunicipioData(TypedDict):
    contratos_pelo_municipio: int
    gasto_pelo_municipio: float
    orgaos_mais_contratam: list[dict[str, str | int]]
    maiores_contratos_ultimo_ano: list[dict[str, str | float]]
    evolucao_gastos_mes: list[dict[str, str | float]]
    modalidades_mais_gastam: list[dict[str, str | float]]
    modalidades_mais_contratam: list[dict[str, str | float]]