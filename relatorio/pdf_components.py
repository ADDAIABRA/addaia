from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, KeepTogether
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime

from .pdf_styles import ThemeColors, get_stylesheet

styles = get_stylesheet()

def format_currency(value):
    """Formata valor float/decimal para BRL."""
    try:
        val = float(value)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(value)

def format_date(date_str):
    """Formata data ISO ou objeto datetime para PT-BR."""
    # Placeholder simples
    if not date_str:
        return datetime.now().strftime("%d/%m/%Y")
    return date_str

# --- Callbacks de Página (Header/Footer) ---

def on_page_template(canvas, doc, title="Relatório de Maturidade", company="Minha Empresa"):
    """
    Função callback para desenhar elementos fixos em todas as páginas.
    Aceita customização básica via closure ou atributos do doc se necessário.
    """
    canvas.saveState()
    
    # --- Cabeçalho ---
    # Linha separadora
    canvas.setStrokeColor(ThemeColors.BORDER_LIGHT)
    canvas.setLineWidth(1)
    # Margens: Left: 2cm, Right: 2cm. Page width A4 = 21cm.
    # width = 21cm - 4cm = 17cm
    canvas.line(2*cm, 28*cm, 19*cm, 28*cm)
    
    # Texto
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(ThemeColors.PRIMARY)
    canvas.drawString(2*cm, 28.2*cm, title)
    
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(ThemeColors.SUBTEXT)
    canvas.drawRightString(19*cm, 28.2*cm, company)
    
    # --- Rodapé ---
    canvas.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
    
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(ThemeColors.SUBTEXT)
    page_num = canvas.getPageNumber()
    canvas.drawString(2*cm, 1.0*cm, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}")
    canvas.drawRightString(19*cm, 1.0*cm, f"Página {page_num}")
    
    canvas.restoreState()

# --- Componentes de Conteúdo (Flowables) ---

def create_spacer(height_cm=0.5):
    return Spacer(1, height_cm * cm)

def create_title(text, style_name='Heading1'):
    return Paragraph(text, styles[style_name])

def create_paragraph(text, style_name='Normal'):
    # Normaliza quebras de linha
    if isinstance(text, str):
        text = text.replace('\n', '<br/>')
    return Paragraph(str(text), styles[style_name])

def create_card_simple(title, content, width_percentage=100):
    """
    Cria uma tabela simples com borda e fundo leve para destacar conteúdo.
    """
    # Conteúdo do card
    elements = []
    if title:
        elements.append(Paragraph(title, styles['CardTitle']))
    
    if isinstance(content, list):
        # Se for lista, assume flowables
        elements.extend(content)
    else:
        # Se for string
        elements.append(Paragraph(str(content), styles['Normal']))
        
    # Table container
    # Largura útil ~17cm.
    col_width = (17 * cm) * (width_percentage / 100)
    
    table = Table([[elements]], colWidths=[col_width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ThemeColors.BACKGROUND_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, ThemeColors.BORDER_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return table

def create_table_data(data_matrix, header_row=True, col_widths=None):
    """
    Cria uma tabela formatada.
    data_matrix: lista de listas de strings ou flowables.
    """
    # Converte strings para Paragraphs para quebrar linha
    processed_data = []
    for row_idx, row in enumerate(data_matrix):
        processed_row = []
        for col_idx, cell in enumerate(row):
            if isinstance(cell, str):
                style = styles['Normal']
                if header_row and row_idx == 0:
                    style = styles['Heading3']
                    # style.alignment = TA_CENTER
                processed_row.append(Paragraph(cell, style))
            else:
                processed_row.append(cell)
        processed_data.append(processed_row)
        
    table = Table(processed_data, colWidths=col_widths)
    
    tbl_style = [
        ('GRID', (0,0), (-1,-1), 0.5, ThemeColors.BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    
    if header_row:
        tbl_style.append(('BACKGROUND', (0,0), (-1,0), ThemeColors.BACKGROUND_LIGHT))
        tbl_style.append(('BOTTOMPADDING', (0,0), (-1,0), 6))
        tbl_style.append(('TOPPADDING', (0,0), (-1,0), 6))
    
    table.setStyle(TableStyle(tbl_style))
    return table

def create_bullet_list(items):
    """Cria uma lista de bullets."""
    flowables = []
    for item in items:
        # Usa BulletChar padrão do ParagraphStyle 'Bullet' ou ListFlowable
        p = Paragraph(item, styles['Bullet'])
        flowables.append(ListFlowable([ListItem(p, bulletColor=ThemeColors.PRIMARY, value='circle')], bulletType='bullet', leftIndent=10))
    # Versão simplificada usando apenas Paragraphs com bullet char visual às vezes é mais estável, 
    # mas ListFlowable é o jeito "correto".
    # Vamos usar ListFlowable com suporte simples.
    
    # Alternativa simples: Paragraphs com bullet
    bullet_list = []
    for item in items:
        bullet_list.append(Paragraph(f"• {item}", styles['Normal']))
    return bullet_list

def create_score_bar(level, max_level=5):
    """
    Retorna uma representação visual (texto ou gráfico simples) do nível.
    Simples: "Nível 3/5 [|||  ]"
    """
    filled = "█" * int(level)
    empty = "░" * (int(max_level) - int(level))
    return Paragraph(f"<font color='{ThemeColors.PRIMARY.hexval()}'>{filled}</font><font color='#cccccc'>{empty}</font> ({level}/{max_level})", styles['Normal'])

def create_pilares_table(pilares_data):
    """
    Gera tabela de pilares.
    Esperado: list of dict {'nome': '...', 'nivel': 3, 'significado': '...'}
    """
    header = ["Pilar", "Nível", "O que significa"]
    rows = [header]
    
    for p in pilares_data:
        rows.append([
            p.get('nome', ''),
            create_score_bar(p.get('nivel', 0)),
            p.get('significado', '')
        ])
    
    # Ajuste de larguras (total ~17cm)
    return create_table_data(rows, col_widths=[4*cm, 4*cm, 9*cm])

def cover_page(data):
    """Gera a capa do relatório."""
    story = []
    story.append(Spacer(1, 4*cm))
    
    # Título Principal
    story.append(Paragraph("Relatório de Maturidade Digital", styles['CoverTitle']))
    
    # Subtítulo (Nome da Empresa)
    empresa = data.get('empresa', {}).get('nome', 'Empresa')
    story.append(Paragraph(empresa, styles['CoverSubtitle']))
    
    story.append(Spacer(1, 1*cm))
    
    # Detalhes
    setor = data.get('empresa', {}).get('setor', 'Setor não informado')
    segmento = data.get('empresa', {}).get('segmento', '')
    
    story.append(Paragraph(f"<b>Setor:</b> {setor}", styles['Normal']))
    if segmento:
        story.append(Paragraph(f"<b>Segmento:</b> {segmento}", styles['Normal']))
        
    story.append(Spacer(1, 2*cm))
    
    # Frase de efeito (opcional)
    frase = data.get('frase_capa', 'Transformando dados em resultados.')
    story.append(Paragraph(frase, styles['Heading2']))
    
    # Quebra de página
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    
    return story
