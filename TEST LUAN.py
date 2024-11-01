from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import bcrypt 
from datetime import datetime

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
    numero_prontuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

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


    def visualizar_consulta(self, session): 
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

        consulta_buscada = query.all()#mudado - estava "consulta_buscada = query.first()"

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

    def exibir_receita_Paciente(self):
        print(f'{self.id_receita} ----- ID DA RECEITA')
        print(f'{self.nome_medico} ----- NOME DO MEDICO')
        print(f'{self.crm_medico} ----- CRM DO MEDICO')
        print(f'{self.nome_paciente} ----- NOME DO PACIENTE')
        print(f'{self.cpf_paciente} ----- CPF DO PACIENTE')
        print(f'{self.descricao} ----- DESCRIÇÃO DA RECEITA')

    def adicionar_ao_prontuario(self, session, paciente):
        session.add(self)
        session.commit()
        print(f"Receita adicionado ao prontuário de {paciente.nome_paciente}.")

#================================================================================================
    
Base.metadata.create_all(bind=db)





# Criar um novo paciente
novo_paciente = Paciente(
    cpf="12345678900",
    numero_prontuario_id=1,  # Assumindo que já existe um prontuário com ID 1
    nome_paciente="João Silva",
    data_nascimento=datetime(1990, 1, 1),  # Data de nascimento
    email="joao.silva@example.com",
    telefone="123456789",
    sexo="Masculino",
    endereco="Rua Exemplo, 123",
    nacionalidade="Brasileiro"
)

# Adicionar o paciente ao banco de dados
session.add(novo_paciente)
session.commit()
print("Paciente adicionado com sucesso!")

paciente_buscado = session.query(Paciente).filter(Paciente.cpf == "12345678900").first()

if paciente_buscado:
    print(f"Nome: {paciente_buscado.nome_paciente}")
    print(f"CPF: {paciente_buscado.cpf}")
    print(f"Data de Nascimento: {paciente_buscado.data_nascimento}")
    print(f"E-mail: {paciente_buscado.email}")
    print(f"Telefone: {paciente_buscado.telefone}")
    print(f"Sexo: {paciente_buscado.sexo}")
    print(f"Endereço: {paciente_buscado.endereco}")
    print(f"Nacionalidade: {paciente_buscado.nacionalidade}")
else:
    print("Paciente não encontrado.")












""" 
# Adicionando um usuário
nova_senha = Usuario.hash_senha("senha_do_usuario")
usuario = Usuario(senha_hash=nova_senha)
session.add(usuario)
session.commit()
print("Usuário adicionado com sucesso.")

# Adicionando um paciente
paciente = Paciente(
    cpf="12345678901",
    numero_prontuario_id=1,
    nome_paciente="João Silva",
    data_nascimento="1990-01-01",
    email="joao@example.com",
    telefone="123456789",
    sexo="Masculino",
    endereco="Rua A, 123",
    nacionalidade="Brasileiro"
)
session.add(paciente)
session.commit()
print("Paciente adicionado com sucesso.")

# Adicionando um médico
medico = Medico(
    crm=123456,
    nome_medico="Dr. Carlos",
    especialidade="Cardiologia"
)
session.add(medico)
session.commit()
print("Médico adicionado com sucesso.")

# Testando login do paciente
cpf = "12345678901"
senha = "senha_do_usuario"  # A senha deve ser a mesma usada para o hash
paciente_login = login_paciente(cpf, senha, session)
if paciente_login:
    print(f"Login bem-sucedido para {paciente_login.nome_paciente}.")
else:
    print("Login falhou.")

# Agendando uma consulta
data_hora = "2024-10-30 10:00:00"
consulta = Consulta()
consulta.agendar_consulta_paciente(session, "12345678901", 123456, data_hora)
print("Consulta agendada com sucesso.")

# Visualizando consultas do paciente
consultas = paciente.visualizar_consulta(session)
for consulta in consultas:
    print(f"Consulta ID: {consulta.id_consulta}, Data: {consulta.data_hora}, Status: {consulta.status}")

# Cancelando uma consulta
consulta_id = 1  # Supondo que a consulta ID 1 exista
paciente.cancelar_consulta(consulta_id, session)
print("Consulta cancelada com sucesso.")

# Fechar a sessão
session.close() """