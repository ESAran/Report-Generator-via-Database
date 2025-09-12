from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import pandas as pd

# Este módulo fornece a classe EmailSender para envio de e-mails via SMTP,
# com suporte a mensagens em texto ou HTML, além de utilitários para formatação
# de corpo de e-mail e extração de listas de destinatários a partir de DataFrames pandas.

class EmailSender:
    """
    Classe responsável pelo envio de e-mails utilizando SMTP, com suporte a mensagens em texto simples ou HTML.

    Métodos
    -------
    __init__(smtp_server, smtp_port, username, password)
        Inicializa o objeto EmailSender com as configurações do servidor SMTP.
    send_email(to_email, from_email, subject, body, is_html=False)
        Envia um e-mail para o destinatário especificado, podendo ser em formato HTML ou texto simples.
    get_body_format()
        Retorna o corpo padrão do e-mail em HTML, informando sobre a disponibilidade dos extratos de cota capital.

    Exemplo de uso
    --------------
    email_sender = EmailSender(smtp_server, smtp_port, username, password)
    body = email_sender.get_body_format()
    email_sender.send_email('destinatario@dominio.com', 'remetente@dominio.com', 'Assunto', body, True)
    """

    def __init__(self, smtp_server, smtp_port, username, password):
        """
        Inicializa o objeto EmailSender com as configurações do servidor SMTP.

        Parâmetros:
        -----------
        smtp_server : str
            Endereço do servidor SMTP.
        smtp_port : int
            Porta do servidor SMTP.
        username : str
            Nome de usuário para autenticação SMTP.
        password : str
            Senha para autenticação SMTP.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_email, from_email, subject, body, is_html=False):
        """
        Envia um e-mail para o destinatário especificado.

        Parâmetros:
        -----------
        to_email : str
            E-mail do destinatário.
        from_email : str
            E-mail do remetente.
        subject : str
            Assunto do e-mail.
        body : str
            Corpo do e-mail (texto simples ou HTML).
        is_html : bool, opcional
            Define se o corpo do e-mail será enviado como HTML (padrão: False).
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            # Permite múltiplos destinatários, separados por vírgula
            if isinstance(to_email, list):
                msg['To'] = ', '.join(to_email)
                recipients = to_email
            else:
                msg['To'] = to_email
                recipients = [to_email]

            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(from_email, recipients, msg.as_string())
        except Exception as e:
            raise

    @staticmethod
    def get_body_format():
        """
        Retorna o corpo padrão do e-mail em HTML, informando sobre a disponibilidade dos extratos de cota capital.

        Retorna:
        --------
        str
            Corpo do e-mail em formato HTML.
        """
        mensagem_final = (
            "Os extratos de cota capital das contas das administradoras já estão disponíveis na pasta da sua agência no <i>One Drive.</i><br>"
            "Por favor, acesse a respectiva pasta para consultar os documentos." \
        )

        # return f"""
        # <html>
        #     <body>
        #     <h2>Extratos de Cota Capital de Condomínios já disponíveis</h2>
        #     <p>{mensagem_final}</p>
        #     <p>Para eventuais dúvidas, favor contatar <i>{os.getenv("EMAIL_USER_DUVIDA")}</i>.</p>
        #     <br>
        #     <p>Atenciosamente,<br>
        #     <br>
        #     Área de Desenvolvimento de Sistemas</p>
        #     </body>
        # </html>
        # """
        return f"""
        <html>
            <body>
            <h2>Extratos de Cota Capital de Condomínios já disponíveis</h2>
            <p>{mensagem_final}</p>
            <p>Para eventuais dúvidas, favor contatar <i>{'Contatos'}</i>.</p>
            <br>
            <p>Atenciosamente,<br>
            <br>
            Área de Desenvolvimento de Sistemas</p>
            </body>
        </html>
        """

    @staticmethod
    def get_email_list_to(df: pd.DataFrame) -> list:
        """
        Retorna uma lista de e-mails extraídos de um DataFrame, separando múltiplos e-mails em uma mesma célula.

        Parâmetros:
        -----------
        df : pd.DataFrame
            DataFrame contendo uma coluna 'email' com os endereços de e-mail.

        Retorna:
        --------
        list
            Lista de e-mails extraídos do DataFrame.
        """
        if 'email' not in df.columns:
            raise ValueError("O DataFrame deve conter uma coluna 'email'.")

        emails = []
        for cell in df['email'].dropna():
            # Divide por ';' ou ',' e remove espaços extras
            for email in str(cell).replace(';', ',').split(','):
                email = email.strip()
                if email:
                    emails.append(email)
        # Remove duplicados mantendo a ordem
        seen = set()
        unique_emails = []
        for email in emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        return unique_emails

# if __name__ == "__main__":

#     # SMTP_SERVER = os.getenv("SMTP_SERVER")
#     # SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
#     # SMTP_USERNAME = os.getenv("SMTP_USERNAME")
#     # SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
#     # EMAIL_FROM = os.getenv("EMAIL_FROM")

#     email_sender = EmailSender(
#         smtp_server=SMTP_SERVER,
#         smtp_port=SMTP_PORT,
#         username=SMTP_USERNAME,
#         password=SMTP_PASSWORD
#     )

#     body = email_sender.get_body_format()
#     email_sender.send_email('eduardo_aran@sicredi.com.br', EMAIL_FROM, 'teste extrato', body, True)