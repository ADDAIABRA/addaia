from reportlab.lib.colors import HexColor   
from reportlab.lib.styles import StyleSheet1, ParagraphStyle    
from reportlab.lib.enums import TA_LEFT, TA_CENTER 
from reportlab.pdfbase.ttfonts import TTFont    
from reportlab.pdfbase import pdfmetrics    

# --- Cores e Identidade ---    
class ThemeColors:  
    # Paleta Projetos (mais vibrante/ação)  
    PRIMARY = HexColor("#2C3E50")      # Azul Escuro/Cinza  
    SECONDARY = HexColor("#18BC9C")    # Verde Turquesa (Ação/Positive)  
    ACCENT = HexColor("#F39C12")       # Laranja (Destaque/Atenção) 
      
    # Neutros   
    TEXT = HexColor("#2C3E50")  
    SUBTEXT = HexColor("#7F8C8D")   
    BACKGROUND_LIGHT = HexColor("#F8F9FA")  
    BORDER_LIGHT = HexColor("#ECF0F1")  
    WHITE = HexColor("#FFFFFF") 
      
    # Semânticos    
    SUCCESS = HexColor("#27AE60")   
    WARNING = HexColor("#E67E22")   
    DANGER = HexColor("#E74C3C")    

# --- Registro de Fontes ---    
def register_fonts():   
    # Fallback para Helvetica   
    return "Helvetica", "Helvetica-Bold"    

# --- Estilos do Documento ---  
def get_stylesheet():   
    styles = StyleSheet1()  
    font_regular, font_bold = register_fonts()  
      
    # Estilo Base 
    styles.add(ParagraphStyle(  
        name='Normal',  
        fontName=font_regular,  
        fontSize=10,    
        leading=14, 
        textColor=ThemeColors.TEXT, 
        alignment=TA_LEFT,  
        spaceAfter=6    
    ))  
      
    # Título do Projeto (Grande)    
    styles.add(ParagraphStyle(  
        name='ProjectTitle',    
        parent=styles['Normal'],    
        fontName=font_bold, 
        fontSize=20,    
        leading=24, 
        textColor=ThemeColors.PRIMARY,  
        spaceAfter=4    
    ))  
      
    # Área/Categoria (Badge style text) 
    styles.add(ParagraphStyle(  
        name='ProjectArea', 
        parent=styles['Normal'],    
        fontName=font_bold, 
        fontSize=10,    
        textColor=ThemeColors.SECONDARY,    
        spaceAfter=12   
    ))  
      
    # H1    
    styles.add(ParagraphStyle(  
        name='Heading1',    
        parent=styles['Normal'],    
        fontName=font_bold, 
        fontSize=14,    
        leading=18, 
        textColor=ThemeColors.PRIMARY,  
        spaceBefore=12, 
        spaceAfter=6,   
        keepWithNext=True   
    ))  
      
    # Label Bolt (ex: "Prazo:", "Custo:")   
    styles.add(ParagraphStyle(  
        name='LabelBold',   
        parent=styles['Normal'],    
        fontName=font_bold, 
        fontSize=10,    
        textColor=ThemeColors.PRIMARY   
    ))  
      
    # Card Title  
    styles.add(ParagraphStyle(  
        name='CardTitle',   
        parent=styles['Normal'],    
        fontName=font_bold, 
        fontSize=11,    
        leading=13, 
        textColor=ThemeColors.PRIMARY,  
        spaceAfter=4    
    ))

    # Lista
    styles.add(ParagraphStyle(
        name='Bullet',
        parent=styles['Normal'],
        leftIndent=10,
        spaceAfter=2
    ))
      
    return styles
