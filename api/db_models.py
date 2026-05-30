from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.db import Base

class Edital(Base):
    __tablename__ = "editais"

    numero_controle_pncp = Column(String, primary_key=True, index=True)
    uf = Column(String, index=True)
    municipio = Column(String, index=True)
    orgao_cnpj = Column(String)
    orgao_nome = Column(String)
    objeto = Column(String)
    data_abertura = Column(Date)
    data_encerramento = Column(Date)
    valor_estimado = Column(Float)
    modalidade_nome = Column(String)
    modalidade_id = Column(Integer)
    situacao_compra_nome = Column(String)
    tipo_contratacao = Column(String)

    itens = relationship("Item", back_populates="edital")
    # Para resultados diretamente se necessário
    resultados = relationship("ResultadoItem", back_populates="edital")

class Item(Base):
    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_controle_pncp = Column(String, ForeignKey("editais.numero_controle_pncp"), index=True)
    numero_item = Column(Integer, index=True)
    lote = Column(Integer)
    descricao = Column(String)
    quantidade = Column(Float)
    valor_unitario = Column(Float)
    valor_total = Column(Float)
    unidade_medida = Column(String)
    categoria = Column(String)

    edital = relationship("Edital", back_populates="itens")
    resultados = relationship("ResultadoItem", back_populates="item")

class ResultadoItem(Base):
    __tablename__ = "resultados_itens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_controle_pncp = Column(String, ForeignKey("editais.numero_controle_pncp"), index=True)
    # A constraint no nível de código pra junção, usando as chaves estrangeiras apropriadamente
    numero_item = Column(Integer) 
    
    # Definição das relações considerando que um item é unicamente identificado por numero_controle + numero_item
    # No SQLAchemy, definiremos a relação foreign key explicitamente para fins de navegação
    sequencial_resultado = Column(Integer)
    fornecedor_cnpj = Column(String)
    fornecedor_nome = Column(String)
    valor_homologado_unitario = Column(Float)
    valor_homologado_total = Column(Float)
    quantidade_homologada = Column(Float)
    situacao_resultado = Column(String)

    edital = relationship("Edital", back_populates="resultados")
    item = relationship("Item", back_populates="resultados", foreign_keys=[numero_controle_pncp, numero_item],
                        primaryjoin="and_(ResultadoItem.numero_controle_pncp==Item.numero_controle_pncp, ResultadoItem.numero_item==Item.numero_item)")

