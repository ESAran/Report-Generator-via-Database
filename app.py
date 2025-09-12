from src.data_management import DataFrameBuilder
from src.report_generator import CotaCapital
from src.file_management import FileManager
from src.email_sender import EmailSender
from src.log import Logs
import src.global_vars as gv

import os
import time

def main():

    logger = Logs.load_log(__name__)

    start_time = time.time()
    logger.info("Iniciando geração dos extratos de cota capital.")

    # Gerar base de dados
    logger.info("Gerando base de dados consolidada.")
    contas = DataFrameBuilder.create_cota_capital()
    logger.info(f"Base de dados gerada com {len(contas)} registros.")

    # Realiza geração do extratos
    logger.info("Iniciando geração dos PDFs de extrato.")
    CotaCapital.gerar_extratos_mensal(contas)
    logger.info("Geração dos PDFs concluída.")

    # Realiza tratativa nos arquivos
    logger.info("Compactando pastas de extratos.")
    FileManager.zip_all_folders(gv.PATH_BASES)
    logger.info("Compactação concluída.")

    # Mandar os emails
    SMTP_SERVER = gv.SMTP_SERVER
    SMTP_PORT = int(gv.SMTP_PORT)
    SMTP_USERNAME = gv.SMTP_USERNAME
    SMTP_PASSWORD = gv.SMTP_PASSWORD
    EMAIL_FROM = gv.EMAIL_FROM

    logger.info("Preparando envio de e-mail.")
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
        logger.info("E-mail enviado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")

    logger.info("Geração de extratos concluída.")
    logger.info(f"Tempo total de execução: {round(time.time() - start_time)} segundos.")


if __name__ == "__main__":
    main()