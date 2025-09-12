from src.data_management import DataFrameBuilder
from src.report_generator import CotaCapital
from src.file_management import FileManager
from src.email_sender import EmailSender
import time
import src.global_vars as gv
from src.log import initialize_logger, get_logger

# BotCity
from botcity.core import DesktopBot
from botcity.maestro import *

BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():

    try:
        # Setups
        maestro = BotMaestroSDK.from_sys_args()
        execution = maestro.get_execution()
        
        # inicializa logger global
        initialize_logger(maestro, execution)
        logger = get_logger()

        start_time = time.time()
        logger.message(__name__, "Iniciando geração dos extratos de cota capital.")

        # Gerar base de dados
        logger.message(__name__, "Gerando base de dados consolidada.")
        contas = DataFrameBuilder.create_cota_capital()
        logger.message(__name__, f"Base de dados gerada com {len(contas)} registros.")

        # Realiza geração do extratos
        logger.message(__name__, "Iniciando geração dos PDFs de extrato.")
        CotaCapital.gerar_extratos_mensal(contas)
        logger.message(__name__, "Geração dos PDFs concluída.")

        # Realiza tratativa nos arquivos
        logger.message(__name__, "Compactando pastas de extratos.")
        FileManager.zip_all_folders(gv.PATH_BASES, delete_original=False)
        logger.message(__name__, "Compactação concluída.")

        # Mandar os emails
        SMTP_SERVER = gv.SMTP_SERVER
        SMTP_PORT = int(gv.SMTP_PORT)
        SMTP_USERNAME = gv.SMTP_USERNAME 
        SMTP_PASSWORD = gv.SMTP_PASSWORD
        EMAIL_FROM = gv.EMAIL_FROM

        logger.message(__name__, "Preparando envio de e-mail.")
        email_sender = EmailSender(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD
        )

        body = email_sender.get_body_format()
        email_to = email_sender.get_email_list_to(contas)
        try:
            email_sender.send_email(email_to, EMAIL_FROM, 'teste extrato', body, True)
            logger.message(__name__, "E-mail enviado com sucesso.")
        except Exception as e:
            logger.message(__name__, f"Erro ao enviar e-mail: {e}")
            maestro.error(task_id=execution.task_id, exception=e)

        logger.message(__name__, "Geração de extratos concluída.")
        logger.message(__name__, f"Tempo total de execução: {round(time.time() - start_time)} segundos.")

        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task Finished OK.",
            total_items=0,
            processed_items=0,
            failed_items=0
        )

    except Exception as e:
        maestro.error(task_id=execution.task_id, exception=e)

if __name__ == "__main__":
    main()
