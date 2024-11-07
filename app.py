import os
from sqlalchemy import create_engine, DateTime, Column, String, Integer, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import menu_medico
import menu_paciente

# Criando a conexão com o banco de dados
db = create_engine("sqlite:///sistemasaude.db")   
Session = sessionmaker(bind=db)
session = Session()

# Definição da base para o ORM
Base = declarative_base()

# ================================= Prontuário ========================================================== #

class Prontuario(Base):
    __tablename__ = 'prontuario'

    id_prontuario = Column(Integer, primary_key=True, autoincrement=True)
    cpf_paciente = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)

    paciente = relationship("Paciente", back_populates="prontuarios")

    @classmethod
    def associar_paciente(cls, session, cpf_paciente): 
        paciente = session.query(Paciente).filter_by(cpf=cpf_paciente).first()
        if not paciente:
            print(f"Paciente com CPF {cpf_paciente} não encontrado!")
            return None
        
        prontuario = cls(cpf_paciente=cpf_paciente)
        session.add(prontuario)
        session.commit()

        print(f"Prontuario associado com sucesso ao Paciente {paciente.nome_paciente} (CPF: {paciente.cpf} )")
        return prontuario
    
    @classmethod
    def exibir_informacoes(cls, session, cpf_paciente):
        prontuario = session.query(cls).filter_by(cpf_paciente=cpf_paciente).first()
        if not prontuario:
            print(f"Nenhum prontuário encontrado para o paciente com CPF {cpf_paciente}")
            return
        
        paciente = session.query(Paciente).filter_by(cpf=cpf_paciente).first()

        print(f"\nInformações do Prontuário - {paciente.nome_paciente} (CPF: {paciente.cpf})")
        print("="*50)
        print(f"Nome do Paciente: {paciente.nome_paciente}")
        print(f"Data de Nascimento: {paciente.data_nascimento}")
        print(f"Telefone: {paciente.telefone}")
        print(f"Sexo: {paciente.sexo}")
        print(f"Endereço: {paciente.endereco}")
        print("="*50)

        Consulta.visualizar_consultas_paciente(session, paciente_cpf=cpf_paciente)

        tratamentos = session.query(Tratamento).join(Diagnostico).filter(Diagnostico.paciente_cpf == cpf_paciente).all()

        if tratamentos:
            print("\nTratamentos do Paciente:")
            for tratamento in tratamentos:
                print("="*50)
                print(f"ID Tratamento: {tratamento.id_tratamento}")
                print(f"Descrição: {tratamento.descricao}")
                print(f"Duracao: {tratamento.duracao}")
                print(f"Medicamentos: {tratamento.medicamentos}")
                print("="*50)
        else:
            print(f"Nenhum tratamento encontrado para o paciente com CPF {cpf_paciente}.")


        Receita.visualizar_receitas_paciente(session, paciente_cpf=cpf_paciente)


# ================================= Paciente ========================================================== #
class Paciente(Base):
    __tablename__ = 'paciente'

    cpf = Column(String(14), primary_key=True, nullable=False)
    nome_paciente = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=True)
    telefone = Column(String(14), nullable=False)
    sexo = Column(String(10), nullable=True)
    endereco = Column(String(50), nullable=False)
    nacionalidade = Column(String(15), nullable=False)
    senha = Column(String(8), nullable=False)

    consultas = relationship("Consulta", back_populates="paciente")
    diagnosticos = relationship("Diagnostico", back_populates="paciente")
    receitas = relationship("Receita", back_populates="paciente")
    prontuarios = relationship("Prontuario", back_populates="paciente")

    @classmethod
    def adicionar_paciente(cls, session, cpf, nome, data_nascimento, telefone, sexo, endereco, nacionalidade, senha):
        novo_paciente = cls(
            cpf=cpf, 
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
    
    @classmethod
    def visualizar_consultas(cls, session, paciente_cpf):
        
        consultas = session.query(Consulta).filter_by(paciente_cpf=paciente_cpf).all()

        if consultas:
            print(f"\nConsultas do Paciente com CPF {paciente_cpf}:\n" + "="*50)
            for consulta in consultas:
                
                medico = session.query(Medico).filter_by(crm=consulta.medico_crm).first()
                print("="*50)
                print(f"ID Consulta: {consulta.id_consulta}")
                print(f"Data e Hora: {consulta.data_hora}")
                print(f"Status: {'Ativa' if consulta.status else 'Cancelada'}")
                print(f"Médico: Dr. {medico.nome_medico} (CRM: {medico.crm})")
                print("="*50)
        else:
            print(f"Nenhuma consulta encontrada para o paciente com CPF {paciente_cpf}.")

    @classmethod
    def cancelar_consulta(cls, session, paciente_cpf, id_consulta):
        
        consulta = session.query(Consulta).filter_by(id_consulta=id_consulta, paciente_cpf=paciente_cpf).first()

        if consulta:
            if consulta.status:  
                consulta.status = False  
                session.commit()
                print(f"Consulta com ID {id_consulta} foi cancelada com sucesso!")
            else:
                print(f"Consulta com ID {id_consulta} já foi cancelada!")
        else:
            print(f"Consulta com ID {id_consulta} não encontrada ou não pertence ao paciente com CPF {paciente_cpf}.")

# ================================= Medico ========================================================== #
class Medico(Base):
    __tablename__ = 'medico'

    crm = Column(Integer, primary_key=True, nullable=False)
    nome_medico = Column(String(45), nullable=False)
    especialidade = Column(String(25), nullable=False)
    senha = Column(String(8), nullable=False)

    consultas = relationship("Consulta", back_populates="medico")
    diagnosticos = relationship("Diagnostico", back_populates="medico")
    receitas = relationship("Receita", back_populates="medico")

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
    def visualizar_todos_paciente(cls, session):
        pacientes = session.query(Paciente).all()
        print("\n  Relatório de Pacientes \n" + "="*50)
        for paciente in pacientes:
            print(f"Nome: {paciente.nome_paciente}")
            print(f"CPF: {paciente.cpf}")
            print(f"Data de Nascimento: {paciente.data_nascimento}")
            print(f"Telefone: {paciente.telefone}")
            print(f"Sexo: {paciente.sexo}")
            print(f"Endereço: {paciente.endereco}")
            print(f"Nacionalidade: {paciente.nacionalidade}")
            print("="*50)

# ================================= Consulta ========================================================== #
class Consulta(Base):
    __tablename__ = 'consulta'

    id_consulta = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    
    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")
    diagnostico = relationship("Diagnostico", back_populates="consulta", uselist=False)

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

        print(f"Consulta agendada com sucesso para o paciente {paciente_cpf}, com o DR(A): {medico_crm}")

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

# ================================= Diagnostico ========================================================== #
class Diagnostico(Base):
    __tablename__ = 'diagnostico'

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(7), nullable=False)
    descricao = Column(String(256), nullable=False)
    consulta_id = Column(Integer, ForeignKey('consulta.id_consulta'), nullable=False)
    paciente_cpf = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    medico_crm = Column(Integer, ForeignKey('medico.crm'), nullable=False)

    consulta = relationship("Consulta", back_populates="diagnostico")
    paciente = relationship("Paciente", back_populates="diagnosticos")
    medico = relationship("Medico", back_populates="diagnosticos")
    tratamentos = relationship("Tratamento", back_populates="diagnostico")
    receitas = relationship("Receita", back_populates="diagnostico")

    @classmethod
    def adicionar_diagnostico(cls, session, cid, descricao, consulta_id, paciente_cpf, medico_crm):
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
            medico_crm=medico_crm
        )
        session.add(novo_diagnostico)
        session.commit()
        return novo_diagnostico
    
# ================================= Tratamento ========================================================== #

class Tratamento(Base):
    __tablename__ = 'tratamento'

    id_tratamento = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(256), nullable=False)
    duracao = Column(String(20), nullable=False)
    medicamentos = Column(String(256), nullable=False)
    diagnostico_id = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=False)

    diagnostico = relationship("Diagnostico", back_populates="tratamentos")
    receitas = relationship("Receita", back_populates="tratamento")

    @classmethod
    def adicionar_tratamento(cls, session, descricao, duracao, medicamentos, diagnostico_id):

        diagnostico = session.query(Diagnostico).filter_by(id_diagnostico=diagnostico_id).first()

        if not diagnostico:
            print(f'Diagnóstico com ID {diagnostico_id} não encontrado!')
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

    id_receita = Column(Integer, primary_key=True, autoincrement=True)
    crm_medico = Column(Integer, ForeignKey('medico.crm'), nullable=False)
    nome_medico = Column(String(45), nullable=False)  
    cpf_paciente = Column(String(14), ForeignKey('paciente.cpf'), nullable=False)
    nome_paciente = Column(String(45), nullable=False) 
    id_diagnostico = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=False)
    id_tratamento = Column(Integer, ForeignKey('tratamento.id_tratamento'), nullable=False)
    descricao = Column(String(256), nullable=False)
    data_receita = Column(Date, nullable=True)

    paciente = relationship("Paciente", back_populates="receitas")
    medico = relationship("Medico", back_populates="receitas")
    diagnostico = relationship("Diagnostico", back_populates="receitas")
    tratamento = relationship("Tratamento", back_populates="receitas")

    @classmethod
    def adicionar_receita(cls, session, crm_medico, nome_medico, cpf_paciente, nome_paciente, id_diagnostico, id_tratamento, descricao, data_receita): 
        
        paciente = session.query(Paciente).filter_by(cpf=cpf_paciente).first()
        medico = session.query(Medico).filter_by(crm=crm_medico).first()

        if not paciente: 
            print(f"Paciente com CPF: {cpf_paciente} não encontrado!")
            return None
        if not medico: 
            print(f"Médico com o CRM: {crm_medico} não encontrado!")

        nova_receita = cls(
            crm_medico=crm_medico, 
            nome_medico=nome_medico,
            cpf_paciente=cpf_paciente,
            nome_paciente=nome_paciente,
            id_diagnostico=id_diagnostico,
            id_tratamento=id_tratamento,
            descricao=descricao,
            data_receita=data_receita
        )

        session.add(nova_receita)
        session.commit()
        return nova_receita
    

    @classmethod
    def visualizar_receitas_paciente(cls, session, paciente_cpf):
        # Usando o filtro corretamente
        receitas = session.query(cls).filter_by(cpf_paciente=paciente_cpf).all()
        
        if receitas: 
            for receita in receitas:
                # Buscando as informações relacionadas
                medico = session.query(Medico).filter_by(crm=receita.crm_medico).first()
                paciente = session.query(Paciente).filter_by(cpf=receita.cpf_paciente).first()
                
                # Exibindo os dados da receita
                print("="*50)
                print(f"CRM médico: {medico.crm}")
                print(f"DR(A): {medico.nome_medico}")
                print(f"CPF do Paciente: {paciente.cpf}")
                print(f"Nome do Paciente: {paciente.nome_paciente}")
                print(f"ID do Diagnóstico: {receita.id_diagnostico}")
                print(f"ID do Tratamento: {receita.id_tratamento}")
                print(f"Descrição da Receita: {receita.descricao}")
                print(f"Data da Receita: {receita.data_receita}")
                print("="*50)
        else:
            print(f"Nenhuma receita encontrada para o paciente com CPF {paciente_cpf}.")



# Criando as tabelas no banco de dados
Base.metadata.create_all(db)

# Inserção de Dados


""" novo_medico = Medico.adicionar_medico(
    session=session,
    crm=21232, 
    nome_medico='Pedro',
    especialidade='Cirurgia geral',
    senha='21232'
)
print(f"DR(A): {novo_medico.nome_medico} do CRM: {novo_medico.crm} adicionado com sucesso!")  """

#===================================================== Login ======================================================================= #

def login(cpf=None, crm=None, senha=None, user_type=None): 
    if user_type == '1':
        usuario = session.query(Paciente).filter_by(cpf=cpf, senha=senha).first()
        if usuario:
            print(f"Login bem-sucedido como {user_type}, bem-vindo {usuario.nome_paciente}")
            opcao = menu_paciente.menu_paciente()
            while opcao != '4':
                if opcao == '1':
                    Paciente.visualizar_consultas(session, paciente_cpf=input("Digite seu CPF para visualizar suas consultas: "))
                elif opcao == '2':
                    Paciente.cancelar_consulta(session, paciente_cpf=input("Digite seu CPF: "), id_consulta=input("Digite o ID da consulta: "))
                elif opcao == '3':
                    Receita.visualizar_receitas_paciente(session, paciente_cpf=input("Digite seu CPF: "))
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
            while opcao != '13':
                if opcao == '1':
                    Consulta.visualizar_consultas_paciente(
                        session, 
                        paciente_cpf=input("Digite o CPF do paciente que deseja ver as consultas: ")
                    )
                elif opcao == '2':
                    Consulta.agendar_consulta(session, paciente_cpf='42276413816', medico_crm=21232)
                elif opcao == '3':
                    Consulta.editar_consulta(
                        session,
                        id_consulta=int(input("Digite o ID da consulta que deseja editar: "))
                    )
                elif opcao == '4':
                    Consulta.cancelar_consulta(
                        session=session, 
                        id_consulta=int(input("Digite o ID da consulta que quer deletar: "))
                    ) 
                elif opcao == '5':
                    print("Visualizando pacientes...")
                    # Funcionalidades
                    Medico.visualizar_todos_paciente(session)
                elif opcao == '6':
                    print("Adicionando pacientes...")
                    novo_paciente = Paciente.adicionar_paciente(
                        session=session,
                        cpf='42276413816',
                        nome='Arthur Antonio',
                        data_nascimento=datetime(2015, 3, 18).date(),
                        telefone='11999999999',
                        sexo='Masculino',
                        endereco='Rua Exemplo, 123',
                        nacionalidade='Brasileiro', 
                        senha='13815'  
                    )
                    print(f"Paciente {novo_paciente.nome_paciente} adicionado com sucesso!")
                elif opcao == '7':
                    # Adicionando Diagnóstico
                    novo_diagnostico = Diagnostico.adicionar_diagnostico(
                        session=session,  
                        cid="F32.0",
                        descricao="Episódio depressivo leve",
                        consulta_id=1,
                        paciente_cpf="42276413816",
                        medico_crm=21232
                    )

                    if novo_diagnostico:
                        print(f"Diagnóstico adicionado: {novo_diagnostico.cid} - {novo_diagnostico.descricao}")
                elif opcao == '8':
                    #Adicionando Tratamento
                    novo_tratamento = Tratamento.adicionar_tratamento(
                        session=session,
                        descricao="Testando descricao", 
                        duracao="1 semana", 
                        medicamentos="Remédio pra loucura",
                        diagnostico_id=1  
                    )

                    if novo_tratamento:
                        print(f"Tratamento adicionado: {novo_tratamento.descricao}, tratamento em virtude do diagnostico: {novo_tratamento.diagnostico_id}")
                elif opcao == '9':
                    # Adicionando Receita
                    nova_receita = Receita.adicionar_receita(
                        session=session,
                        crm_medico=21232,
                        nome_medico="Pedro",
                        cpf_paciente='42276413816',  # CPF como string
                        nome_paciente="Arthur Antonio",
                        id_diagnostico=1,
                        id_tratamento=1,
                        descricao="Testando", 
                        data_receita=datetime(2024, 11, 6).date()
                    )

                    if nova_receita:
                        print(f"Receita criada para o Paciente: {nova_receita.nome_paciente}, pelo DR(A): {nova_receita.nome_medico}")
                elif opcao == '10':
                    Receita.visualizar_receitas_paciente(session, paciente_cpf=input("Digite o CPF do Paciente: "))
                elif opcao == '11':
                    # Associe o paciente ao prontuário
                    Prontuario.associar_paciente(session, cpf_paciente=input("Associar paciente ao prontuário: "))
                elif opcao == '12':
                    # Exibir todas as informações do paciente, consultas, tratamentos e receitas
                    Prontuario.exibir_informacoes(session, cpf_paciente=input("Digite o CPF do paciente que deseja ver o Prontuario: "))
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