from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
url_database = "sqlite:///gerenciador_hospital.db"


Base = declarative_base()

""" teu cu é meus """
engine = create_engine(url_database, echo=True)

class Prontuario(Base):
    __tabelename__ = 'Prontuario'

    numero_prontuario = Column(Integer, primary_key=True, nullable=False)

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

    
    