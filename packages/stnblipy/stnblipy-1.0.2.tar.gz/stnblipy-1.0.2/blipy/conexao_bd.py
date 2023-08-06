
"""
Gerencia a conexão com um banco de dados.
"""

# TODO: colocar métodos num try. o catch desses try's vai ser feito nas funções que chamarem isso aqui, aqui vai tratar o erro e dar re-raise

from sqlalchemy import create_engine
import os
import blipy.erro as erro

class ConexaoBD():
    """
    Conexão com o banco de dados.

    Qualquer falha na criação dessa conexão dispara uma exceção.
    """

    def __init__(self, user, pwd, ip, port, service_name):
        self.__conexao = None

        # tratamento de erro
        # este atributo é público, portanto pode ser alterado por quem usa 
        # esta classe se quiser um tipo de tratamento de erro diferente de 
        # imprimir mensagem no console
        self.e = erro.console

        try:
            cstr = "oracle://" +    user + ":" +                \
                                    pwd + "@" +                 \
                                    ip + ":" +                  \
                                    port + "/?service_name=" +  \
                                    service_name

            engine = create_engine( cstr, 
                                    convert_unicode=True, 
                                    connect_args={"encoding": "UTF-8"})

            self.__conexao = engine.connect()

        except Exception as err:
            self.e._(   "Erro ao conectar com o banco de dados."
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

    def __del__(self):
        if self.__conexao != None:
            try:
                self.__conexao.close()
            except:
                self.e._(   "Erro ao fechar conexão com o banco de dados."
                            "\nDetalhes do erro:\n" + str(err))
                raise RuntimeError

# TODO: precisa desse consulta? não pode ser só o executa? se sim, precisar, então fazê-lo chamar o executa e testar se o sql é mesmo de uma consulta; o try vai ficar no meu executa()
    def consulta(self, sql):
        """
        Executa uma comando de consulta no banco.

        Args:
            sql     : SELECT a ser executado no banco
        Ret:
            Cursor com o resultado do SELECT.
        """

        return self.__conexao.execute(sql)

# TODO: criar métodos insere, atualiza (?)
    def executa(self, sql, commit=False):
        """
        Executa um comando sql no banco.

        Args:
            sql     : sql a ser executado no banco
            commit  : flag indicativa se haverá um commit após a execução do
                      sql ou não 
        Ret:
            Cursor com o resultado do comando sql.
        """

        try:
            if not commit:
                ret = self.__conexao.execute(sql)
            else:
                trans = self.__conexao.begin()
                ret = self.__conexao.execute(sql)
                trans.commit()
        except Exception as err:
            self.e._(   "Erro ao executar o seguinte comando no banco de "
                        "dados:\n" + sql + 
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

        return ret

    def get_agora(self):
        """
        Retorna o dia e hora atuais do banco.
        """
        return self.consulta("select sysdate from dual").first()[0]

    def tabela_existe(self, tabela):
        """
        Verifica se uma tabela existe no banco.

        Arg:
            tabela  : nome da tabela no banco
        Ret:
            True se tabela existe, False se não existe.
        """
        return self.__conexao.dialect.has_table(self.__conexao, tabela)

    def apaga_registros(self, tabela, condicao=None, commit=False):
        """
        Apaga registros de uma tabela no banco, de acordo com a condição
        informada.

        Args:
            tabela      : nome da tabela no banco
            condicao    : condição WHERE da deleção; se não informado, apaga
                          todas as linhas da tabela
            commit      : flag indicativa se haverá um commit após a execução 
                          da deleção ou não 
        """
        if condicao is not None:
            condicao = " where " + condicao
        else:
            condicao = ""

        sql = "delete from " + tabela + condicao
        try:
            self.executa(sql , commit)
        except Exception as err:
            self.e._(   "Erro ao apagar registros do banco de dados." 
                        "O seguinte comando falhou:\n" + sql + 
                        "\nDetalhes do erro:\n" + str(err))
            raise RuntimeError

