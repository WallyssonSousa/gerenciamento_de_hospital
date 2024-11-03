from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date, Boolean, DateTime
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

    consultas = relationship("Consulta", back_populates="paciente")
    
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

    consultas = relationship("Consulta", back_populates="medico")

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


class Consulta(Base):
    __tablename__ = "consulta"

    id_consulta = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")

    @classmethod
    def agendar_consulta(cls, session, paciente_cpf, medico_crm):

        paciente = session.query(Paciente).filter_by(cpf=paciente_cpf).first() 
        medico = session.query(Medico).filter_by(crm=medico_crm).first() 
        if not paciente: 
            print(f"Paciente com CPF {paciente_cpf} não encontrado!") 
            return None 
        if not medico: 
            print(f"Médico com CRM {medico_crm} não encontrado!") 
            return None

        data_hora_str = input("Informe a data e hora da consulta (AAAA-MM-DD HH:MM): ")
        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
        
        consulta_agendada = cls(
            data_hora = data_hora,
            status=True,
            paciente_cpf=paciente_cpf, 
            medico_crm=medico_crm
        )

        session.add(consulta_agendada)
        session.commit()

        print(f"Consulta agendada com sucesso para o paciente {paciente_cpf}, com o médico {medico_crm}")
    
    @classmethod
    def cancelar_consulta(cls, session, id_consulta):
        consulta = session.query(cls).filter_by(id_consulta=id_consulta).first()
        if consulta: 
            session.delete(consulta)
            session.commit()
            print(f"Consulta com ID {id_consulta} cancelada com sucesso!")
        else:
            print(f"Consulta com ID {id_consulta} não encontrada!")


    @classmethod
    def editar_consulta(cls, session, id_consulta): 
        consulta = session.query(cls).filter_by(id_consulta=id_consulta).first()
        if not consulta:
            print(f"Consulta com ID {id_consulta} não encontrada!")
            return None
        print("Deixe em branco para manter o valor atual")

        data_hora_str = input(f"Informe a nova data e hora da consulta (AAAA-MM-DD HH:MM) [{consulta.data_hora}]: ")
        if data_hora_str:
            consulta.data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
        
        status_str = input(f"Informe o novo status da consulta (True/False) [{consulta.status}]: ")
        if status_str:
            consulta.status = status_str.lower() in ['true', 1]

        session.commit()
        print(f"Consulta com ID {id_consulta} atualizada com sucesso!")


    @classmethod
    def visualizar_consultas_paciente(cls, session, paciente_cpf):
        consultas = session.query(cls).filter_by(paciente_cpf=paciente_cpf).all()
        if consultas:
            print(f"\n Consultas do Paciente com CPF {paciente_cpf}:\n" + "="*50)
            for consulta in consultas:
                medico = session.query(Medico).filter_by(crm=consulta.medico_crm).first()
                print("="*50)
                print(f"ID Consulta: {consulta.id_consulta}")
                print(f"Data e Hora: {consulta.data_hora}")
                print(f"Status: {consulta.status}")
                print(f"Médico: Dr. {medico.nome_medico} (CRM: {medico.crm})")
                print("="*50)

Consulta.cancelar_consulta(
    session=session, 
    id_consulta=int(input("Digite o ID da consulta que quer deletar: "))
)

Consulta.visualizar_consultas_paciente(
    session, 
    paciente_cpf=int(input("Digite o CPF do paciente que deseja ver as consultas: "))
)




# Criar as tabelas no banco de dados
Base.metadata.create_all(db)




