from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer, KeepTogether, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from projetos.pdf_styles import ThemeColors, get_stylesheet

styles = get_stylesheet()
from projetos.pdf_components import (
    on_page_template_project, create_paragraph, create_section_header,
    create_bullet_list, create_card_highlight, create_info_grid,
    format_currency
)

class NumberedCanvasProject(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(ThemeColors.SUBTEXT)
        text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(19*cm, 1.0*cm, text)
        self.restoreState()

def generate_project_pdf(project_data, output_path, logo_path=None):
    """
    Gera PDF para um único projeto.
    project_data: dicionário com os campos do modelo Projeto + 'empresa_nome'.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.0*cm,
        rightMargin=2.0*cm,
        topMargin=2.5*cm,
        bottomMargin=2.0*cm,
        title=f"Projeto: {project_data.get('nome_projeto')}"
    )
    
    story = []
    
    # 1. Cabeçalho do Projeto
    story.append(create_paragraph(project_data.get('area', 'Geral'), 'ProjectArea'))
    story.append(create_paragraph(project_data.get('nome_projeto', 'Sem Nome'), 'ProjectTitle'))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(create_paragraph(project_data.get('descricao', ''), 'Normal'))
    story.append(Spacer(1, 0.5*cm))
    
    # 2. Resumo Executivo (Objetivos e Problema)
    story.append(create_card_highlight("Resumo Estratégico", [
        create_paragraph(f"<b>Objetivo Principal:</b> {project_data.get('objetivo_principal', '-')}", 'Normal'),
        Spacer(1, 0.2*cm),
        create_paragraph(f"<b>Problema Resolvido:</b> {project_data.get('problema', '-')}", 'Normal'),
        Spacer(1, 0.2*cm),
        create_paragraph(f"<b>Causa Raiz:</b> {project_data.get('causa_raiz', '-')}", 'Normal'),
        Spacer(1, 0.2*cm),
        create_paragraph(f"<b>Impacto do Problema:</b> {project_data.get('impacto_do_problema', '-')}", 'Normal'),
        Spacer(1, 0.2*cm),
        create_paragraph(f"<b>Público Impactado:</b> {project_data.get('publico_impactado', '-')}", 'Normal')
    ]))
    story.append(Spacer(1, 0.5*cm))
    
    # 3. Solução Detalhada
    story.append(create_section_header("Solução Proposta"))
    story.append(create_paragraph(project_data.get('solucao', ''), 'Normal'))
    
    if project_data.get('beneficios'):
        story.append(Spacer(1, 0.3*cm))
        story.append(create_paragraph("<b>Benefícios Esperados:</b>", 'LabelBold'))
        story.extend(create_bullet_list(project_data.get('beneficios', [])))
    
    story.append(Spacer(1, 0.5*cm))
    
    # 4. Dados Financeiros e Prazos (Grid)
    story.append(create_section_header("Estimativas de Execução"))
    
    # Formata valores
    p_min = project_data.get('prazo_minimo', 0)
    p_max = project_data.get('prazo_maximo', 0)
    p_est = project_data.get('prazo_estimado', 0)
    
    v_min = format_currency(project_data.get('preco_minimo', 0))
    v_max = format_currency(project_data.get('preco_maximo', 0))
    v_est = format_currency(project_data.get('preco_estimado', 0))
    
    estimates = {
        "Prazo Mínimo": f"{p_min} semanas",
        "Prazo Máximo": f"{p_max} semanas",
        "Prazo Recomendado": f"{p_est} semanas",
        "Investimento Mín.": v_min,
        "Investimento Máx.": v_max,
        "Investimento Médio": v_est
    }
    
    story.append(create_info_grid(estimates))
    story.append(Spacer(1, 0.5*cm))
    
    # 5. Impactos (Card)
    story.append(KeepTogether([
        create_section_header("Matriz de Impacto"),
        create_card_highlight("", [
            create_paragraph(f"<b>Operacional:</b> {project_data.get('impacto_operacional', '-')}", 'Normal'),
            Spacer(1, 0.2*cm),
            create_paragraph(f"<b>Financeiro:</b> {project_data.get('impacto_financeiro', '-')}", 'Normal'),
            Spacer(1, 0.2*cm),
            create_paragraph(f"<b>Tempo:</b> {project_data.get('impacto_tempo', '-')}", 'Normal')
        ], color=ThemeColors.BACKGROUND_LIGHT)
    ]))
    
    story.append(PageBreak())
    
    # 6. Cronograma e Entregas (Lado a Lado logicamente, mas sequencial no PDF)
    story.append(create_section_header("Cronograma de Fases"))
    phases = project_data.get('fases_projeto', [])
    if phases:
        for idx, phase in enumerate(phases, 1):
            story.append(create_paragraph(f"<b>Fase {idx}:</b> {phase}", 'Normal'))
            story.append(Spacer(1, 0.2*cm))
    else:
        story.append(create_paragraph("Não definido.", 'Normal'))
        
    story.append(Spacer(1, 0.5*cm))
    
    story.append(create_section_header("Entregáveis"))
    entregas = project_data.get('entregaveis', [])
    if entregas:
        story.extend(create_bullet_list(entregas))
    else:
        story.append(create_paragraph("Não definido.", 'Normal'))
        
    story.append(Spacer(1, 0.5*cm))
    
    # 7. Riscos e KPIs
    story.append(create_section_header("Indicadores de Sucesso (KPIs)"))
    kpis = project_data.get('indicadores_chave', [])
    if kpis:
        story.extend(create_bullet_list(kpis))
        
    story.append(Spacer(1, 0.5*cm))
    
    story.append(create_section_header("Riscos e Mitigação"))
    riscos = project_data.get('riscos', [])
    mitig = project_data.get('mitigacao_riscos', [])
    
    # Combina riscos e mitigação se possível
    if riscos:
        for i, r in enumerate(riscos):
            m = mitig[i] if i < len(mitig) else "N/A"
            story.append(create_paragraph(f"<b>Risco:</b> {r}", 'Normal'))
            story.append(create_paragraph(f"<i>Mitigação:</i> {m}", 'Normal'))
            story.append(Spacer(1, 0.2*cm))

    # 7.5 Dados Necessários e Futuro
    story.append(create_section_header("Preparação e Evolução"))
    story.append(create_paragraph("<b>Dados Necessários para Início:</b>", 'LabelBold'))
    story.extend(create_bullet_list(project_data.get('dados_necessarios', [])))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(create_paragraph("<b>Possíveis Casos de Uso Futuros:</b>", 'LabelBold'))
    story.extend(create_bullet_list(project_data.get('casos_uso_futuros', [])))

    # 8. Rodapé / Vantagem
    story.append(Spacer(1, 1*cm))
    story.append(create_card_highlight("Vantagem Competitiva", 
        [create_paragraph(project_data.get('vantagem_competitiva', ''), 'Normal')],
        color='#fff6e6' # Tom amarelado claro
    ))

    # Build
    def footer_callback(canvas, doc):
        on_page_template_project(canvas, doc, 
            title=f"Projeto: {project_data.get('nome_projeto')}",
            company=project_data.get('empresa_nome', ''))

    doc.build(story, onFirstPage=footer_callback, onLaterPages=footer_callback, canvasmaker=NumberedCanvasProject)
    return output_path

def generate_projects_summary_pdf(projects_list, output_path, empresa_nome="", logo_path=None):
    """
    Gera um PDF resumo com todos os projetos (formato cards).
    projects_list: lista de dicionários/objetos de projeto.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.0*cm,
        rightMargin=2.0*cm,
        topMargin=2.5*cm,
        bottomMargin=2.0*cm,
        title="Roadmap de Projetos Estratégicos"
    )
    
    story = []
    
    # Título do Relatório
    story.append(create_paragraph("Roadmap de Projetos Estratégicos", 'ProjectTitle'))
    story.append(create_paragraph(f"Portfólio de iniciativas para {empresa_nome}", 'Normal'))
    story.append(Spacer(1, 1*cm))
    
    for proj in projects_list:
        # Pega dados se for objeto ou dict
        p_name = proj.nome_projeto if hasattr(proj, 'nome_projeto') else proj.get('nome_projeto', 'Sem Nome')
        p_area = proj.area if hasattr(proj, 'area') else proj.get('area', 'Geral')
        p_desc = proj.descricao if hasattr(proj, 'descricao') else proj.get('descricao', '')
        p_obj = proj.objetivo_principal if hasattr(proj, 'objetivo_principal') else proj.get('objetivo_principal', '-')
        p_prazo = proj.prazo_estimado if hasattr(proj, 'prazo_estimado') else proj.get('prazo_estimado', 0)
        p_invest = proj.preco_estimado if hasattr(proj, 'preco_estimado') else proj.get('preco_estimado', 0)
        
        # Cria card resumo
        card_content = [
            Paragraph(f"<b>Área:</b> {p_area}", styles['Normal']),
            Spacer(1, 0.1*cm),
            Paragraph(str(p_desc), styles['Normal']),
            Spacer(1, 0.3*cm),
            Paragraph(f"<b>Objetivo:</b> {p_obj}", styles['Normal']),
            Spacer(1, 0.2*cm),
            Paragraph(f"<b>Prazo Est.:</b> {p_prazo} semanas | <b>Investimento Est.:</b> {format_currency(p_invest)}", styles['Normal']),
        ]
        
        story.append(KeepTogether([
            create_card_highlight(p_name, card_content),
            Spacer(1, 0.8*cm)
        ]))

    def footer_callback(canvas, doc):
        on_page_template_project(canvas, doc, 
            title="Roadmap de Projetos Estratégicos",
            company=empresa_nome)

    doc.build(story, onFirstPage=footer_callback, onLaterPages=footer_callback, canvasmaker=NumberedCanvasProject)
    return output_path

if __name__ == "__main__":
    # Teste
    sample_proj = {
        'empresa_nome': 'Tech Corp',
        'area': 'Data Science',
        'nome_projeto': 'Previsão de Demanda com IA',
        'descricao': 'Implementação de modelo preditivo para otimizar estoques.',
        'objetivo_principal': 'Reduzir ruptura em 30%.',
        'problema': 'Falta de produtos.',
        'causa_raiz': 'Planejamento manual.',
        'solucao': 'Modelo XGBoost treinado com histórico de vendas.',
        'beneficios': ['Menor custo estoque', 'Maior venda'],
        'prazo_minimo': 4, 'prazo_maximo': 8, 'prazo_estimado': 6,
        'preco_minimo': 10000, 'preco_maximo': 20000, 'preco_estimado': 15000,
        'impacto_operacional': 'Alto', 'impacto_financeiro': 'Alto', 'impacto_tempo': 'Médio',
        'fases_projeto': ['Coleta dados', 'Treino', 'Deploy'],
        'entregaveis': ['Dataset', 'API', 'Dashboard'],
        'indicadores_chave': ['Acurácia', 'Ruptura'],
        'riscos': ['Dados sujos'], 'mitigacao_riscos': ['Limpeza prévia'],
        'vantagem_competitiva': 'Precisão no atendimento.'
    }
    generate_project_pdf(sample_proj, "projeto_teste.pdf")
