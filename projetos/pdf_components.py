from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime

from projetos.pdf_styles import ThemeColors, get_stylesheet

styles = get_stylesheet()

def format_currency(value):
    try:
        val = float(value)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(value)

# --- Callbacks ---

def on_page_template_project(canvas, doc, title="Plano de Projeto", company="Minha Empresa"):
    canvas.saveState()
    # Separador Header
    canvas.setStrokeColor(ThemeColors.BORDER_LIGHT)
    canvas.setLineWidth(1)
    canvas.line(2*cm, 28*cm, 19*cm, 28*cm)
    
    # Texto Header
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(ThemeColors.PRIMARY)
    canvas.drawString(2*cm, 28.2*cm, title)
    
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(ThemeColors.SUBTEXT)
    canvas.drawRightString(19*cm, 28.2*cm, company)
    
    # Rodapé
    canvas.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
    
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(ThemeColors.SUBTEXT)
    page_num = canvas.getPageNumber()
    canvas.drawString(2*cm, 1.0*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
    # Nota: Numeração total será gerada pelo Canvas customizado
    
    canvas.restoreState()

# --- Componentes ---

def create_paragraph(text, style_name='Normal'):
    return Paragraph(str(text).replace('\n', '<br/>'), styles[style_name])

def create_key_value(key, value):
    """Linha simples Chave: Valor"""
    return Paragraph(f"<b>{key}:</b> {value}", styles['Normal'])

def create_card_highlight(title, content_list, color=ThemeColors.BACKGROUND_LIGHT):
    """Card destaca conteúdo (ex: Impacto, Financeiro)"""
    elements = []
    if title:
        elements.append(Paragraph(title, styles['CardTitle']))
    
    if isinstance(content_list, list):
        elements.extend(content_list)
    else:
        elements.append(Paragraph(str(content_list), styles['Normal']))
        
    table = Table([[elements]], colWidths=[17*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('BOX', (0,0), (-1,-1), 0.5, ThemeColors.BORDER_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    return table

def create_bullet_list(items):
    flowables = []
    for item in items:
        p = Paragraph(f"• {item}", styles['Bullet'])
        flowables.append(p)
    return flowables

def create_section_header(title, icon_char=""):
    """Subtítulo com linha decorativa"""
    # No reportlab padrão não temos icons FontAwesome fácil, usamos texto ou shapes.
    # Vamos usar apenas texto.
    return Paragraph(title, styles['Heading1'])

def create_info_grid(data_dict):
    """Cria grid de informações (ex: Prazo min/max, Custo min/max)"""
    # data_dict = {"Label": "Valor", ...}
    data = []
    row = []
    for k, v in data_dict.items():
        cell = [Paragraph(f"<b>{k}</b>", styles['LabelBold']), Paragraph(str(v), styles['Normal'])]
        row.append(cell)
        if len(row) == 2: # 2 colunas
            data.append(row)
            row = []
    if row:
        row.append(["", ""]) # Padding se ímpar
        data.append(row)
        
    # Estrutura para tabela: preciso de [[cell1, cell2], [cell3, cell4]] mas cell é composto.
    # Correção: Table espera flowables na célula. 
    # Vou criar uma tabela aninhada para cada célula ou apenas usar flowables simples.
    
    # Melhor abordagem: Lista de listas para Table
    table_data = []
    current_row = []
    for k, v in data_dict.items():
        cell_content = [Paragraph(k, styles['LabelBold']), Paragraph(str(v), styles['Normal'])]
        current_row.append(cell_content)
        if len(current_row) == 3: # 3 colunas por linha
            table_data.append(current_row)
            current_row = []
            
    if current_row:
        while len(current_row) < 3:
            current_row.append([])
        table_data.append(current_row)
        
    # Table Principal
    t = Table(table_data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    return t
