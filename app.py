from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import bcrypt 

db = create_engine("sqlite:///bancoteste.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()


class Usuario(Base): 
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    senha_hash = Column(String(60), nullable=False)

    @staticmethod
    def hash_senha(senha):
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verificar_senha(senha, senha_hash): 
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))


def login_paciente(cpf, senha, session):
    paciente = session.query(Paciente).filter(Paciente.cpf == cpf).first()
    if paciente and Usuario.verificar_senha(senha, paciente.senha_hash): 
        print(f"Bem vindo, {paciente.nome_paciente}")
        return paciente
    else:
        print("CPF ou senha inválidos")
        return None
    
def login_medico(crm, senha, session):
    medico = session.query(Medico).filter(Medico.crm == crm).first()
    if medico and Usuario.verificar_senha(senha, medico.senha_hash):
        print(f"Bem vindo, Dr(a). {medico.nome_medico}")
        return medico
    else: 
        print("CRM ou senha inválidos.")
        return None


# Tabelas
#===================================================================================================

class Prontuario(Base):
    __tablename__ = "prontuario"
    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)

#=================================================================================================
class Paciente(Base): 
    __tablename__ = 'paciente'

    consultas = relationship("Consulta", back_populates="paciente")
    
    cpf = Column(String(14), primary_key=True, nullable=False)
    numero_prontuario_id = Column(Integer, ForeignKey('prontuario.numero_prontuario'), nullable=False)
    nome_paciente = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    telefone = Column(String(14), nullable=False)
    sexo = Column(String(10), nullable=False)
    endereco = Column(String(50), nullable=False)
    nacionalidade = Column(String(15), nullable=False) 

    prontuario = relationship("Prontuario")

    def visualizar_consulta(self, session): 
        consultas = session.query(Consulta).filter(Consulta.paciente_cpf == self.cpf).all()
        return [consulta.visualizar_consulta(session) for consulta in consultas]

    def cancelar_consulta(self, consulta_id, session):
        consulta = session.query(Consulta).filter(Consulta.id_consulta == consulta_id, Consulta.paciente_cpf == self.cpf).first()
        if consulta: 
            consulta.cancelar_consulta_agendada(session)
        else: 
            print("Consulta não encontrada ou não pertece a este paciente")
#================================================================================================

class Medico(Base):
    __tablename__ = "medico"

    consultas = relationship("Consulta", back_populates="medico")

    crm = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome_medico = Column(String(45), nullable=False)
    especialidade = Column(String(25), nullable=False)


    def visualizr_consultas(self, session): 
        consultas = session.query(Consulta).filter(Consulta.medico_crm == self.crm).all()
        return [consulta.visualizar_consulta(session) for consulta in consultas]
    
    def editar_consulta(self, consulta_id, novos_dados, session):
        consulta = session.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
        if consulta: 
            for key, value in novos_dados.items():
                setattr(consulta, key, value)
            session.commit()
        else: 
            print("Consulta não encontrada.")

    def cancelar_consulta(self, consulta_id, session):
        consulta = session.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
        if consulta: 
            consulta.cancelar_consulta_agendada(session)
        else:
            print("Consulta não encontrada.")

#================================================================================================

class Consulta(Base):
    __tablename__= "consulta"

    medico      = relationship("Medico", back_populates="consultas")
    paciente    = relationship("Paciente", back_populates="consultas")

    id_consulta = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(String(45), nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    paciente = relationship("Paciente")
    medico = relationship("Medico")

    def agendar_consulta_paciente(self, session, paciente_cpf, medico_crm, data_hora, status="Agendada"):
        consulta_agendada = Consulta(
            data_hora = data_hora,
            status = status,
            paciente_cpf = paciente_cpf,
            medico_crm = medico_crm
        )
        
        session.add(consulta_agendada)
        session.commit()

        return consulta_agendada
    
    def visualizar_consulta(self, session, consulta_id=None, paciente_cpf=None, medico_crm=None):
        query = session.query(Consulta)

        if consulta_id:
            query = query.filter(Consulta.id_consulta == consulta_id)
        elif paciente_cpf:
            query = query.filter(Consulta.paciente_cpf == paciente_cpf)
        elif medico_crm:
            query = query.filter(Consulta.medico_crm == medico_crm)

        consulta_buscada = query.first()

        if consulta_buscada:
            return consulta_buscada
        else:
            print("Consulta não encontrada!")

    def cancelar_consulta_agendada(self, session):
        if self.status.lower() == "Cancelada":
            print("A consulta já está cancelada")
            return
        
        self.status = "Cancelada"

        session.add(self)
        session.commit()

#================================================================================================

class Diagnostico(Base):
    __tablename__ = "diagnostico"

    consulta = relationship("Consulta", back_populates="diagnosticos")

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(7), nullable=False)
    descricao = Column(String(256), nullable=False)
    consulta_id = Column(Integer, ForeignKey('consulta.id_consulta'), nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    consulta = relationship("Consulta")
    paciente = relationship("Paciente")
    medico = relationship("Medico")

    def adicionar_ao_prontuario(self, session, paciente): 
        session.add(self)
        session.commit()
        paciente.prontuario = self
        print(f"Diagnóstico adicionado ao prontuário de {paciente.nome_paciente}.")

#================================================================================================

class Tratamento(Base):
    __tablename__ = "tratamento"

    id_tratamento = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao = Column(String(100), nullable=False)
    duracao = Column(String(20), nullable=False)
    medicamentos = Column(String(256), nullable=False)
    diagnostico_id = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=False)

    diagnostico = relationship("Diagnostico")
    
    def adicionar_ao_prontuario(self, session, paciente):
        session.add(self)
        session.commit()
        print(f"Tratamento adicionado ao prontuário de {paciente.nome_paciente}.")

#================================================================================================

class Receita(Base):
    __tablename__ = "receita"

    id_receita = Column(Integer, primary_key=True, autoincrement=True)
    crm_medico = Column(Integer, ForeignKey('medico.crm'), nullable=False)
    nome_medico = Column(String(45), ForeignKey('medico.nome_medico'), nullable=False)
    cpf_paciente = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    nome_paciente = Column(String(45), ForeignKey('paciente.nome_paciente'), nullable=False)
    id_diagnostico = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=True)
    id_tratamento = Column(Integer, ForeignKey('tratamento.id_tratamento'), nullable=True)
    descricao = Column(String(256), nullable=False)

    def adicionar_ao_prontuario(self, session, paciente):
        session.add(self)
        session.commit()
        print(f"Receita adicionado ao prontuário de {paciente.nome_paciente}.")

#================================================================================================
    
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
