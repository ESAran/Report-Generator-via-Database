import time, win32com.client

# Este módulo fornece utilitários para automação de operações no Excel via Windows,
# como recarregar consultas de arquivos Excel de forma automática, permitindo rodar
# processos em segundo plano ou de forma visível. Facilita a atualização de dados
# em planilhas sem intervenção manual.

# region DESKTOP
# --------------------------------------------------------------
class DSSheets:

    def windows_excel_refresh_query(path, visible = True):
        '''
        windows_excel_refresh_query():

            - Recarrega a consulta de um arquivo Excel.

            - Requer a passagem por parâmetro do caminho do arquivo e se a operação será visível ou rodada em segundo plano.
        '''
        # Obtém o nome do arquivo Excel
        arquivo = path.split('/')
        arquivo = arquivo[-1]

        # Inicia o Excel
        excel = win32com.client.DispatchEx("Excel.Application")
        
        # Determina se será em segundo plano
        excel.visible = visible

        # Cria o Workbook
        if excel.Workbooks.Count > 0:
            for i in range(1, excel.Workbooks.Count+1):
                if excel.Workbooks.Item(i).Name is arquivo:
                    wb = excel.Workbooks.Item(i)
                    break

        # Abre o arquivo 
        wb = excel.Workbooks.Open(path)

        #Recarrega a A Query
        time.sleep(15)
        wb.RefreshAll()

        # Aguarda até ela finalizar
        excel.CalculateUntilAsyncQueriesDone()

        # Salva e fecha o arquivo
        time.sleep(3)
        wb.Save()
        excel.Quit()
        time.sleep(15)
