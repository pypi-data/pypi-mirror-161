
"""
Helper para o profiling de programas.
"""

import time
import inspect

class ProfilingPerformance():
    """
    Classe mix-in para profiling da performance do código.

    Grava o tempo gasto entre o início e o fim da contagem de acordo com a
    configuração feita no método configura_profiling.
    """

    # <atributos de classe>

    # guarda a contagem de quantos profilings estão sendo realizados, para
    # fechar o arquivo de profiling quando o última profiling for destruído
    __qtd_profilings = 0

    # planilha onde serão gravados os dados de profiling coletados
    __planilha = None

    def __del__(self):
        # se for a última instância de profiling sendo desruída, fecha a
        # planilha de saída
        if self._profiling_on:
            ProfilingPerformance.__qtd_profilings -= 1

            if ProfilingPerformance.__qtd_profilings == 0:
                ProfilingPerformance.__planilha.close()

    def habilita_profiling_performance(self, path_csv=""):
        """
        Habilita o registro da performance de execução. O resultado do profiling
        será gravado na planilha 'performance.csv'.

        Args:
            path_csv : caminho onde deverá ser salva a planilha. Se não
                       informado, será salva no diretório atual
            
        """

        if ProfilingPerformance.__qtd_profilings == 0:
            # TODO: acrescentar path (que é um saco!)
            try:
                ProfilingPerformance.__planilha = open("performance.csv", "a")
                # escreve uma linha em branco para separar os registros entre
                # uma sessão de profiling e outra
                ProfilingPerformance.__planilha.write(
                        "Funcao;" 
                        "Objeto;"
                        "Tempo em segundos\n")
            except Exception as err:
                raise SystemExit(err)

        ProfilingPerformance.__qtd_profilings += 1
        self._profiling_on = True

    def _inicia_timer(self):
        """
        Inicia o contador de tempo.
        """

        self.__inicio = time.perf_counter()

    def _finaliza_timer(self):
        """
        Calcula o tempo despendido.
        """
        duracao = time.perf_counter() - self.__inicio
        self.__grava_resultado(duracao)

    def __grava_resultado(self, duracao):
        #  pega o nome do método para o qual está sendo realizado o profiling
        funcao = inspect.stack()[2].function

        ProfilingPerformance.__planilha.write(
                funcao + ";" + \
                str(self) + ";" +  \
                ("%10.10f" % duracao).replace(".", ",") + "\n")

