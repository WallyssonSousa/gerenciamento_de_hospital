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
    __tablename__ = "prontuario"
    numero_prontuario = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

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

    """ def set_new_paciente(session):
        while True:
            print('==== NOVO PACIENTE')

            cpf = input('Insira o cpf do paciente: ')
            nome_paciente = input('Informe o nome completo do paciente: ')
            data_nascimento = input('Coloque a data de nascimento do paciente: ')
            telefone = input('Digite o telefone de contato do paciente: ')
            email = input("Insira o email do paciente: ")
            sexo = ("Informe o sexo do paciente: ")
            endereco = ("Insira o endereço do paciente: ")
            nacionalidade = ("Informe a nacionalidade do paciente: ")


#                            ADICIONANDO PACIENTE

            novo_paciente = Paciente(
                cpf=cpf,
                nome_paciente=nome_paciente,
                data_nascimento=data_nascimento,
                email=email,
                telefone=telefone,
                sexo=sexo,
                endereco=endereco,
                nacionalidade=nacionalidade,
            ) """

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



    """
                                        Comentado por não está pronto para uso
                                        Se for utilizar, relacionar com a tabela consulta

        consultas = relationship("Consulta", back_populates="medico")

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
            print("Consulta não encontrada.") """

#=====================================Consulta=================================================

class Consulta(Base):
    __tablename__= "consulta"

    medico      = relationship("Medico", back_populates="consultas")
    paciente    = relationship("Paciente", back_populates="consultas")

    id_consulta = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    paciente = relationship("Paciente")
    medico = relationship("Medico")

    def set_agendar_consulta_paciente(self, session, data_hora, paciente_cpf, medico_crm):
        # Solicitar dados da consulta
        data_hora = input('Insira a data e hora da consulta (AAAA-MM-DD HH:MM): ')

        # Criar um objeto de consulta com status padrão como True (agendada)
        consulta_agendada = Consulta(
            data_hora=data_hora,
            status=True,  # Definindo a consulta como agendada
            paciente_cpf=paciente_cpf,
            medico_crm=medico_crm
        )

        # Adicionar a consulta à sessão e salvar no banco de dados
        session.add(consulta_agendada)
        session.commit()

        print(f"Consulta agendada com sucesso para o paciente {paciente_cpf} com o médico {medico_crm}!")

        return consulta_agendada
    
    def cancelar_consulta(self, consulta_id, session):
        consulta = session.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
        if consulta:
            consulta.status = False  # Alterar o status para False (cancelada)
            session.commit()
            print("Consulta cancelada com sucesso!")
        else:
            print("Consulta não encontrada.")

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

    consulta = relationship("Consulta")
    paciente = relationship("Paciente")
    medico = relationship("Medico")

    def adicionar_ao_prontuario(self, session, paciente): 
        session.add(self)
        session.commit()
        paciente.prontuario = self
        print(f"Diagnóstico adicionado ao prontuário de {paciente.nome_paciente}.")

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

#========================================================================================================






#============================ Login ============================ #

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


""" 
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