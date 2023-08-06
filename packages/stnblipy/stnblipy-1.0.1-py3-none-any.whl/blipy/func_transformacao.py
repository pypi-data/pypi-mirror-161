
"""
Funções de transformação a serem usadas nas cargas ("T" do ETL).
"""

from datetime import date, datetime


"""
Módulo com as classes de transformação de dados ("T" do ETL)
"""

class Copia():
    """
    Cópia simples de dados, sem transformações ou nenhum tipo de alteração.
    """

    def transforma(self, entradas):
        """
        Copia a entrada, sem nenhuma transformação.

        Args:
            entradas   : tupla com o valor a ser copiado; como não faz
                         transformação alguma, só pode haver um elemento na
                         tupla
        Ret:
            cópia do valor de entrada
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para cópia.")

        return entradas[0]

class ValorFixo():
    """
    Transforma a entrada num valor fixo.
    """

    def __init__(self, valor):
        self.__valor = valor

    def transforma(self, entradas):
        """
        Retorna um valor fixo, definido na instanciação do objeto.

        Args:
            entradas   : não é necessário, mantido apenas para consistência da 
                         interface
        Ret:
            Valor definido na instanciação da classe
        """

        return self.__valor

class DePara():
    """
    Faz um de/para dos valores de entrada.
    """

    def __init__(self, de_para, copia_se_nao_encontrado=True):
        """
        Args:
            de_para                 : dict com o de/para desejado
            copia_se_nao_encontrado : se True, copia valor da entrada para a
                                      saída caso valor de entrada não seja
                                      encontrado no de/para; se False, dispara
                                      exceção
        """
        self.__de_para = de_para
        self.__copia_se_nao_encontrado = copia_se_nao_encontrado

# TODO: criar outras condições se não achar o valor no de/para: preenche null ou um valor específico; tem que mudar o método transforma() abaixo e ver quais impactos na classe filha deparasn

    def transforma(self, entradas):
        """
        Retorna um de/para dos valores de entrada.

        Args:
            entradas   : tupla com o valor a ser transformado; como só
                         transforma um valor em outro, só pode haver um
                         elemento na tupla
        Ret:
            De/para da entrada.
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada para um de/para.")

        for item in entradas:
            if item in list(self.__de_para):
                return self.__de_para[item]

        if self.__copia_se_nao_encontrado:
            return entradas[0]
        else:
# TODO: disparar uma exceção específica pra master job decidir se quer continuar ou não se não achar de/para
            #  não achou a key no de_para informado no construtor
            raise RuntimeError(
                "Impossível fazer a transformação, valor de de/para não encontrado.")

class DeParaSN(DePara):
    """
    Faz um de/para de campos S/N para 1/0 e vice-versa. Considera também
    a língua (por exemplo, Y/N ao invés de S/N).
    """

    def __init__(self, 
            copia_se_nao_encontrado=True, 
            inverte=False, 
            val_int=True, 
            lingua="pt"):
        """
        Args:
            copia_se_nao_encontrado  : dispara execeção de erro caso valor não
                                      seja encontrado no de/para; se False,
                                      copia valor da entrada para a saída
            inverte                 : se de/para é de S/N para 1/0 ou de 1/0 
                                      para S/N
            val_int                 : se valor 1/0 deve ser um inteiro ou
                                      string
            lingua                  : "pt" ou "en"
        """

        if lingua == "pt" and val_int and not inverte:
            de_para = {"S": 1, "N": 0}
        elif lingua == "pt" and not val_int and not inverte: 
            de_para = {"S": "1", "N": "0"}

        elif lingua == "pt" and val_int and inverte: 
            de_para = {1: "S", 0: "N"}
        elif lingua == "pt" and not val_int and inverte: 
            de_para = {"1": "S", "0": "N"}

        elif lingua == "en" and val_int and not inverte: 
            de_para = {"Y": 1, "N": 0}
        elif lingua == "en" and not val_int and not inverte: 
            de_para = {"Y": "1", "N": "0"}

        elif lingua == "en" and val_int and inverte: 
            de_para = {1: "Y", 0: "N"}
        elif lingua == "en" and not val_int and inverte: 
            de_para = {"1": "Y", "0": "N"}

        super().__init__(de_para, copia_se_nao_encontrado)

class Somatorio():
    """
    Calcula o somatório dos valores de entrada.
    """

    def transforma(self, entradas):
        """
        Calcula o somatório dos valores de entrada.

        Args:
            entradas   : tupla com os valores a serem somados
        Ret:
            somatório dos valores de entrada
        """

        soma = 0
        for item in entradas:
            soma += item
        return soma

class Media():
    """
    Calcula a média dos valores de entrada.
    """

    def transforma(self, entradas):
        """
        Calcula a média dos valores de entrada.

        Args:
            entradas   : tupla com os valores dos quais calcular a média
        Ret:
            média dos valores de entrada
        """

        soma = f_somatorio.transforma(entradas)
        return soma/len(entradas)

class Agora():
    """
    Calcula o dia ou dia/hora atual do banco de dados ou do sistema 
    operacional.
    """

    def __init__(self, conexao=None, so_data=False):
        """
        Args:
            conexao : conexão com o banco de dados (caso se busque a
                      informação no banco) ou None se for para buscar no
                      sistema operacional
            so_data : flag se é para trazer só a data ou a hora também
        """
        self.__so_data = so_data
        self.__conn = conexao

    def transforma(self, entradas):
        """
        Calcula o dia/hora atual.

        Args:
            entradas   : não é necessário, mantido apenas para consistência da 
                         interface
        Ret:
            Dia (ou dia/hora) atual do banco de dados ou do sistema
            operacional, a depender de como o objeto foi construído.
        """

        if self.__conn is None:
            # busca do sistema operacional
            if self.__so_data:
                ret = date.today()
            else:
                ret = datetime.now().replace(microsecond=0)
        else:
            # busca do banco de dados
            if self.__so_data:
                ret = self.__conn.get_agora().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                ret = self.__conn.get_agora().replace(microsecond=0)

        return ret


# TODO: implementar classe de transformação de conversão tipo

#  objetos de classes de transformação que só fazem sentido ter uma instância 
#  (singletons). Desta forma, ao importar este módulo estes objetos já estarão
#  instanciandos e bastará utilizá-los, sem necessidade de criar uma nova
#  instância no código que importou este módulo
f_copia     = Copia()
f_somatorio = Somatorio()
f_media     = Media()

