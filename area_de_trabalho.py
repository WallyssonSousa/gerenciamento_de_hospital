from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

db = create_engine("sqlite:///sistemasaude.db")
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

class Prontuario(Base):
    __tablename__ = 'prontuario'
    numero_prontuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    diagnosticos = relationship("Diagnostico", back_populates="prontuario")

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
    consultas = relationship("Consulta", back_populates="paciente")
    diagnosticos = relationship("Diagnostico", back_populates="paciente")

class Medico(Base):
    __tablename__ = "medico"
    crm = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome_medico = Column(String(45), nullable=False)
    especialidade = Column(String(25), nullable=False)
    senha = Column(String(8), nullable=False)

    consultas = relationship("Consulta", back_populates="medico")
    diagnosticos = relationship("Diagnostico", back_populates="medico")

class Consulta(Base):
    __tablename__ = "consulta"
    id_consulta = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")
    diagnosticos = relationship("Diagnostico", back_populates="consulta")

class Diagnostico(Base):
    __tablename__ = 'diagnostico'
    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    cid = Column(String(10), nullable=False)
    descricao = Column(Text, nullable=False)
    consulta_id = Column(Integer, ForeignKey('consulta.id_consulta'), nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)
    prontuario_id = Column(Integer, ForeignKey('prontuario.numero_prontuario'), nullable=False)

    consulta = relationship("Consulta", back_populates="diagnosticos")
    paciente = relationship("Paciente", back_populates="diagnosticos")
    medico = relationship("Medico", back_populates="diagnosticos")
    prontuario = relationship("Prontuario", back_populates="diagnosticos")
    tratamentos = relationship("Tratamento", back_populates="diagnostico")

    @classmethod
    def adicionar_diagnostico(cls, session, cid, descricao, consulta_id, paciente_cpf, medico_crm, prontuario_id):
        consulta = session.query(Consulta).filter_by(id_consulta=consulta_id).first()
        paciente = session.query(Paciente).filter_by(cpf=paciente_cpf).first()
        medico = session.query(Medico).filter_by(crm=medico_crm).first()

        if not consulta:
            print(f"Consulta com ID {consulta_id} não encontrada!")
            return None
        if not paciente:
            print(f"Paciente com CPF {paciente_cpf} não encontrado!")
            return None
        if not medico:
            print(f"Médico com CRM {medico_crm} não encontrado!")
            return None

        novo_diagnostico = cls(
            cid=cid,
            descricao=descricao,
            consulta_id=consulta_id,
            paciente_cpf=paciente_cpf,
            medico_crm=medico_crm,
            prontuario_id=prontuario_id
        )
        session.add(novo_diagnostico)
        session.commit()
        return novo_diagnostico


class Tratamento(Base):
    __tablename__ = 'tratamento'
    
    id_tratamento = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao = Column(String(256), nullable=False)
    duracao = Column(String(20), nullable=False)
    medicamentos = Column(String(256), nullable=False)
    diagnostico_id = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=False)

    diagnostico = relationship("Diagnostico", back_populates="tratamentos")

    @classmethod
    def adicionar_tratamento(cls, session, descricao, duracao, medicamentos, diagnostico_id):

        diagnostico = session.query(Diagnostico).filter_by(id_diagnostico=diagnostico_id).first()

        if not diagnostico:
            print(f"Diagnóstico com ID {diagnostico_id} não encontrado!")
            return None

        novo_tratamento = cls(
            descricao=descricao, 
            duracao=duracao, 
            medicamentos=medicamentos,
            diagnostico_id=diagnostico_id
        )
        session.add(novo_tratamento)
        session.commit()
        return novo_tratamento

Base.metadata.create_all(db)

novo_tratamento = Tratamento.adicionar_tratamento(
    session=session,
    descricao="Testando descricao", 
    duracao="1 semana", 
    medicamentos="Remédio pra loucura",
    diagnostico_id=1  
)

if novo_tratamento:
    print(f"Tratamento adicionado: {novo_tratamento.descricao}, tratamento em virtude do diagnostico: {novo_tratamento.diagnostico_id}")
