
"""
Módulo para tratamento de erros.
"""

import inspect

class TpSaida():
    CONSOLE     = 1
    # valores dos próximos têm que ser o valor anterior * 2, Por exemplo:
    # (isso vai permitir mais de uma saída ao mesmo tempo)
    # EMAIL     = 2
    # TEAMS     = 4
    # BD        = 8

class TratamentoErro():
    """
    Classe para emissão de mensagens de erro formatadas. Para ser usado dentro
    de um bloco try..except, por exemplo.
    """

    def __init__(self, saida=TpSaida.CONSOLE):
        """
        Args:
            saida:  : indica onde a mensagem de erro será exibida.
                       Atualmente, única opção é exibir o erro no console.
        """

        self.__saida = saida

    def _(self, msg):
        """
        Emite a mensagem de erro formatada na saída definida para esta
        instância.

        Args:
            msg:  a mensagem de erro
        """

        #  pega objeto que chamou essse método aqui
        chamador = inspect.stack()[1]

        if "self" in chamador.frame.f_locals:
            obj = " de " + str(type(chamador.frame.f_locals["self"])) + ":"

            # pega o nome do método que  chamou o tratamento do erro
            # https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback
            func = chamador[3]
        elif "__name__" in chamador.frame.f_locals:
            obj = ":"
            func = chamador.frame.f_locals["__name__"]
        else:
            obj = ":"
            func = "não foi possível identificar a função"

        if self.__saida & TpSaida.CONSOLE:
            print()
            print("============= ERRO ================")
            print(  "Ocorreu um erro " 
                    f"na função <{func}>{obj}" )
            print(msg)
            print("===================================")
            print()
        else:
            raise NotImplementedError

# Instância criada por conveniência para uso mais comum desta classe
console = TratamentoErro(TpSaida.CONSOLE)

