#===============================PRONTUARIO ERRO====================================================#
class ProntuarioPacienteNaoEncontradoError(Exception):
    def __init__(self, cpf_paciente):
        self.message = f"Paciente com o CPF {cpf_paciente} não encontrado!"
        super.__init__(self.message)

class ProntuarioNaoEncontradoError(Exception):
    def __init__(self, cpf_paciente):
        self.message = f"Nenhum prontuário encontrado para o paciente com CPF {cpf_paciente}."
        super().__init__(self.message)

#======================PACIENTE ERRO==============================================================#
class PacienteAdicionarPacienteError(Exception):
    def __init__(self, cpf):
        self.message = f"CPF {cpf} ja cadastrado no sistema."
        super.__init__(self.message)

class PacienteVizualizarConsultasError(Exception):
    def __init__(self, paciente_cpf):
        self.message = f"Nenhuma consulta encontrada para o paciente com CPF {paciente_cpf}"
        super().__init__(self.message)

class PacienteCancelarConsultasError(Exception):
    def __init__(self, id_consulta):
        self.message = f"A consulta {id_consulta} já foi cancelada."
        super().__init__(self.message)

class PacienteConsultaNaoEncontradaError(Exception):
    def __init__(self, id_consulta, paciente_cpf):
        self.message = f"A consulta {id_consulta} não foi encontrada ou ela não pertence ao paciente com CPF {paciente_cpf}"
        super().__init__(self.message)

class PacienteDeletarPacienteError(Exception):
    def __init__(self, cpf):
        self.message = f"Erro ao deletar paciente, paciente com CPF {cpf} não encontrado."
        super().__init__(self.message)

#=======================MEDICO ERRO=======================================================#
class MedicoExisteError(Exception):
    def __init__(self, crm):
        self.message = f"O CRM {crm} já pertence a outro médico"
        super().__init__(self.message)

#=========================CONSULTA ERRO===================================================#
class ConsultaCpfNaoEncontradoError(Exception):
    def __init__(self, paciente_cpf):
        self.message = f"Paciente com o CPF {paciente_cpf} não encontrado."
        super().__init__(self.message)

class ConsultaCrmNaoEncontradoError(Exception):
    def __init__(self, medico_crm):
        self.message = f"Paciente com o CPF {medico_crm} não encontrado."
        super().__init__(self.message)

class ConsultaCancelarConsultaError(Exception):
    def __init__(self, id_consulta):
        self.message = f"Consulta {id_consulta} não encontrada."
        super().__init__(self.message)

class ConsultaEditarConsultaError(Exception):
    def __init__(self, id_consulta):
        self.message = f"Consulta {id_consulta} não encontrada."
        super().__init__(self.message)

class ConsultaVizualizarConsultasPacienteError(Exception):
    def __init__(self, paciente_cpf):
        self.message = f"Houve um erro ao mostrar as consultas do Paciente com CPF {paciente_cpf}. Tente Novamente!."
        super().__init__(self.message)

#==========================DIAGNOSTICO ERRO============================================================#
class DiagnosticoConsultaNaoEncontradaError(Exception):
    def __init__(self, id_consulta):
        self.message = f"Consulta {id_consulta} não encontrada."
        super().__init__(self.message)

class DiagnosticoPacienteNaoEncontradoError(Exception):
    def __init__(self, cpf_paciente):
        self.message = f"Paciente com CPF {cpf_paciente} não encontrado."
        super().__init__(self.message)

class DiagnosticoMedicoNaoEncontradoError(Exception):
    def __init__(self, crm):
        self.message = f"Medico com CRM {crm} não encontrado."
        super().__init__(self.message)

#==========================RECEITA ERRO============================================================#
class ReceitaPacienteNaoEncontrado(Exception):
    def __init__(self, cpf_paciente):
        self.message = f"Paciente com CPF {cpf_paciente} não encontrado."
        super().__init__(self.message)

class ReceitaMedicoNaoEncontradoError(Exception):
    def __init__(self, crm):
        self.message = f"Medico com CRM {crm} não encontrado."
        super().__init__(self.message)

class ReceitaVizualizarReceitaPacienteError(Exception):
    def __init__(self, cpf_paciente):
        self.message = f"Nenhuma receita encontrada para o paciente com CPF {cpf_paciente}."
        super().__init__(self.message)

#==========================TRATAMENTO ERRO=====================================================#
class TratamentoDiagnosticoNaoEncontrado(Exception):
    def __init__(self, diagnostico_id):
        self.message = f"Não foi encontrado o diagnostico com ID {diagnostico_id}."
        super().__init__(self.message)