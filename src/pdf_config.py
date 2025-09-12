from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


# pdf_config.py
# Este arquivo define um dicionário de configuração padrão para geração de arquivos PDF utilizando a biblioteca ReportLab.
# As configurações incluem tamanhos de página, fontes, cores, margens, espaçamentos e outros parâmetros visuais.
# Essas definições centralizam e padronizam o estilo dos PDFs gerados no projeto, facilitando manutenção e reutilização.

PDF_CONFIG = {
    "pagesize": A4,
    "title_font": ("Courier-Bold", 13),
    "semititle_font": ("Courier-Bold", 6.5),
    "title_color": colors.HexColor("#000000"),
    "line_color": colors.HexColor("#000000"),
    "line_width": 0.3,
    "body_font": ("Courier", 6.5),
    "header_font": ("Courier", 6.5),
    "header_color": colors.black,
    "body_color": colors.black,
    "footer_font": ("Courier-Oblique", 9),
    "footer_color": colors.grey,
    "margin_left": 50,
    "margin_right": 50,
    "margin_top": 90,
    "line_spacing": 10,
    "line_spacing2" : 15,
    "line_spacing_line" : 5,
    "footer_y": 30,
    "block_spacing": 50,
    "text_space_s" : "                                      ",
    "text_space_b" : "                                                                              "
}