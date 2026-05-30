# Guia de Consultas SQL (SQLite) - Informações de Compras e Editais

Este documento serve como referência técnica detalhada do banco de dados (SQLite) para ajudar na criação e validação de consultas SQL (Queries) em cima da base de compras públicas, editais, itens e os resultados.

---

## 1. Estrutura das Tabelas (Esquema)

### Tabela `editais`
Contém os dados cabeçalho da licitação (nível do edital).
*   **`numero_controle_pncp`** (TEXT/VARCHAR) - **Primary Key** | Identificador único do edital.
*   **`uf`** (TEXT) - Unidade Federativa. **Cuidado:** Filtros estaduais devem OBRIGATORIAMENTE ser feitos utilizando esta coluna (ex: `WHERE uf = 'SP'`).
*   **`municipio`** (TEXT) - Nome do Município.
*   **`orgao_cnpj`** (TEXT) - CNPJ do órgão comprador.
*   **`orgao_nome`** (TEXT) - Nome do órgão comprador.
*   **`objeto`** (TEXT) - Descrição resumida da licitação/compra.
*   **`data_abertura`** (DATE) - Data da publicação/abertura.
*   **`data_encerramento`** (DATE) - Data do fim da vigência/recebimento.
*   **`valor_estimado`** (NUMERIC/FLOAT) - Valor orçado (nível do edital inteiro).
*   **`modalidade_nome`** (TEXT) - Ex: 'Pregão', 'Dispensa', etc.
*   **`modalidade_id`** (INTEGER) - ID da modalidade.
*   **`situacao_compra_nome`** (TEXT) - Status principal da licitação.
*   **`tipo_contratacao`** (TEXT) - Forma ou tipo de contratação.

### Tabela `itens`
Contém os desdobramentos de cada edital, sendo os itens/serviços específicos que foram licitados.
*   **`id`** (INTEGER) - **Primary Key** gerada automaticamente.
*   **`numero_controle_pncp`** (TEXT) - **Foreign Key** apontando para `editais.numero_controle_pncp`.
*   **`numero_item`** (INTEGER) - Sequencial de identificação do item **dentro do edital**.
*   **`lote`** (INTEGER) - Número do lote.
*   **`descricao`** (TEXT) - O que está sendo comprado neste item especificamente.
*   **`quantidade`** (NUMERIC/FLOAT) - Quantidade licitada.
*   **`valor_unitario`** (NUMERIC/FLOAT) - Valor estipulado para a unidade.
*   **`valor_total`** (NUMERIC/FLOAT) - Valor estimado somado. **Regra de Negócio:** Para somar "O valor total estimado" de compras, some ou use esta coluna.
*   **`unidade_medida`** (TEXT) - Ex: 'Unid', 'Serv', 'Litro'.
*   **`categoria`** (TEXT) - Classificação/catálogo.

### Tabela `resultados_itens`
Contém a adjudicação ou homologação dos itens, evidenciando quem ganhou, por quanto e se foi efetivado.
*   **`id`** (INTEGER) - **Primary Key** gerada auto incrementalmente.
*   **`numero_controle_pncp`** (TEXT) - **Foreign Key**.
*   **`numero_item`** (INTEGER) - **Foreign Key**.
*   **`sequencial_resultado`** (INTEGER) - Utilizado caso tenham várias etapas de submissão/resultados.
*   **`fornecedor_cnpj`** (TEXT) - Conta do vencedor da licitação/item.
*   **`fornecedor_nome`** (TEXT) - Nome da empresa vencedora.
*   **`valor_homologado_unitario`** (NUMERIC/FLOAT) - Preço final fechado da unidade.
*   **`valor_homologado_total`** (NUMERIC/FLOAT) - Preço final fechado que deverá ser pago. **Regra de Negócio:** "Gasto Real", "Valor Contratado", devem obrigatoriamente realizar SUM() ou basear cálculos sobre esta coluna.
*   **`quantidade_homologada`** (NUMERIC/FLOAT) - Qtde real comprada do ganhador.
*   **`situacao_resultado`** (TEXT) - Ex: "Homologado", "Adjudicado", "Fracassado", "Deserto".

---

## 2. Relacionamentos Básicos (JOINs)

Para agrupar dados do contrato inicial, com os itens e verificar quem os venceu, preste atenção aos JOINS corretos, caso contrário, haverá explosão cartesiana (dados duplicados).

### `editais` -> `itens`
Relacionamento **(1:N)**. Usa apenas a PK principal do edital.
```sql
SELECT e.orgao_nome, i.descricao
FROM editais e
INNER JOIN itens i
  ON e.numero_controle_pncp = i.numero_controle_pncp;
```

### `itens` -> `resultados_itens`
Relacionamento **(1:N)**. Uma junção confiável OBRIGA verificar O edital E O número do item correspondente simultaneamente.
```sql
SELECT i.descricao, r.fornecedor_nome, r.valor_homologado_total
FROM itens i
INNER JOIN resultados_itens r
  ON i.numero_controle_pncp = r.numero_controle_pncp
  AND i.numero_item = r.numero_item;
```

---

## 3. Consultas Frequentes (Exemplos Práticos)

### A. Total Gasto (Homologado) por Estado (UF)
Como o filtro de UF vive em `editais`, mas o "Gasto Real" está em `resultados_itens`, as 3 tabelas participam da composição. Recomendado fazer restrição de situação (se necessário)

```sql
SELECT
    e.uf,
    SUM(r.valor_homologado_total) as gasto_total_real
FROM editais e
JOIN itens i ON e.numero_controle_pncp = i.numero_controle_pncp
JOIN resultados_itens r ON i.numero_controle_pncp = r.numero_controle_pncp
                       AND i.numero_item = r.numero_item
WHERE r.situacao_resultado = 'Homologado' -- Opcional, dependendo da necessidade de ver apenas homologados
GROUP BY e.uf
ORDER BY gasto_total_real DESC;
```

### B. Quais órgãos do "RS" mais realizam licitações (Volume / Frequência)?
Utiliza apenas a base de cabeçalho `editais`.

```sql
SELECT
    e.orgao_nome,
    COUNT(e.numero_controle_pncp) as quantidade_editais
FROM editais e
WHERE e.uf = 'RS'
GROUP BY e.orgao_nome
ORDER BY quantidade_editais DESC
LIMIT 10;
```

### C. Evolução ou Maior Gasto com de Fornecedores Específicos
Quais empresas ganharam mais dinheiro com o governo em pregões homologados.

```sql
SELECT
    r.fornecedor_nome,
    r.fornecedor_cnpj,
    SUM(r.valor_homologado_total) as valor_acumulado_ganho
FROM resultados_itens r
GROUP BY r.fornecedor_nome, r.fornecedor_cnpj
ORDER BY valor_acumulado_ganho DESC
LIMIT 5;
```

### D. Encontrar as modalidades que mais gastam em um município ("Porto Alegre" e "RS")
Lembre-se sempre de colocar a UF junto com o Município pra evitar colisões de cidades homônimas em estados diferentes.

```sql
SELECT 
    e.modalidade_nome,
    SUM(r.valor_homologado_total) as volume_dinheiro_modalidade
FROM editais e
JOIN itens i ON e.numero_controle_pncp = i.numero_controle_pncp
JOIN resultados_itens r ON i.numero_controle_pncp = r.numero_controle_pncp
                       AND i.numero_item = r.numero_item
WHERE e.uf = 'RS' AND e.municipio = 'Porto Alegre'
GROUP BY e.modalidade_nome
ORDER BY volume_dinheiro_modalidade DESC;
```

---

## 4. Dicas Importantes para Uso com IA LangChain / SQL Agents
* **Tipos Numéricos**: Em SQLite, cuide para realizar converções numéricas implícitas se os dados não caírem formatados perfeitamente (Cuidado com `,` no lugar de `.`). 
* **LIMIT**: Como se trata de dashboard público ou de IA, sempre delimite suas respostas genéricas utilizando `ORDER BY <campo> DESC LIMIT N` caso as linhas retornadas tendam a ser altas para listagens curtas no Chat/Tela.
* **Capitalização / Acentuação**: Em bancos embarcados SQLite sem extensores customizados, `LIKE` no formato simples é Case-Insensitive (para carácteres ASCII), mas certifique-se de tratar `UPPER()` caso sinta perda de performance ou acentuações não tratadas nas consultas do bot.
