"""
Gerencia a carga dos dados de uma planilha do Excel.
"""

# módulo usado para  implementar method overloading
# ATENÇÃO: este módulo *não é* thread safe
# (https://stackoverflow.com/questions/6434482/python-function-overloading)
# ATENÇÃO: métodos que usam o decorator dispatch e que contenham argumentos
# nomeados com valores default: se o valor default for alterado na chamada do
# método, precisa ser por meio de argumento nomeado, não pode se basear na
# posição do argumento
# (https://stackoverflow.com/questions/54132640/how-to-use-default-parameter-with-multipledispatch)

import pandas as pd
import blipy.erro as erro


class Planilha():
    """
    Planilha a ser carregada no banco de dados.
    """

    def carrega_dados(self, io=None, sheet_name=0, header=0, skipfooter=0, names=None, index_col=None, usecols=None,
                      skiprows=None, nrows=None, na_values=None, engine='openpyxl'):
        """
                Lê uma aba de uma planilha de Excel e carrega em um Data Frame do Pandas.
                    Args:
                        :param io:         Caminho (path) do arquivo, com nome do arquivo incluso ou uma URL
                        :param sheet_name: Aba ou guia do Excel, pode ser o nome ou número 0-indexed
                        :param header:     Linhas de cabeçalho a serem ignoradas, 0-indexed
                        :param skipfooter: Linhas de rodapé (final arquivo) a serem ignoradas, 0-indexed.
                        :param names:      Lista de nomes de colunas. Se arquivo não contém header, deve-se obrigatoriamente setar header=None
                        :param index_col:  int, list of int, default None - Coluna com o índice do
                        :param usecols:    Seleção de colunas. Tipos de seleção: 'A,B,C', [0,1,2], ['ID','Coluna_1','Coluna_4']
                        :param skiprows:   Linhas a serem ignoradas no início do arquivo, 0-indexed.
                        :param nrows:      Número de linhas carregadas.
                        :param na_values:  Lista de strings a serem consideradas como dados não disponívels NaN
                        :param engine:     O padrão é openpyxl. Existem outras para formatos antigos ex .odf
                        Referência - https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

                    Ret:
                        :return: self.__tabela_data_frame
        """

        self.__tabela_data_frame = None  # Data Frame da planilha carregada
        self.__cursor            = None  # Iterável para função le_prox_registro()
        self.e = erro.console

        # Verificações de possíveis erros
        if io is None:
            self.e._("O argumento 'io' é o mínimo para funcionamento da função. \n"
                     "Este é o caminho (path) para a planilha com o nome do arquivo incluso ao final e com a extensão .xlsx ou .xls. \n"
                     "Formato esperado: C:/.../planilha.xlsx")
            raise RuntimeError

        if io.endswith('.xlsx') and engine != 'openpyxl':
            self.e._("Parâmetro 'engine' não adequado para o tipo de arquivo.\n"
                     "O argumento 'io' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'io' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        if io.endswith('.xls') and engine != 'xlrd':
            self.e._("Parâmetro 'engine' não adequado para o tipo de arquivo.\n"
                     "O argumento 'io' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'io' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        if not io.endswith(('.xlsx','.xls')):
            self.e._("O argumento 'io' caminho (path) para a planilha deve terminar com: .xlsx ou .xls.\n"
                     "Para cada formato de arquivo existe uma engine adequada.\n"
                     "Engine 'openpyxl' para .xlsx e 'xlrd' para .xls.\n"
                     "Exemplos de parâmetro 'io' esperados:\n"
                     "\tC:/.../planilha.xlsx\n"
                     "\tC:/.../planilha.xls\n")
            raise RuntimeError

        # Carregamento da tabela para a memória
        self.__tabela_data_frame = pd.read_excel(io=io,sheet_name=sheet_name, header=header, skipfooter=skipfooter,
                                                 names=names, index_col=index_col, usecols=usecols, skiprows=skiprows,
                                                 nrows=nrows, na_values=na_values, engine=engine)


    def recarrega_dados(self):
        """
        Faz o reset do cursor para o ponto inicial a partir do data frame carregado.
        Ret:
            Iterável com os registros de una tabela do Excel
            se a tabela ainda não foi carregada em um data frame retorna erro.
        """
        if self.__tabela_data_frame is None:
            self.e._("A planilha não pode ser recarregada pois ainda não "
                     "foi carregada pela primeira vez.\n"
                     "Necessário executar a função carrega_dados() primeiro.")
            raise RuntimeError

        # Reset do cursor para o index 0.
        self.__cursor = None
        self.__cursor = self.__tabela_data_frame.itertuples()


    def le_prox_registro(self):
        """
        Lê a próximo registro da tabela.
        Ret:
            tupla com o registro lido ou None se não houver mais registros a
            serem lidos.
        """

        if self.__cursor is None:
            self.__cursor = self.__tabela_data_frame.itertuples()

        try:
            registro = next(self.__cursor)
            registro = tuple(registro)
        except StopIteration:
            registro = None

        return registro
