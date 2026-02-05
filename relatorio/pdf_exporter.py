import os
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .pdf_styles import ThemeColors
from .pdf_components import on_page_template
from .render_templates import (
    render_template_basico,
    render_template_intermediario,
    render_template_avancado
)

# --- Canvas Customizado para "Página X de Y" ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Adiciona o número de página em cada página salva."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Chama o template padrão para desenhar header/bg
        # Note: on_page_template desenha apenas a página atual.
        # Precisamos redesenhar o rodapé aqui para ter o "de Y".
        
        # Desenha Header/Footer base (sem numeração)
        # Como o on_page_template já desenha numeração simples, 
        # vamos sobrescrever ou adaptar. 
        # Para simplificar, vou desenhar manualmente aqui o "X de Y".
        
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(ThemeColors.SUBTEXT)
        
        # Posição do rodapé
        from reportlab.lib.units import cm
        text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(19*cm, 1.0*cm, text)
        self.restoreState()

# --- Função Principal ---

def generate_pdf(report_data, output_path, template="basico", logo_path=None):
    """
    Gera o relatório em PDF.
    
    Args:
        report_data (dict): Dados do relatório.
        output_path (str): Caminho final do arquivo.
        template (str): 'basico', 'intermediario', 'avancado'.
        logo_path (str, optional): Caminho para imagem de logo.
    """
    
    # 1. Configurar Documento
    # Margens: Top/Bottom um pouco maiores para Header/Footer
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.0*10*2.83465/10, # 2.0cm ~= 56.7pt
        rightMargin=2.0*28.35, # 28.35 pt = 1cm
        topMargin=2.5*28.35,   # Maior para caber Header
        bottomMargin=2.0*28.35,
        title="Relatório de Maturidade"
    )
    
    # ReportLab usa pontos (pt). 1cm = 28.35pt.
    doc.leftMargin = 2.0 * 28.35
    doc.rightMargin = 2.0 * 28.35
    doc.topMargin = 2.5 * 28.35
    doc.bottomMargin = 2.5 * 28.35
    
    # 2. Construir História (Flowables)
    story = []
    
    if template == "basico":
        render_template_basico(story, report_data)
    elif template == "intermediario":
        render_template_intermediario(story, report_data)
    elif template == "avancado":
        render_template_avancado(story, report_data)
    else:
        raise ValueError(f"Template desconhecido: {template}")

    # 3. Gerar PDF
    # Usamos o NumberedCanvas para paginação "X de Y"
    # Passamos on_page_template para elementos fixos (exceto numeração que o canvas sobrescreve)
    
    def footer_callback(canvas, doc):
        on_page_template(canvas, doc, title=report_data.get('titulo', 'Relatório de Maturidade'), 
                         company=report_data.get('empresa', {}).get('nome', ''))

    doc.build(story, onFirstPage=footer_callback, onLaterPages=footer_callback, canvasmaker=NumberedCanvas)
    
    print(f"PDF gerado com sucesso: {output_path}")
    return output_path

# --- Main para Teste ---

if __name__ == "__main__":
    # Dados de Exemplo
    
    sample_basico = {
        'empresa': {'nome': 'Tech Solutions Ltda', 'setor': 'Tecnologia', 'segmento': 'SaaS B2B'},
        'sumario_executivo': {
            'estagio': 'Inicial', 'gargalo': 'Processos Manuais', 
            'oportunidade': 'Automação RPA', 'risco': 'Perda de Dados'
        },
        'contexto': {'funcionarios': '10-50', 'faturamento': 'R$ 5M'},
        'pilares': [
            {'nome': 'Cultura', 'nivel': 2, 'significado': 'Conscientização iniciada'},
            {'nome': 'Dados', 'nivel': 1, 'significado': 'Dados descentralizados'},
        ],
        'dores': ['Lentidão no fechamento', 'Erros manuais em planilhas'],
        'recomendacoes': [
            {'titulo': 'Centralizar Dados', 'descricao': 'Criar Data Lake único.'},
            {'titulo': 'Automatizar NFs', 'descricao': 'Implementar robô de leitura de notas.'}
        ],
        'plano_30_dias': {
            'semana_1': ['Mapear processos', 'Definir acessos'],
            'semana_2': 'Contratar ferramenta X'
        }
    }
    
    generate_pdf(sample_basico, "exemplo_basico.pdf", "basico")
