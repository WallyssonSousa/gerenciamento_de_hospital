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


class Paciente(Base): 
    __tablename__ = 'Paciente'
    
    cpf = Column(String(14), primary_key=True, nullable=False)
    nome_paciente = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    telefone = Column(String(14), nullable=False)
    sexo = Column(String(10), nullable=False)
    endereco = Column(String(50), nullable=False)
    naciolidade = Column(String(15), nullable=False)

    
    #oi
    
