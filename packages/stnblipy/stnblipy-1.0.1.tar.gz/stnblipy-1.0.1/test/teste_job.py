
"""
Exemplos de uso e casos de teste.
"""

import sys

from blipy.conexao_bd import ConexaoBD
from blipy import tabela_entrada as ti
from blipy import tabela_entrada as ti
from blipy import tabela_saida as to
from blipy import func_transformacao as ft
from blipy import erro as e
from blipy.enum_tipo_col_bd import TpColBD as tp


# TODO: testar algum campo da entrada == null (na leitura da tupla de entrada ele vira None? se sim, meu código continua funcionando?)

def executa_master_job():
    user            = "TESTES_BLIPY"
    pwd             = "4cmSnZDyVhaQx1J"
    ip              = "cluster3-scan"
    port            = "1521"
    service_name    = "DWPROD"

    # conecta com o banco
    try:
        conn = ConexaoBD(user, pwd, ip, port, service_name)
    except:
        sys.exit()

    # cria a tabela de entrada
    abrangencia_in = ti.TabelaEntrada(conn)

    testes = 1
    if testes & 1:
        # --------------------------------------
        # caso 1: cópia simples de tabelas
        # --------------------------------------

        abrangencia_in.carrega_dados( """
            select 
                ID_ABRANGENCIA, 
                NO_ABRANGENCIA, 
                SN_ATIVO, 
                QT_PONTOS 
            from 
                TESTES_BLIPY.ABRANGENCIA""")

        # cria as colunas da tabela de saída
        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        # prepara a tabela de saída
        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            # parâmetro de calcula_valor é uma tupla, como só tem um elemento
            # tem que colocar a vírgula no final para construir um objeto do 
            # tipo tupla
            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

    if testes & 2:
        # --------------------------------------
        # caso 2: preencher campos com NULL
        # há duas formas: passando None como função de transformação ou 
        # passando a tupla (None,) para f_copia
        # --------------------------------------

        abrangencia_in.carrega_dados(
                "TESTES_BLIPY.ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"])

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, None)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (None,) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

    if testes & 4:
        # --------------------------------------
        # caso 3: transforma entrada num valor fixo
        # --------------------------------------

        abrangencia_in.carrega_dados(
                "ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
                esquema="TESTES_BLIPY")

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.ValorFixo("*****")), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.ValorFixo(50))
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor()
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor()

            abrangencia_out.grava_registro()

    if testes & 8:
        # --------------------------------------
        # caso 4: de/para (inclusive de S/N para 1/0)
        # --------------------------------------

        abrangencia_in.carrega_dados(
            "ABRANGENCIA", 
            ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
            esquema="TESTES_BLIPY")

        # preparar os de/para
        de_para = { "Teste1": "Alterado pelo de/para",
                    "S"     : "1",
                    "N"     : "0"}
        f_de_para = ft.DePara(de_para, copia_se_nao_encontrado=True)

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, f_de_para), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, f_de_para), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

    if testes & 16:
        # --------------------------------------
        # caso 5: de/para usando classe específica para S/N
        # --------------------------------------

        abrangencia_in.carrega_dados(
            "ABRANGENCIA", 
            ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
            esquema="TESTES_BLIPY")

        # preparar o de/para
        de_para_nome = {    "Teste1": "Teste1 - Alterado pelo de/para",
                            "Teste2": "Teste2 - Alterado pelo de/para"}
        f_de_para_nome = ft.DePara(de_para_nome, copia_se_nao_encontrado=True)

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, f_de_para_nome), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, 
                                                ft.DeParaSN(val_int=False)), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

    if testes & 32:
        # --------------------------------------
        # caso 6: somatório e média
        # --------------------------------------

        abrangencia_in.carrega_dados(
            "ABRANGENCIA", 
            ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
            esquema="TESTES_BLIPY")
        
        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_somatorio)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        # calcula o somatário
        valor_anterior = 0
        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )

            # cada registro é o somatório dele com a soma dos anteriores
            # abrangencia_out.col["pontos"].calcula_valor( (valor_anterior, registro[3]) )
            # valor_anterior = abrangencia_out.col["pontos"].valor

            # cada registro é o somatário dele com a anterior
            abrangencia_out.col["pontos"].calcula_valor( (valor_anterior, registro[3] ))
            valor_anterior = registro[3]

            abrangencia_out.grava_registro()


        # ------------------
        # calcula a média

        abrangencia_in.recarrega_dados()

        # altera a função de transformação para "média"
        abrangencia_out.col["pontos"] = to.Coluna(  "QT_PONTOS", 
                                                    tp.NUMBER, 
                                                    ft.f_media)

        # calcula a média
        valor_anterior = 0
        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )

            # cada registro é a média dele com a anterior
            abrangencia_out.col["pontos"].calcula_valor( (valor_anterior, registro[3] ) )
            valor_anterior = registro[3]

            abrangencia_out.grava_registro()

    if testes & 64:
        # --------------------------------------
        # caso 7: data (e hora) atuais
        # --------------------------------------

        abrangencia_in.carrega_dados(
                "ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
                esquema="TESTES_BLIPY")
        
        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        nr_registro = 0
        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            if nr_registro == 0:
                abrangencia_out.col["data_atualizacao"] = \
                    to.Coluna("DT_ATUALIZACAO", tp.DATE, 
                            ft.Agora(conn))
            elif nr_registro == 1:
                abrangencia_out.col["data_atualizacao"] = \
                    to.Coluna("DT_ATUALIZACAO", tp.DATE, 
                            ft.Agora(conn, so_data=True))
            elif nr_registro == 2:
                abrangencia_out.col["data_atualizacao"] = \
                    to.Coluna("DT_ATUALIZACAO", tp.DATE, 
                            ft.Agora())
            elif nr_registro == 3:
                abrangencia_out.col["data_atualizacao"] = \
                    to.Coluna("DT_ATUALIZACAO", tp.DATE, 
                            ft.Agora(so_data=True))

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )
            abrangencia_out.col["data_atualizacao"].calcula_valor()

            abrangencia_out.grava_registro()

            nr_registro += 1

    if testes & 128:
        # --------------------------------------
        # caso 8: força erro para emitir mensagem formatada
        # --------------------------------------

        #+++++++++++++
        # erro 1
        #+++++++++++++

        abrangencia_in.carrega_dados(
                "ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"], 
                esquema="TESTES_BLIPY")
 #
        de_para = { "Teste1": "Alterado pelo de/para",
                    "S"     : "1",
                    "N"     : "0"}
        f_de_para = ft.DePara(de_para, copia_se_nao_encontrado=True)

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, f_de_para), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, f_de_para), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            try:
                abrangencia_out.col["id"].calcula_valor(     (registro[0],) )

                # código forçando um erro (não poderia haver mais de uma entrada)
                abrangencia_out.col["nome"].calcula_valor(   (registro[1], registro[2]) )

                abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
                abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

                abrangencia_out.grava_registro()

            except:
                e.console._("Erro no master job. Abortando.")
                break


        #+++++++++++++
        # erro 2
        #+++++++++++++

        abrangencia_in.recarrega_dados()

        de_para = { "Teste1": "Alterado pelo de/para",
                    "S"     : "1",
                    "N"     : "0"}
        f_de_para = ft.DePara(de_para, copia_se_nao_encontrado=True)

        col = {
            # código forçando um erro (ainda não há tratamento para tipo BOOL)
            "id"        : to.Coluna("ID_ABRANG", tp.BOOL, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, f_de_para), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, f_de_para), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            try:
                abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
                abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
                abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
                abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

                abrangencia_out.grava_registro()

            except:
                e.console._("Erro no master job. Abortando.")
                break

    if testes & 256:
        # --------------------------------------
        # caso 9: profiling de performance
        # --------------------------------------

        abrangencia_in.carrega_dados(
                "TESTES_BLIPY.ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"])

        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia), 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, None)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        # habilita o profiling de performance
        abrangencia_out.habilita_profiling_performance()

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )
            abrangencia_out.col["ativo"].calcula_valor(  (None,) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

    if testes & 512:
        # --------------------------------------
        # caso 10: trasnformação custom
        # --------------------------------------

        abrangencia_in.carrega_dados(
                "TESTES_BLIPY.ABRANGENCIA", 
                ["ID_ABRANGENCIA", "NO_ABRANGENCIA", "SN_ATIVO", "QT_PONTOS"])

        nome_invertido = to.Coluna("NO_ABRANG", tp.STRING, InverteString())
        nome_copiado   = to.Coluna("NO_ABRANG", tp.STRING, ft.f_copia) 
        col = {
            "id"        : to.Coluna("ID_ABRANG", tp.NUMBER, ft.f_copia), 
            "nome"      : nome_invertido, 
            "ativo"     : to.Coluna("SN_ATIVO",  tp.STRING, ft.f_copia), 
            "pontos"    : to.Coluna("QT_PONTOS", tp.NUMBER, ft.f_copia)
            }

        abrangencia_out = to.TabelaSaida("ZZ_TESTE", col, conn)

        while True:
            registro = abrangencia_in.le_prox_registro()
            if registro is None:
                break

            abrangencia_out.col["id"].calcula_valor(     (registro[0],) )

            if registro[1] == "Teste4":
                col["nome" ] = nome_copiado
            abrangencia_out.col["nome"].calcula_valor(   (registro[1],) )

            abrangencia_out.col["ativo"].calcula_valor(  (registro[2],) )
            abrangencia_out.col["pontos"].calcula_valor( (registro[3],) )

            abrangencia_out.grava_registro()

            if registro[1] == "Teste4":
                col["nome" ] = nome_invertido


class InverteString():
    """
    Inverte uma string de entrada.
    """

    def transforma(self, entradas):
        """
        Inverte a string de entrada.

        Args:
            entradas   : tupla com o valor a string a ser invertida; 
                         só pode haver um elemento na tupla
        Ret:
            string de entrada invertida
        """

        if len(entradas) != 1:
            raise RuntimeError(
                "Não pode haver mais de um dado de entrada.")

        # não funciona pra utf-8!
        return entradas[0][::-1]
