from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# --- Cores e Identidade ---
class ThemeColors:
    # Paleta Padrão
    PRIMARY = HexColor("#1F4E79")      # Azul Sóbrio
    SECONDARY = HexColor("#2E75B6")    # Azul Intermediário
    ACCENT = HexColor("#00A389")       # Verde Discreto (ou #F5A623 Amarelo)
    
    # Neutros
    TEXT = HexColor("#111111")
    SUBTEXT = HexColor("#666666")
    BACKGROUND_LIGHT = HexColor("#EFEFEF")
    BORDER_LIGHT = HexColor("#DDDDDD")
    WHITE = HexColor("#FFFFFF")
    
    # Semânticos (opcional)
    SUCCESS = HexColor("#28a745")
    WARNING = HexColor("#ffc107")
    DANGER = HexColor("#dc3545")

# --- Registro de Fontes ---
def register_fonts():
    """
    Tenta registrar fontes personalizadas (Inter/Source Sans 3).
    Se não encontrar, fallback para Helvetica (padrão do PDF).
    """
    # Exemplo de tentativa de registro:
    # try:
    #     pdfmetrics.registerFont(TTFont('Inter-Regular', 'Inter-Regular.ttf'))
    #     pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-Bold.ttf'))
    #     return "Inter-Regular", "Inter-Bold"
    # except:
    #     pass
    
    # Fallback padrão
    return "Helvetica", "Helvetica-Bold"

# --- Estilos do Documento ---
def get_stylesheet():
    """Retorna o objeto StyleSheet1 configurado com a hierarquia tipográfica."""
    styles = StyleSheet1()
    
    font_regular, font_bold = register_fonts()
    
    # Estilo Base
    styles.add(ParagraphStyle(
        name='Normal',
        fontName=font_regular,
        fontSize=11,
        leading=15,
        textColor=ThemeColors.TEXT,
        alignment=TA_LEFT,
        spaceAfter=6
    ))
    
    # Título da Capa
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=26,
        leading=30,
        textColor=ThemeColors.PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=12
    ))
    
    # Subtítulo da Capa
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        leading=18,
        textColor=ThemeColors.SUBTEXT,
        alignment=TA_LEFT,
        spaceAfter=24
    ))
    
    # Título de Seção (H1)
    styles.add(ParagraphStyle(
        name='Heading1',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=16,
        leading=20,
        textColor=ThemeColors.PRIMARY,
        spaceBefore=18,
        spaceAfter=12,
        keepWithNext=True
    ))
    
    # Subtítulo de Seção (H2)
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Normal'],
        fontName=font_bold, # ou semibold se disponível
        fontSize=13,
        leading=16,
        textColor=ThemeColors.SECONDARY,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    ))
    
    # H3
    styles.add(ParagraphStyle(
        name='Heading3',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        leading=14,
        textColor=ThemeColors.TEXT,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    ))
    
    # Texto Pequeno (Legendas, Notas)
    styles.add(ParagraphStyle(
        name='Small',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=ThemeColors.SUBTEXT
    ))
    
    # Lista (Bullets)
    styles.add(ParagraphStyle(
        name='Bullet',
        parent=styles['Normal'],
        bulletFontName=font_bold,
        bulletFontSize=11,
        leftIndent=15,
        firstLineIndent=0,
        spaceAfter=4
    ))

    # Título do Card
    styles.add(ParagraphStyle(
        name='CardTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        leading=13,
        textColor=ThemeColors.PRIMARY,
        spaceAfter=4
    ))
    
    # Centralizado
    styles.add(ParagraphStyle(
        name='Centered',
        parent=styles['Normal'],
        alignment=TA_CENTER
    ))
    
    return styles
