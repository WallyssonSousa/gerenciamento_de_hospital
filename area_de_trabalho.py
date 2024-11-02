from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import menu_medico
import menu_paciente

db = create_engine("sqlite:///sistemasaude.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

class Prontuario(Base):
    __tablename__ = 'prontuario'
    numero_prontuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

class Paciente(Base):
    __tablename__ = 'paciente'
    
    cpf = Column(String(14), primary_key=True, nullable=False)
    numero_prontuario = Column(Integer, ForeignKey('prontuario.numero_prontuario'), nullable=False)
    nome_paciente = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(14), nullable=False)
    sexo = Column(String(10), nullable=False)
    endereco = Column(String(50), nullable=False)
    nacionalidade = Column(String(15), nullable=False)
    senha = Column(String(8), nullable=False)

    prontuario = relationship("Prontuario")

    @classmethod
    def adicionar_paciente(cls, session, cpf, nome, data_nascimento, telefone, sexo, endereco, nacionalidade, senha):
        novo_prontuario = Prontuario()
        session.add(novo_prontuario)
        session.commit()

        novo_paciente = cls(
            cpf=cpf,
            numero_prontuario=novo_prontuario.numero_prontuario,
            nome_paciente=nome,
            data_nascimento=data_nascimento,
            telefone=telefone,
            sexo=sexo,
            endereco=endereco,
            nacionalidade=nacionalidade,
            senha=senha
        )
        session.add(novo_paciente)
        session.commit()
        return novo_paciente

class Medico(Base):
    __tablename__ = "medico"

    crm = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome_medico = Column(String(45), nullable=False)
    especialidade = Column(String(25), nullable=False)
    senha = Column(String(8), nullable=False)

    @classmethod
    def adicionar_medico(cls, session, crm, nome_medico, especialidade, senha):
        novo_medico = cls(
            crm=crm,
            nome_medico=nome_medico,
            especialidade=especialidade,
            senha=senha
        )
        session.add(novo_medico)
        session.commit()
        return novo_medico

    @classmethod
    def visualizar_todos_pacientes(cls, session):
        pacientes = session.query(Paciente).all()
        print("\n Relatório  de Pacientes \n" + "="*50)
        for paciente in pacientes:
            print(f"Nome: {paciente.nome_paciente}")
            print(f"CPF: {paciente.cpf}")
            print(f"Data de Nascimento: {paciente.data_nascimento}")
            print(f"Telefone: {paciente.telefone}")
            print(f"Sexo: {paciente.sexo}")
            print(f"Endereço: {paciente.endereco}")
            print(f"Nacionalidade: {paciente.nacionalidade}")
            print("="*50)
            

    

# Criar as tabelas no banco de dados
Base.metadata.create_all(db)

def login(cpf=None, crm=None, senha=None, user_type=None): 
    if user_type == 'paciente':
        usuario = session.query(Paciente).filter_by(cpf=cpf, senha=senha).first()
        if usuario:
            print(f"Login bem-sucedido como {user_type}, bem-vindo {usuario.nome_paciente}")
            opcao = menu_paciente.menu_paciente()
            while opcao != '3':
                if opcao == '1':
                    print("Visualizar")

                elif opcao == '2':
                    print("Cancelar")
                else:
                    print("Opção inválida. Tente novamente.")
                opcao = menu_paciente.menu_paciente()
        else:
            return "Usuario não encontrado!"
    elif user_type == 'medico':
        usuario = session.query(Medico).filter_by(crm=crm, senha=senha).first()
        if usuario:
            print(f"Login bem-sucedido como {user_type}, bem-vindo {usuario.nome_medico}")
            opcao = menu_medico.menu_medico()
            while opcao != '4':
                if opcao == '1':
                    print("Visualizando consultas...")
                    
                elif opcao == '2':
                    print("Adicionando consulta...")
                    
                elif opcao == '3':
                    print("Visualizando pacientes...")
                    Medico.visualizar_todos_pacientes(session)
                else:
                    print("Opção inválida. Tente novamente.")
                opcao = menu_medico.menu_medico()
        else:
            return "Usuario não encontrado!"

usuario_tipo = input("Você está logando como 'paciente' ou 'medico'? ")
cpf = None
crm = None
if usuario_tipo == 'paciente':
    cpf = input("Digite seu CPF: ")
elif usuario_tipo == 'medico':
    crm = input("Digite seu CRM: ")
senha = input("Digite sua senha: ")

login(cpf=cpf, crm=crm, senha=senha, user_type=usuario_tipo)
