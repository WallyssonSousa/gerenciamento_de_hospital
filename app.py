import os
from sqlalchemy import create_engine, DateTime, Column, String, Integer, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import menu_medico
import menu_paciente

from error import *
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
        try:

            paciente = session.query(Paciente).filter_by(cpf=cpf_paciente).first()
            if not paciente:
                raise ProntuarioPacienteNaoEncontradoError(cpf_paciente)

            prontuario = cls(cpf_paciente=cpf_paciente)
            session.add(prontuario)
            session.commit()

            print(f"Prontuario associado com sucesso ao Paciente {paciente.nome_paciente} (CPF: {paciente.cpf} )")
            return prontuario
        
        except Exception as e:
            print(f"Erro inesperado aconteceu ao associar paciente. Erro: {str(e)}")
        except ProntuarioPacienteNaoEncontradoError as e:
            print(e)
    
    @classmethod
    def exibir_informacoes(cls, session, cpf_paciente):
        try:

            prontuario = session.query(cls).filter_by(cpf_paciente=cpf_paciente).first()
            if not prontuario:
                raise ProntuarioNaoEncontradoError(cpf_paciente)

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

        except ProntuarioNaoEncontradoError as e:
            print(e)
        except Exception:
            print(f"Erro inesperado aconteceu ao exibir informações. Erro: {str(e)}")


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
        try:
            paciente_existe = session.query(Paciente).filter_by(cpf=cpf).first()
            if paciente_existe:
                raise PacienteAdicionarPacienteError(cpf)
            
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
        except PacienteAdicionarPacienteError as e:
            print(e)
        except Exception:
            print(f"Erro inesperado ao adicionar paciente. Erro: {str(e)}")
    
    @classmethod
    def visualizar_consultas(cls, session, paciente_cpf):
        try:
        
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
                raise PacienteVizualizarConsultasError(paciente_cpf)

        except PacienteVizualizarConsultasError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao vizualizar consultas. Erro: {str(e)}")

    @classmethod
    def cancelar_consulta(cls, session, paciente_cpf, id_consulta):
        try:  
            consulta = session.query(Consulta).filter_by(id_consulta=id_consulta, paciente_cpf=paciente_cpf).first()

            if consulta:
                if consulta.status:
                    consulta.status = False  
                    session.commit()
                    print(f"Consulta com ID {id_consulta} foi cancelada com sucesso!")
                else:
                    raise PacienteCancelarConsultasError(id_consulta)
            else:
                raise PacienteConsultaNaoEncontradaError(id_consulta, paciente_cpf)
            
        except(PacienteCancelarConsultasError, PacienteConsultaNaoEncontradaError) as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao cancelar consulta. Erro: {str(e)}")

    @staticmethod
    def deletar_paciente_por_cpf(session, cpf):
        try:

            paciente = session.query(Paciente).filter_by(cpf=cpf).first()

            if paciente:
                session.delete(paciente)
                session.commit()
                print(f"Paciente com CPF {cpf} deletado com sucesso!")
            else:
                raise PacienteDeletarPacienteError(cpf)
        
        except PacienteDeletarPacienteError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao deletar paciente. Erro: {str(e)}")

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
        try:

            medico_existe = session.query(Medico).filter_by(crm=crm).first()
            if medico_existe:
                raise MedicoExisteError(crm)
            novo_medico = cls(
                crm=crm,
                nome_medico=nome_medico,
                especialidade=especialidade,
                senha=senha
            )
            session.add(novo_medico)
            session.commit()
            return novo_medico
    
        except MedicoExisteError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao adicionar médico. Erro: {str(e)}")
    
    @classmethod
    def visualizar_todos_paciente(cls, session):
        try:

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

        except Exception as e:
            print(f"Erro inesperado ao vizualizar pacientes. Erro: {str(e)}")
            
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
        try:
            paciente = session.query(Paciente).filter_by(cpf=paciente_cpf).first()
            medico = session.query(Medico).filter_by(crm=medico_crm).first()
            if not paciente:
                raise ConsultaCpfNaoEncontradoError(paciente_cpf)  
            if not medico:
                raise ConsultaCrmNaoEncontradoError(medico_crm)

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

        except (ConsultaCpfNaoEncontradoError, ConsultaCrmNaoEncontradoError) as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao agendar consulta. Erro: {str(e)}")

    @classmethod
    def cancelar_consulta(cls, session, id_consulta):
        try:

            consulta = session.query(cls).filter_by(id_consulta=id_consulta).first()    
            if consulta:
                session.delete(consulta)
                session.commit()
                print(f"Consulta com ID {id_consulta} cancelada com sucesso!")
            else:
                raise ConsultaCancelarConsultaError(id_consulta)
    
        except ConsultaCancelarConsultaError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado aconteceu ao cancelar consulta. Erro: {str(e)}")

    @classmethod
    def editar_consulta(cls, session, id_consulta): 
        try:

            consulta = session.query(cls).filter_by(id_consulta=id_consulta).first()
            if not consulta:
                raise ConsultaEditarConsultaError(id_consulta)

            print("Deixe em branco para manter o valor atual")

            data_hora_str = input(f"Informe a nova data e hora da consulta (AAAA-MM-DD HH:MM) [{consulta.data_hora}]: ")
            if data_hora_str:
                consulta.data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')

            status_str = input(f"Informe o novo status da consulta (True/False) [{consulta.status}]: ")
            if status_str:
                consulta.status = status_str.lower() in ['true', 1]

            session.commit()
            print(f"Consulta com ID {id_consulta} atualizada com sucesso!")

        except ConsultaEditarConsultaError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao editar consulta. Erro: {str(e)}")
            

    @classmethod
    def visualizar_consultas_paciente(cls, session, paciente_cpf):
        try:
            
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
            else:
                raise ConsultaVizualizarConsultasPacienteError(paciente_cpf)
            
        except ConsultaVizualizarConsultasPacienteError as e:
            print(e) 
        except Exception as e:
            print(f"Erro inesperado ao vizualizar as consultas do paciente. Erro: {str(e)}")

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
        try:

            consulta = session.query(Consulta).filter_by(id_consulta=consulta_id).first()
            paciente = session.query(Paciente).filter_by(cpf=paciente_cpf).first()
            medico = session.query(Medico).filter_by(crm=medico_crm).first()

            if not consulta:
                raise DiagnosticoConsultaNaoEncontradaError(consulta_id)
            if not paciente:
                raise DiagnosticoPacienteNaoEncontradoError(paciente_cpf)
            if not medico:
                raise DiagnosticoMedicoNaoEncontradoError(medico_crm)

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
        
        except(DiagnosticoMedicoNaoEncontradoError, DiagnosticoConsultaNaoEncontradaError, DiagnosticoPacienteNaoEncontradoError) as e:

            print(e)
        except Exception as e:
            print(f"Erro inesperado ao adiconar diagnostico. Erro: {str(e)}")
    
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
        try:

            diagnostico = session.query(Diagnostico).filter_by(id_diagnostico=diagnostico_id).first()

            if not diagnostico:
                raise TratamentoDiagnosticoNaoEncontrado(diagnostico_id)

            novo_tratamento = cls(
                descricao=descricao, 
                duracao=duracao,
                medicamentos=medicamentos,
                diagnostico_id=diagnostico_id
            )
            session.add(novo_tratamento)
            session.commit()
            return novo_tratamento

        except TratamentoDiagnosticoNaoEncontrado as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao adicionar tratamento. Erro: {e}")
            
#=====================================RECEITA===============================================#    
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
        try: 
        
            paciente = session.query(Paciente).filter_by(cpf=cpf_paciente).first()
            medico = session.query(Medico).filter_by(crm=crm_medico).first()

            if not paciente: 
                raise ReceitaPacienteNaoEncontrado(cpf_paciente)
            if not medico: 
                raise ReceitaMedicoNaoEncontradoError(crm_medico)

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
        
        except(ReceitaMedicoNaoEncontradoError, ReceitaPacienteNaoEncontrado) as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado aconteceu ao adicionar receita. Erro: {str(e)}")
    

    @classmethod
    def visualizar_receitas_paciente(cls, session, paciente_cpf):
        try:

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
                raise ReceitaVizualizarReceitaPacienteError(paciente_cpf)

        except ReceitaVizualizarReceitaPacienteError as e:
            print(e)
        except Exception as e:
            print(f"Erro inesperado ao vizulizar receitas do paciente. Erro: {str(e)}")





# Criando as tabelas no banco de dados
Base.metadata.create_all(db)

# Inserção de Dados

#===================================================== Login ======================================================================= #

def login(cpf=None, crm=None, senha=None, user_type=None): 
    try: 
        if user_type == '1':  # Login como paciente
            paciente = session.query(Paciente).filter_by(cpf=cpf, senha=senha).first()
            if paciente:
                print(f"Login bem-sucedido! Bem-vindo {paciente.nome_paciente}")
                opcao = menu_paciente.menu_paciente()
                while opcao != '4':
                    if opcao == '1':
                        Paciente.visualizar_consultas(session, paciente_cpf=cpf)
                    elif opcao == '2':
                        Paciente.cancelar_consulta(session, paciente_cpf=cpf, id_consulta=input("Digite o ID da consulta: "))
                    elif opcao == '3':
                        Receita.visualizar_receitas_paciente(session, paciente_cpf=cpf)
                    else:
                        print("Opção inválida. Tente novamente.")
                    opcao = menu_paciente.menu_paciente()
            else:
                print("Usuário não encontrado!")

        elif user_type == '2':  # Login como médico
            medico = session.query(Medico).filter_by(crm=crm, senha=senha).first()
            if medico:
                print(f"Login bem-sucedido como Médico, bem-vindo {medico.nome_medico}")
                opcao = menu_medico.menu_medico()
                while opcao != '14':
                    if opcao == '1':
                        Consulta.visualizar_consultas_paciente(session, paciente_cpf=input("Digite o CPF do paciente: "))
                    elif opcao == '2':
                        Consulta.agendar_consulta(session, paciente_cpf=input("Digite o CPF do paciente: "), medico_crm=input("Digite o CRM do médico: "))
                    elif opcao == '3':
                        Consulta.editar_consulta(session, id_consulta=int(input("Digite o ID da consulta que deseja editar: ")))
                    elif opcao == '4':
                        Consulta.cancelar_consulta(session, id_consulta=int(input("Digite o ID da consulta para cancelar: ")))
                    elif opcao == '5':
                        Medico.visualizar_todos_paciente(session)
                    elif opcao == '6':
                        novo_paciente = Paciente.adicionar_paciente(
                            session=session, 
                            cpf=input("Digite o CPF do Paciente: "), 
                            nome=input("Digite o Nome do Paciente: "),
                            data_nascimento=datetime.strptime(input("Digite a Data de Nascimento (AAAA-MM-DD): "), "%Y-%m-%d").date(),
                            telefone=input("Digite o Telefone: "),
                            sexo="Digite o sexo do Paciente: ", 
                            endereco=input("Digite o Endereco: "), 
                            nacionalidade=input("Digite a nacionalidade: "),
                            senha=input("Digite a senha: (5 Primeiras letras do CPF): ")
                        )
                        print(f"Paciente {novo_paciente.nome_paciente} adicionado com sucesso!")
                    elif opcao == '7':
                        # A função 'excluir_paciente' deve ser definida fora do bloco do 'if' e ser chamada com a 'session' como argumento
                        def excluir_paciente(session):
                            cpf = input("Digite o CPF do paciente que deseja excluir: ")
                            Paciente.deletar_paciente_por_cpf(session, cpf)

                        # Passando a session ao chamar a função
                        excluir_paciente(session)
                    elif opcao == '8':
                        novo_diagnostico = Diagnostico.adicionar_diagnostico(
                            session=session, 
                            cid=input("Digite o cid do diagnostico: "),
                            descricao=input("Digite a descricao do diagnostico: "), 
                            consulta_id=input("Digite o ID da consulta: "),
                            paciente_cpf=input("Digite o CPF do paciente: "), 
                            medico_crm=input("Digite o CRM do médico: ")
                        )
                        print(f"Diagnóstico adicionado: {novo_diagnostico.cid} - {novo_diagnostico.descricao}")
                    elif opcao == '9':
                            novo_tratamento = Tratamento.adicionar_tratamento(
                                session=session,
                                descricao=input("Digite a descricao do tratamento: "), 
                                duracao=input("Digite a duracao do tratamento: "), 
                                medicamentos=input("Digite o medicamento do tratamento: "),
                                diagnostico_id=input("Digite o ID do diagnostico: ")  
                            )
                            # Verifique se o retorno não é None
                            if novo_tratamento:
                                print(f"Tratamento adicionado: {novo_tratamento.descricao}")
                            else:
                                print("Erro ao adicionar tratamento: Não foi retornado um tratamento válido.")

                            print(f"Tratamento adicionado: {novo_tratamento.descricao}")
                    elif opcao == '10':
                        nova_receita = Receita.adicionar_receita(
                            session=session, 
                            crm_medico=input("CRM do médico: "),
                            nome_medico=input("Digite o nome do médico: "), 
                            cpf_paciente=input("Digite o CPF do paciente: "),
                            nome_paciente=input("Digite o nome do Paciente: "), 
                            id_diagnostico=input("Digite o ID do diagnostico: "),
                            id_tratamento=input("Digite o ID do tratamento: "), 
                            descricao=input("Digite a descricao da receita: "), 
                            data_receita=datetime.strptime(input("Digite a Data da Receita (AAAA-MM-DD): "), "%Y-%m-%d").date())
                        print(f"Receita criada para o Paciente: {nova_receita.nome_paciente}, pelo Dr(a): {nova_receita.nome_medico}")
                    elif opcao == '11':
                        Receita.visualizar_receitas_paciente(session, paciente_cpf=input("Digite o CPF do paciente: "))
                    elif opcao == '12':
                        Prontuario.associar_paciente(session, cpf_paciente=input("Associar paciente ao prontuário: "))
                    elif opcao == '13':
                        Prontuario.exibir_informacoes(session, cpf_paciente=input("Digite o CPF do paciente para ver o prontuário: "))
                    else:
                        print("Opção inválida. Tente novamente.")
                    opcao = menu_medico.menu_medico()
            else:
                print("Médico não encontrado!")
        elif user_type == '4':  
            admin_password = "admin123"
            if senha == admin_password:
                print(f"Login bem-sucedido como Administrador!")
                novo_medico = Medico.adicionar_medico(
                    session=session,
                    crm=input("Digite um crm: "), 
                    nome_medico=input('Digite o nome do médico: '),
                    especialidade=input("Digite a especialidade: "),
                    senha=int(input("Digite sua senha: "))
                )
                print(f"DR(A): {novo_medico.nome_medico} do CRM: {novo_medico.crm} adicionado com sucesso!") 
            else:
                print("Senha do Administrador incorreta!")
    except Exception as e:
        print(f"Erro inesperado! Erro: {str(e)}")

def escolha_usuario():
    print("\n==================== Deseja fazer login como: ======================")
    print("1. 👤 Paciente")
    print("2. 🧑‍⚕ Médico")
    print("3. 🚪 Sair")
    print("4. 👑 Admin")
    print("=======================================================")
    opcao = input("Escolha uma opção: ")
    return opcao

def obter_dados_login(usuario_tipo):
    if usuario_tipo == '1':  # Paciente
        cpf = input("Digite seu CPF: ")
        return cpf, None
    elif usuario_tipo == '2':  # Médico
        crm = input("Digite seu CRM: ")
        return None, crm
    elif usuario_tipo == '4':
        return None, None

usuario_tipo = escolha_usuario()
cpf, crm = obter_dados_login(usuario_tipo)
senha = input("Digite sua senha: ")

login(cpf=cpf, crm=crm, senha=senha, user_type=usuario_tipo)