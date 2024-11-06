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
    consultas = relationship("Consulta", back_populates="paciente")
    diagnosticos = relationship("Diagnostico", back_populates="paciente")


    @classmethod
    def adicionar_paciente(cls, session, cpf, nome, data_nascimento, telefone, sexo, endereco, nacionalidade, senha):
        novo_prontuario = Prontuario()
        session.add(novo_prontuario)
        session.commit()  

        novo_paciente = cls(
            cpf=cpf,
            numero_prontuario=novo_prontuario.numero_prontuario,  # Acessando o atributo numero_prontuario corretamente
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


    def visualizar_consulta(self, session): 
        consultas = session.query(Consulta).filter(Consulta.paciente_cpf == self.cpf).all()
        return [consulta.visualizar_consulta(session) for consulta in consultas]

    def cancelar_consulta(self, consulta_id, session):
        consulta = session.query(Consulta).filter(Consulta.id_consulta == consulta_id, Consulta.paciente_cpf == self.cpf).first()
        if consulta: 
            consulta.cancelar_consulta_agendada(session)
        else: 
            print("Consulta não encontrada ou não pertece a este paciente")  

class Medico(Base):
    __tablename__ = "medico"

    crm = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nome_medico = Column(String(45), nullable=False)
    especialidade = Column(String(25), nullable=False)
    senha = Column(String(8), nullable=False)

    consultas = relationship("Consulta", back_populates="medico")
    diagnosticos = relationship("Diagnostico", back_populates="medico")

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
    receitas = relationship("Receita", back_populates="diagnoticos")

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
    receitas = relationship("Receita", back_populates="tratamentos")

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

class Receita(Base):
    __tablename__ = 'receita'

    id_receita = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descricao = Column(String(256), nullable=False)
    data_receita = Column(Date, nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    paciente_nome = Column(String(45), ForeignKey('paciente.nome_paciente'))
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)
    medico_nome = Column(String(45), ForeignKey('medico.nome_medico'), nullable=False)
    diagnostico_id = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=True)
    tratamento_id = Column(Integer, ForeignKey('tratamento.id_tratamento'), nullable=True)

    paciente = relationship("Paciente", back_populates="receitas")
    medico = relationship("Medico", back_populates="receitas")
    diagnostico = relationship("Diagnostico", back_populates="receitas")
    tratamento = relationship("Tratamento", back_populates="receitas")

    @classmethod
    def adicionar_receita(cls, session, descricao, paciente_cpf, paciente_nome,
                         medico_crm, medico_nome, diagnostico_id, tratamento_id): 
        
        paciente = session.query(Paciente).filter_by(cpf=paciente_cpf).first()
        medico = session.query(Medico).filter_by(crm=medico_crm).first()

        if not paciente:
            print(f"Paciente com CPF {paciente_cpf} não encontrado!")
        if not medico:
            print(f"Medico com CRM {medico_crm} não encontrado!")

        data_str = input("Informe a data da receita (AAAA-MM-DD): ")
        data = Date.strptime(data_str, '%Y-%m-%d')

        adicionar_receita = cls(
            descricao=descricao,
            data=data,
            paciente_cpf=paciente_cpf,
            paciente_nome=paciente_nome,
            medico_crm=medico_crm,
            medico_nome=medico_nome,
            diagnostico_id=diagnostico_id,
            tratamento_id=tratamento_id
        )
        session.add(adicionar_receita)
        session.commit()
        return adicionar_receita

Base.metadata.create_all(db)

nova_receita = Receita.adicionar_receita(
    session=session,
    descricao="Testando descricao", 
    paciente_cpf=input("Digite o cpf do paciente: "), 
    paciente_nome=input("Digite o nome do paciente: "),
    medico_crm=int(input("Digite o crm do médico: ")),
    medico_nome=input("Digite o nome do médico: "),
    diagnostico_id=int(input("Digite o id do diagnostico: ")),
    tratamento_id=int(input("Digite o id do tratamento: "))
)

if nova_receita:
    print(f"Receita adicionada para o paciente {nova_receita.paciente_nome}, pelo Dr(a) {nova_receita.medico_nome}")




