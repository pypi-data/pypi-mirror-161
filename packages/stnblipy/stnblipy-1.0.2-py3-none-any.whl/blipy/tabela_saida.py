
"""
Gerencia a gravação de dados numa tabela no banco.
"""

# TODO: ajustar tratamento de erro para tratamento próprio

import blipy.erro as erro
from blipy.profiling import ProfilingPerformance
from blipy.enum_tipo_col_bd import TpColBD as tp

class TabelaSaida(ProfilingPerformance):
    """
    Tabela a ser gravada no banco de dados.
    """

    def __init__(self, nome, colunas, conexao_bd):
        """
        Args:
            nome        : nome da tabela no banco
            colunas     : dict com objetos do classe Coluna representando as
                          colunas do banco
            conexao_bd  : conexão com o banco de dados
        """

        self.__nome         = nome
        self.__conexao_bd   = conexao_bd
        self.col            = colunas

        # tratamento de erro
        # este atributo é público, portanto pode ser alterado por quem usa 
        # esta classe se quiser um tipo de tratamento de erro diferente de 
        # imprimir mensagem no console
        self.e = erro.console

        self._profiling_on = False


    def habilita_profiling_performance(self, path_csv=""):
        """
        Habilita o registro de performance para essa classe em si e para todas
        as colunas que compõem a tabela.
        """
        
        # habilita profiling pra todas as colunas que compõem a tabela
        for key in list(self.col):
            self.col[key].habilita_profiling_performance(path_csv)

        self._profiling_on = True

# TODO: criar parâmetro para estratégia de gravacao (limpa e grava tudo, insert, update etc.)
    def grava_registro(self):
        """
        Grava os dados da tabela no banco.

        Um erro de banco disparará uma exceção.
        """

        if self._profiling_on:
            self._inicia_timer()

        cols = ""
        for coluna in self.col:
            cols += self.col[coluna].nome + ", "
        cols = cols[:len(cols)-2]

        # TODO: tratar demais tipos possíveis do banco (como bool)
        values = ""
        for coluna in self.col:
            if self.col[coluna].valor is None:
                values += "NULL"
            else:
                if self.col[coluna].tipo == tp.STRING:
                    values += "'" + self.col[coluna].valor + "'"
                elif self.col[coluna].tipo == tp.INT       or \
                     self.col[coluna].tipo == tp.NUMBER:
                    values += str(self.col[coluna].valor)

                elif self.col[coluna].tipo == tp.DATE:
                    values += "TO_DATE('" + str(self.col[coluna].valor) + \
                        "', 'yyyy-mm-dd hh24:mi:ss')"
                else:
                    self.e._(   "Tipo de dado inválido para a coluna " \
                                + self.col[coluna].nome + " da tabela " + \
                                self.__nome + ".")
                    if self._profiling_on:
                        self._finaliza_timer()
# TODO: disparar uma exceção específica pro master job saber se continua ou não (?)
                    raise RuntimeError

            values += ", "
        values = values[:len(values)-2]

        # TODO: implementar os outros estratégias além do insert: insert_update, update_insert, update
        self.__conexao_bd.executa(
                "insert into " 
                + self.__nome + 
                " (" + cols + ") " + 
                " values ( " + values +
                ") "
            )

        if self._profiling_on:
            self._finaliza_timer()

class Coluna(ProfilingPerformance):
    """
    Uma coluna de uma tabela do banco de dados.
    """

# TODO: parâmetro 'tipo' seria interessante se fosse pra fazer um cast automático do resultado da ft para o valor da coluna
    def __init__(self, nome, tipo, func_transf):
        """
        Args:
            nome        : nome da coluna no banco de dados
            tipo        : tipo da coluna no banco de dados. É um elemento do 
                          enum tipo_col_bd
            func_transf : função de transformação que será aplicada para obter
                          o valor da coluna. Se for None, valor da coluna no 
                          banco de dados será NULL
        """
        self.nome           = nome
        self.tipo           = tipo
        self.__func_transf  = func_transf
        self.valor          = None

        # tratamento de erro
        # este atributo é público, portanto pode ser alterado por quem usa 
        # esta classe se quiser um tipo de tratamento de erro diferente de 
        # imprimir mensagem no console
        self.e = erro.console

        self._profiling_on = False

    def calcula_valor(self, entradas=None):
        """
        Calcula o valor da coluna de acordo com sua função de transformação.
        Se a função de transformação for None, valor será NULL (None).

        Arg:
            entradas    : tupla de valores a ser passado para a função de
                          transformação
        """

        if self._profiling_on:
            self._inicia_timer()

        if self.__func_transf is None:
            self.valor = None
        else:
            try:
                self.valor = self.__func_transf.transforma(entradas)
            except Exception as err:
                self.e._(
                    f"Erro ao calcular o valor da coluna {self.nome}." + 
                    "\n" + str(err))
                if self._profiling_on:
                    self._finaliza_timer()
                raise RuntimeError

        if self._profiling_on:
            self._finaliza_timer()

