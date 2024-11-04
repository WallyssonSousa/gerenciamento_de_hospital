from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import menu_medico
import menu_paciente

db = create_engine("sqlite:///sistemasaude.db")   
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()


# Tabelas
#===================================Prontuario====================================================

class Prontuario(Base):
    __tablename__ = 'prontuario'
    numero_prontuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    diagnosticos = relationship("Diagnostico", back_populates="prontuario")

#===================================Paciente===============================================

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

#============================ Médico ============================ #
            
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




#=====================================Consulta=================================================

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

        print(f"Consulta agendada com sucesso para o paciente {paciente_cpf} \n Com o médico {medico_crm}")

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


#===================================Diagnostico====================================================

class Diagnostico(Base):
    __tablename__ = "diagnostico"

    consulta = relationship("Consulta", back_populates="diagnosticos")

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(7), nullable=False)
    descricao = Column(String(256), nullable=False)
    consulta_id = Column(Integer, ForeignKey('consulta.id_consulta'), nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    consulta = relationship("Consulta", back_populates="diagnosticos")
    paciente = relationship("Paciente", back_populates="diagnosticos")
    medico = relationship("Medico", back_populates="diagnosticos")
    prontuario = relationship("Prontuario", back_populates="diagnosticos")

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

#===================================Tratamento=================================================

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

#====================================Receita=================================================

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


#=========================================== Metódos e Adicionando a tabela ================================
    
Base.metadata.create_all(bind=db)

#============================ Chamando o meth e adicionando paciente ============================ #

# Agora, testando a adição de um novo paciente
novo_paciente = Paciente.adicionar_paciente(
    session=session,
    cpf='42276413901',
    nome='Antonio Arthur',
    data_nascimento=datetime(2005, 5, 17).date(),  # Converte para objeto date
    telefone='11999999999',
    sexo='Masculino',
    endereco='Rua Exemplo, 123',
    nacionalidade='Brasileiro',
    senha='42276'
)

print(f"Paciente {novo_paciente.nome_paciente} adicionado com prontuário número {novo_paciente.numero_prontuario}.")

# Adicionar o paciente ao banco de dados
session.add(novo_paciente)
session.commit()
print("Paciente adicionado com sucesso!")


#============================ Chamando o meth e adicionando médico ============================ #

novo_medico = Medico.adicionar_medico(
    session=session,
    crm='21232', 
    nome_medico='Pedro',
    especialidade='Clinico Geral',  
    senha='21232'
)

print(f"Dr(a) {novo_medico.nome_medico} adicionado com sucesso! {novo_medico.crm}")
session.add(novo_medico)
session.commit()
print("Dr(a) adicionado com sucesso!")

#========================================================================================================

Medico.visualizar_todos_pacientes(session)

#============================= Testando metodos de consulta=========================================

Consulta.agendar_consulta(
    session, 
    paciente_cpf=input("Digite o CPF do paciente: "),
    medico_crm=input("Digite o CRM do médico: ")
)

Consulta.cancelar_consulta(
    session=session, 
    id_consulta=int(input("Digite o ID da consulta que quer deletar: "))
)

Consulta.editar_consulta(
    session,
    id_consulta=int(input("Digite o ID da consulta que deseja editar: "))
)

Consulta.visualizar_consultas_paciente(
    session, 
    paciente_cpf=int(input("Digite o CPF do paciente que deseja ver as consultas: "))
)

#================================ Adicionando Diagnostico ======================================

novo_diagnostico = Diagnostico.adicionar_diagnostico(
    session=session,  
    cid="F32.0",
    descricao="Episódio depressivo leve",
    consulta_id=1,
    paciente_cpf="42276413901",
    medico_crm=21232,
    prontuario_id=1
)

if novo_diagnostico:
    print(f"Diagnóstico adicionado: {novo_diagnostico.cid} - {novo_diagnostico.descricao}")

#===================================================== Login ======================================================================= #

def login(cpf=None, crm=None, senha=None, user_type=None): 
    if user_type == '1':
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
            print("Usuario não encontrado!")
    elif user_type == '2':
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
            print("Usuario não encontrado!")
    
def escolha_usuario():
    print("\n==================== Deseja fazer login como: ======================")
    print("1. 👤 Paciente")
    print("2. 🧑‍⚕️ Medico")
    print("3. 🚪 Sair")
    print("=======================================================")
    opcao = input("Escolha uma opção: ")
    return opcao

usuario_tipo = escolha_usuario()
cpf = None
crm = None
if usuario_tipo == '1':
    cpf = input("Digite seu CPF: ")
elif usuario_tipo == '2':
    crm = input("Digite seu CRM: ")
senha = input("Digite sua senha: ")

login(cpf=cpf, crm=crm, senha=senha, user_type=usuario_tipo) 

