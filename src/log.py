import logging
import os

#imports necessários no arquivo da classe, pode ser alocado no navigations.py

# Em todos os outros arquivos que usarão log, deve ser chamada a função no início:
# LOGGER = Logs.load_log(__name__)

# Caso tenha mais de um arquivo de log, necessário especificar:
# LOGGER = Logs.load_log(__name__, "main")

# Recomendações de registro:
# LOGGER.info("informação geral")
# LOGGER.warning("aviso simples")
# LOGGER.error("erro pesado")


class Logs:
    @staticmethod
    def load_log(name: str, log: str = "logs/specific", minimal_level: str = "debug") -> logging.Logger:
        '''
        name - nome do logger: opcional, não usado na formatação pq (filename) é mais bonito
        log - arquivo do log: opcional, especificar quando houver mais de um log
        minimal_level - nivel mínimo de log registrado: "info" não registrará .debug, apenas .info pra cima
        '''

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, minimal_level.upper(), logging.INFO))

        if not logger.handlers:
            if not os.path.exists("logs"):
                os.makedirs("logs")
            log_path = f"{log}.log"
            file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger

