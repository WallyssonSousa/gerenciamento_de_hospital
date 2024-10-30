from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

db = create_engine("sqlite:///bancoteste.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

#Tabelas

#============================PROONTUARIO==============================================
class Prontuario(Base):
    __tablename__ = "prontuario"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
#======================================================================================


#==============================PACIENTES===============================================
class Paciente(Base):
    __tablename__ = "paciente"

    id           = Column("id", Integer, primary_key=True, autoincrement=True)
    cpf          = Column()
    nome         = Column()
    data_nasc    = Column()
    email        = Column()
    telefone     = Column()
    sexo         = Column()
    endereço     = Column()
    naturalidade = Column()
    prontuario   = Column()

#======================================================================================

#======================================MEDICOS=========================================
class Medico(Base):
    __tablename__ = "medico"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    crm             = Column()
    nome            = Column()
    especialidade   = Column()

#=======================================================================================

#====================================CONSULTA===========================================
class Consulta(Base):
    __tablename__= "consulta"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    data_hora       = Column()
    status          = Column()
    paciente_cpf    = Column()
    medico_crm      = Column()

#====================================DIAGNOSTICO=========================================
class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    cid             = Column()
    descrição       = Column()
    consulta_id     = Column()
    paciente_cpf    = Column()
    medico_crm      = Column()
#==========================================================================================

#=====================================TRATAMENTO============================================
class Tratamento(Base):
    __tablename__ = "tratamento"

    id              = Column("id", Integer, primary_key=True, autoincrement=True)
    descrição       = Column()
    duração         = Column()
    medicamentos    = Column()
    diagnostico     = Column()
#=========================================================================================

#=====================================RECEITA=============================================
class Receita(Base):
    __tabelname__ = "receita"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome_medico
#========================================================================================
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
