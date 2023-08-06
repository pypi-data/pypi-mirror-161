import blipy.planilha as planilha


## Teste 01 __________________________________________
def teste_01(param_io, param_sheet_name):
    print('Teste 01')
    print('Execução básica - print de registros da tabela.')
    print()

    p = planilha.Planilha()
    p.carrega_dados(io=param_io, sheet_name=param_sheet_name)

    for i in range(25):
        r = p.le_prox_registro()
        print(r)


    print()
    print('Fim teste 01')


# Teste 02 __________________________________________
def teste_02(param_io, param_sheet_name):
    print('Teste 02')
    print('Duas execuções conseguintes.\n'
          'Entre a primeira e a segunda é executada a função recarrega_dados()')
    print()

    p = planilha.Planilha()
    p.carrega_dados(io=param_io, sheet_name=param_sheet_name)

    for i in range(25):
        r = p.le_prox_registro()
        print(r)

    p.recarrega_dados()
    print()
    print('Nova execução pós chamada da função recarrega_dados()')

    print()
    for i in range(25):
        r = p.le_prox_registro()
        print(r)

    print()
    print('Fim teste 02')


## Teste 03 __________________________________________
def teste_03(param_io, param_sheet_name):
    print('Teste 03')
    print('Teste erro - Dicionario sem parametro io.')
    print()

    p = planilha.Planilha()
    p.carrega_dados(io=param_io, sheet_name=param_sheet_name)

    print()
    print('Fim teste 03')


## Teste 04 __________________________________________
def teste_04(param_io, param_sheet_name, param_engine):
    print('Teste 04')
    print('Teste erro - Formato do arquivo de extensão .xlsx e engine diferente de openpyxl.')
    print()

    p = planilha.Planilha()
    p.carrega_dados(io=param_io, sheet_name=param_sheet_name, engine=param_engine)

    print()
    print('Fim teste 04')


## Teste 05 __________________________________________
def teste_05(param_io, param_sheet_name, param_engine):
    print('Teste 05')
    print("Teste erro - Formato do arquivo de extensão .xls e engine diferente de xlrd.")
    print()

    p = planilha.Planilha()
    p.carrega_dados(io=param_io, sheet_name=param_sheet_name, engine=param_engine)

    print()
    print('Fim teste 05')

