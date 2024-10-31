from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

db = create_engine("sqlite:///bancoteste.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

# Tabelas
#===================================================================================================

class Prontuario(Base):
    __tablename__ = "prontuario"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
#=================================================================================================

class Paciente(Base):
    __tablename__ = "paciente"
    consultas = relationship("Consulta", back_populates="paciente")

    id                  = Column("id", Integer, primary_key=True, autoincrement=True)
    cpf                 = Column("cpf", String(14), unique=True, nullable=False)  
    nome                = Column(String, nullable=False) 
    data_nasc           = Column(DateTime, nullable=True)  
    email               = Column(String, nullable=True)
    telefone            = Column(String(15), nullable=True)
    sexo                = Column(String(1), nullable=False)
    endereco            = Column(String, nullable=True)
    naturalidade        = Column(String, nullable=True)
    prontuario_numero   = Column("prontuario_numero", ForeignKey('prontuario.id'), nullable=True)
#================================================================================================

class Medico(Base):
    __tablename__ = "medico"
    consultas = relationship("Consulta", back_populates="medico")

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    crm             = Column("crm", String(13), unique=True, nullable=False)
    nome            = Column(String, nullable=False)
    especialidade   = Column(String, nullable=True)
#=============================================================================================

class Consulta(Base):
    __tablename__ = "consulta"
    medico      = relationship("Medico", back_populates="consultas")
    paciente    = relationship("Paciente", back_populates="consultas")

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    data_hora       = Column(DateTime, nullable=False)
    status          = Column(String, nullable=True)
    paciente_cpf    = Column("paciente_cpf", ForeignKey('paciente.cpf'), nullable=False)
    medico_crm      = Column("medico_crm", ForeignKey('medico.crm'), nullable=False)
#==========================================================================================

class Diagnostico(Base):
    __tablename__ = "diagnostico"
    consulta = relationship("Consulta", back_populates="diagnosticos")

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    cid             = Column(String, nullable=True)
    descricao       = Column(String, nullable=True)
    consulta_id     = Column("consulta_id", ForeignKey('consulta.id'), nullable=False)
    paciente_cpf    = Column("paciente_cpf", ForeignKey('paciente.cpf'), nullable=False)
    medico_crm      = Column("medico_crm", ForeignKey('medico.crm'), nullable=False)
#=========================================================================================

class Tratamento(Base):
    __tablename__ = "tratamento"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    descricao       = Column(String, nullable=True)
    duracao         = Column(Integer, nullable=True)
    medicamentos    = Column(String, nullable=True)
    diagnostico_id  = Column("diagnostico_id", ForeignKey('diagnostico.id'), nullable=False)

#=========================================================================================
class Receita(Base):
    __tablename__ = "receita"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    medico_id       = Column(Integer, ForeignKey("medico.id"), nullable=False)
    descricao       = Column(String, nullable=True)
    paciente_id     = Column(Integer, ForeignKey("paciente.id"), nullable=False)
    tratamento_id   = Column("tratamento_id", ForeignKey('tratamento.id'), nullable=True)
    diagnostico_id  = Column("diagnostico_id", ForeignKey('diagnostico.id'), nullable=True)
#===========================================================================================

Base.metadata.create_all(bind=db)

#CRUD

paciente = Paciente(cpf="19350048756", nome="Carlos", data_nasc="11/08/2000", email="carlos@gmail.com", telefone="11985647526", sexo="M", enedereço="Rua 9", naturalidade="Brasileiro")
session.add(paciente)
session.commit()

#READ
""" lista_paciente = session.query(Paciente).all()
print(lista_paciente) """
paciente_carlos = session.query(Paciente).filter_by(nome="Carlos").first()
print(paciente_carlos)
print(paciente_carlos.nome)
print(paciente_carlos.cpf)
print(paciente_carlos.sexo)
print(paciente_carlos.naturalidade)
