from src.data_management import DataFrameBuilder
from reportlab.pdfgen import canvas

from src.pdf_config import PDF_CONFIG
from src.log import Logs

import pandas as pd
import os
import time
import json
from datetime import datetime, timedelta
import src.global_vars as gvars

# Este módulo fornece a classe CotaCapital para geração de extratos de cota capital em PDF,
# utilizando dados de contas e administradoras. Permite criar relatórios detalhados ou simplificados,
# organizando os arquivos em pastas por agência e administradora, com layout customizado via ReportLab.
# Inclui métodos para formatação de informações, agrupamento por agência, controle de logs e
# integração com DataFrames pandas para automatizar o processo de geração dos extratos mensais.

logger = Logs.load_log(__name__)
class CotaCapital():
    """
    Classe responsável pela geração dos extratos de cota capital em PDF para contas de administradoras.
    Utiliza o ReportLab para formatação e criação dos arquivos, organizando-os em pastas por agência e administradora.

    Métodos
    -------
    gerar_extratos_mensal(accounts: pd.DataFrame)
        Gera os extratos mensais em PDF para cada conta presente no DataFrame.
    gerar_pdf(pdf_filename, row, PDF_CONFIG, base_dir)
        Cria e salva o PDF do extrato detalhado de uma conta, incluindo movimentações.
    gerar_pdf2(pdf_filename, row, PDF_CONFIG, base_dir)
        Cria e salva um PDF de extrato simplificado para uma conta.
    """

    @staticmethod
    def gerar_extratos_mensal(accounts: pd.DataFrame):
        """
        Gera os extratos mensais em PDF para cada conta do DataFrame fornecido.
        Os arquivos são salvos em pastas organizadas por agência e administradora.

        Parâmetros:
        -----------
        accounts : pd.DataFrame
            DataFrame contendo os dados das contas e administradoras para geração dos extratos.
        """
        for _, row in accounts.iterrows():
            # Obtém o diretório base a partir da variável de ambiente PATH_BASES
            path_bases = gvars.PATH_BASES
            agencia = str(int(float(row['agência']))).zfill(2)
            # Monta o caminho: PATH_BASES/UAXX/Extratos de Cota Capital
            pasta_agencia = f"UA{agencia}"
            pdf_dir = os.path.join(
            path_bases,
            pasta_agencia,
            "Extratos de Cota Capital", # Extratos de Cota Capital",
            row['administradora']
            )
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = os.path.join(pdf_dir, f"{row['conta']}.pdf")

            CotaCapital.gerar_pdf(pdf_filename, row, PDF_CONFIG, pasta_agencia)

            # Agrupamento para log por agência e administradora
            if not hasattr(CotaCapital, "_contas_por_agencia"):
                CotaCapital._contas_por_agencia = {}

            agencia_key = agencia
            admin_key = row['administradora']

            if agencia_key not in CotaCapital._contas_por_agencia:
                CotaCapital._contas_por_agencia[agencia_key] = {}

            if admin_key not in CotaCapital._contas_por_agencia[agencia_key]:
                CotaCapital._contas_por_agencia[agencia_key][admin_key] = 0

            CotaCapital._contas_por_agencia[agencia_key][admin_key] += 1

            # Após o loop, faça o log (apenas uma vez)
            if _ == accounts.index[-1]:
                for ag, admins in CotaCapital._contas_por_agencia.items():
                    total = sum(admins.values())
                    admins_str = ", ".join([f"{adm}: {qtd}" for adm, qtd in admins.items()])
                    logger.info(f"Agência {ag}: {total} contas geradas. ({admins_str})")

    @staticmethod
    def gerar_pdf(pdf_filename, row, PDF_CONFIG, base_dir):
        """
        Cria e salva o PDF do extrato detalhado de uma conta, incluindo cabeçalho, dados do associado,
        movimentações mensais, saldo anterior, saldo atual e informações de ouvidoria.

        Parâmetros:
        -----------
        pdf_filename : str
            Caminho completo do arquivo PDF a ser gerado.
        row : pd.Series
            Linha do DataFrame com os dados da conta e movimentações.
        PDF_CONFIG : dict
            Dicionário com as configurações de layout e estilos do PDF.
        base_dir : str
            Diretório base do projeto para localização de recursos (ex: imagem de fundo).
        """
        c = canvas.Canvas(pdf_filename, pagesize=PDF_CONFIG["pagesize"])
        width, height = PDF_CONFIG["pagesize"]

        # Imagem background (ajustada para cobrir toda a folha A4)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(base_dir, "data", "img", "background.png")
        c.drawImage(
            bg_path,
            0, 0,
            width=width,
            height=height,
            preserveAspectRatio=True,
            mask='auto'
        )

        # Linha separadora
        y = height - PDF_CONFIG["margin_top"]
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.setDash(3, 3)
        #c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        c.setDash()

        # Cabeçalho
        y -= PDF_CONFIG["line_spacing"]
        c.setFont(*PDF_CONFIG["header_font"])
        c.setFillColor(PDF_CONFIG["header_color"])
        c.drawString(PDF_CONFIG["margin_left"], y, "NOME_EMPRESA - EXTRATO DE CONTA CAPITAL")

        y -= PDF_CONFIG["line_spacing"]
        c.setFont(*PDF_CONFIG["header_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        conta_str = str(row['conta']).zfill(10)
        c.drawString(PDF_CONFIG["margin_left"], y, f"ASSOCIADO...: {conta_str} - {row['nome']}")

        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"ENDERECO....: {row['endereco_completo']}")

        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"CIDADE......: {row['municipio']} - SC")
    
        y -= PDF_CONFIG["line_spacing"]
        # Calcula o período: do primeiro ao último dia do mês anterior à data de emissão

        data_emissao = pd.to_datetime(row['data_emissao'], dayfirst=True)
        primeiro_dia_mes_anterior = (data_emissao.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
        ultimo_dia_mes_anterior = (data_emissao.replace(day=1) - pd.DateOffset(days=1))

        periodo_str = f"{primeiro_dia_mes_anterior:%d/%m/%Y} a {ultimo_dia_mes_anterior:%d/%m/%Y}"
        text = "{:<30}{:>90}".format(
            f"PERIODO.....: {periodo_str}", f"EMISSAO: {row['data_emissao']}"
        )
        c.drawString(PDF_CONFIG["margin_left"], y, text)

        # Linha separadora
        y -= PDF_CONFIG["line_spacing_line"]
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.setDash(3, 3)
        #c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        c.setDash()

        # # Linha separadora pontilhada
        # y -= PDF_CONFIG["line_spacing"]
        # c.setStrokeColor(PDF_CONFIG["line_color"])
        # c.setLineWidth(PDF_CONFIG["line_width"])
        # c.setDash(3, 3)  # Define o padrão pontilhado: 3 pontos preenchidos, 3 vazios
        # c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        # c.setDash()  # Reseta para linha contínua para não afetar outras linhas

        # Movimentações em formato de texto
        y -= PDF_CONFIG["line_spacing"]
        c.setFont(*PDF_CONFIG["body_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        header = "{:<30}{:<40}{:>17}{:>17}{:>23}".format(
            "DATA", "HISTORICO", "DEBITO", "CREDITO", "SALDO (R$)"
        )
        c.drawString(PDF_CONFIG["margin_left"], y, header)

        # Linha separadora pontilhada
        y -= PDF_CONFIG["line_spacing"]
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.setDash(3, 3)  # Define o padrão pontilhado: 3 pontos preenchidos, 3 vazios
        c.line(PDF_CONFIG["margin_left"], y + 5, width - PDF_CONFIG["margin_left"], y + 5)
        c.setDash()  # Reseta para linha contínua para não afetar outras linhas

        # movimentações
        y -= PDF_CONFIG["line_spacing_line"]
        capital_social = float(row['capital_social'])
        movimentacao = float(row['movimentacao'])
        saldo_anterior = capital_social - movimentacao
        valor_saldo_mov = saldo_anterior
        saldo_anterior_str = f"{saldo_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        first_line = "{:<30}{:<40}{:>17}{:>17}{:>23}".format(
            "", "SALDO ANTERIOR", "", "", saldo_anterior_str
        )
        c.drawString(PDF_CONFIG["margin_left"], y, first_line)

        movimentacoes = row.get('tipo_valor_data_movimentacao', [])
        if isinstance(movimentacoes, str):
            movimentacoes = json.loads(movimentacoes)

        if movimentacoes:
            y -= PDF_CONFIG["line_spacing"]
            c.setFont(*PDF_CONFIG["body_font"])
            for mov in movimentacoes:
                data = mov['data_transacao']
                tipo = mov['tipo_movimento']
                valor = mov['valor_transacao']  # ou mov.get('valor_transacao')
                # Agora você pode usar data, tipo e valor normalmente
                try:
                    valor_float = float(valor)
                except Exception:
                    valor_float = 0.0
                
                valor_saldo_mov = valor_saldo_mov + valor_float
                valor_saldo_str = f"{valor_saldo_mov:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                mov_line = "{:<30}{:<40}{:>17}{:>17}{:>23}".format(
                f"{data}", f"{tipo}", "", f"{valor}", f"{valor_saldo_str}"
                )
                c.drawString(PDF_CONFIG["margin_left"], y, mov_line)
                y -= PDF_CONFIG["line_spacing"]
        else:
            y -= PDF_CONFIG["line_spacing"]
            # Centraliza a mensagem na página
            msg = "NENHUMA MOVIMENTACAO REGISTRADA NESTE MES."
            mov_line = "{:<30}{:<42}{:>15}{:>17}{:>23}".format(
            "", f"{msg}", "", "", ""
            )
            c.drawString(PDF_CONFIG["margin_left"], y, mov_line)

        # Saldo final
        # Linha separadora pontilhada
        y -= PDF_CONFIG["line_spacing_line"]
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.setDash(3, 3)  # Define o padrão pontilhado: 3 pontos preenchidos, 3 vazios
        c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
        c.setDash()  # Reseta para linha contínua para não afetar outras linhas

        # Movimentações em formato de texto
        y -= PDF_CONFIG["line_spacing"]
        c.setFont(*PDF_CONFIG["body_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        valor_saldo_final = f"{float(row['capital_social']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        resumo = "{:<30}{:<40}{:>17}{:<17}{:>23}".format(
            "", "", "", "SALDO ATUAL (R$):", f"{valor_saldo_final}"
        )
        c.drawString(PDF_CONFIG["margin_left"], y, resumo)

        # Linha separadora pontilhada
        y -= PDF_CONFIG["line_spacing"]
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.setDash(3, 3)  # Define o padrão pontilhado: 3 pontos preenchidos, 3 vazios
        c.line(PDF_CONFIG["margin_left"], y + 5, width - PDF_CONFIG["margin_left"], y + 5)
        c.setDash()  # Reseta para linha contínua para não afetar outras linhas

        # ouvidoria
        y -= PDF_CONFIG["line_spacing_line"]
        c.setFont(*PDF_CONFIG["body_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        ouvidoria = gvars.OUVIDORIA_SICREDI
        
        # Centraliza exatamente a string na página, independente do tamanho
        ouvidoria_text = f'Ouvidoria NOME_EMPRESA - {ouvidoria}'
        text_width = c.stringWidth(ouvidoria_text, *PDF_CONFIG["body_font"])
        c.drawString((width - text_width) / 2, y, ouvidoria_text)

        # Rodapé
        c.setFont(*PDF_CONFIG["footer_font"])
        c.setFillColor(PDF_CONFIG["footer_color"])
        c.drawRightString(width - PDF_CONFIG["margin_left"], PDF_CONFIG["footer_y"], f"Sicredi Vale Litoral - SC")

        c.save()

    @staticmethod
    def gerar_pdf2(pdf_filename, row, PDF_CONFIG, base_dir):
        """
        Cria e salva um PDF de extrato simplificado para uma conta, com informações centrais e layout reduzido.

        Parâmetros:
        -----------
        pdf_filename : str
            Caminho completo do arquivo PDF a ser gerado.
        row : pd.Series
            Linha do DataFrame com os dados da conta.
        PDF_CONFIG : dict
            Dicionário com as configurações de layout e estilos do PDF.
        base_dir : str
            Diretório base do projeto para localização de recursos (ex: imagem de fundo).
        """
        c = canvas.Canvas(pdf_filename, pagesize=PDF_CONFIG["pagesize"])
        width, height = PDF_CONFIG["pagesize"]

        # Imagem background (ajustada para cobrir toda a folha A4)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(base_dir, "data", "img", "background.png")
        c.drawImage(
            bg_path,
            0, 0,
            width=width,
            height=height,
            preserveAspectRatio=True,
            mask='auto'
        )

        # Título
        c.setFont(*PDF_CONFIG["title_font"])
        c.setFillColor(PDF_CONFIG["title_color"])
        c.drawCentredString(width / 2, height - PDF_CONFIG["margin_top"] -5, f"{row['nome']}")

        # Linha separadora
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.line(PDF_CONFIG["margin_left"], height - PDF_CONFIG["margin_top"] - 10, width - PDF_CONFIG["margin_left"], height - PDF_CONFIG["margin_top"] - 10)

        # Cabeçalho
        y = height - PDF_CONFIG["margin_top"] - 30
        c.setFont(*PDF_CONFIG["header_font"])
        c.setFillColor(PDF_CONFIG["header_color"])
        c.drawString(PDF_CONFIG["margin_left"], y, "NOME_EMPRESA - EXTRATO DE CONTA CAPITAL")

        y -= PDF_CONFIG["line_spacing"]
        c.setFont(*PDF_CONFIG["header_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        c.drawString(PDF_CONFIG["margin_left"], y, f"ASSOCIADO: {row['nome']}")

        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"ENDEREÇO: {row['endereco_completo']}")

        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"CIDADE: {row['municipio']} - SC")
        
        # Linha separadora
        y -= PDF_CONFIG["line_spacing"] - 5
        c.setStrokeColor(PDF_CONFIG["line_color"])
        c.setLineWidth(PDF_CONFIG["line_width"])
        c.line(PDF_CONFIG["margin_left"], y, width - PDF_CONFIG["margin_left"], y)
    
        # Semi titulo centralizado
        y = height / 2 + 170
        c.setFont(*PDF_CONFIG["semititle_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        c.drawString(PDF_CONFIG["margin_left"], y, "Relatório de Cota Capital:")

        # Dados centralizados
        c.setFont(*PDF_CONFIG["body_font"])
        c.setFillColor(PDF_CONFIG["body_color"])
        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"Número da Conta: {row['conta']}")
        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"Saldo: R$ {row['capital_social']}")
        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"Movimentação mensal: {row['movimentacao']}")
        y -= PDF_CONFIG["line_spacing"]
        c.drawString(PDF_CONFIG["margin_left"], y, f"Data de Emissão: {row['data_emissao']}")

        # Rodapé
        c.setFont(*PDF_CONFIG["footer_font"])
        c.setFillColor(PDF_CONFIG["footer_color"])
        c.drawRightString(width - PDF_CONFIG["margin_left"], PDF_CONFIG["footer_y"], f"Sicredi Vale Litoral - SC")

        c.save()

if __name__ == "__main__":
    start_time = time.time()
    contas = DataFrameBuilder.create_cota_capital()
    CotaCapital.gerar_extratos_mensal(contas)
    end_time = time.time()
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")