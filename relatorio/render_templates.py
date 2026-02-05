from reportlab.platypus import PageBreak, KeepTogether, Paragraph, Spacer
from .pdf_components import (
    cover_page, create_title, create_paragraph, create_spacer, 
    create_card_simple, create_table_data, create_bullet_list, 
    create_pilares_table, format_currency, styles
)
from reportlab.lib.units import cm

def get_safe(data, path, default=None):
    """Helper para acessar dados aninhados com segurança."""
    keys = path.split('.')
    current = data
    for k in keys:
        if isinstance(current, dict):
            current = current.get(k, {})
        else:
            return default
    return current if current else default

# --- Template Básico ---
def render_template_basico(story, data):
    # 1. Capa
    story.extend(cover_page(data))
    
    # 1.5 Destaques Estratégicos
    story.append(create_title("Destaques Estratégicos"))
    destaques = data.get('destaques_estrategicos', {})
    d_rows = [
        [Paragraph("<b>Diagnóstico do nível atual</b><br/><font size='9' color='#666666'>Entenda sua maturidade digital hoje.</font>", styles['Normal']), destaques.get('diagnostico_nivel_atual', '-')],
        [Paragraph("<b>Identificação de gargalos</b><br/><font size='9' color='#666666'>Onde você está perdendo dinheiro e tempo.</font>", styles['Normal']), destaques.get('identificacao_gargalos', '-')],
        [Paragraph("<b>Foco estratégico</b><br/><font size='9' color='#666666'>O que você não deve priorizar agora.</font>", styles['Normal']), destaques.get('foco_estrategico', '-')],
        [Paragraph("<b>Próximos passos</b><br/><font size='9' color='#666666'>Um plano claro e prático para execução imediata.</font>", styles['Normal']), destaques.get('proximos_passos', '-')],
    ]
    story.append(create_table_data(d_rows, header_row=False, col_widths=[6*cm, 11*cm]))
    story.append(create_spacer())
    story.append(create_title("Sumário Executivo"))
    exec_sum = data.get('sumario_executivo', {})
    
    rows = [
        [Paragraph("<b>Estágio Atual:</b>", styles['Normal']), exec_sum.get('estagio', '-')],
        [Paragraph("<b>Principal Gargalo:</b>", styles['Normal']), exec_sum.get('gargalo', '-')],
        [Paragraph("<b>Oportunidade:</b>", styles['Normal']), exec_sum.get('oportunidade', '-')],
        [Paragraph("<b>Risco Imediato:</b>", styles['Normal']), exec_sum.get('risco', '-')]
    ]
    story.append(create_table_data(rows, header_row=False, col_widths=[4*cm, 13*cm]))
    story.append(create_spacer())
    
    # 3. Contexto Considerado
    contexto = data.get('contexto', {})
    story.append(create_title("Contexto", "Heading2"))
    ctx_rows = [["Item", "Detalhe"]]
    for k, v in contexto.items():
        ctx_rows.append([k.replace('_', ' ').capitalize(), str(v)])
    story.append(create_table_data(ctx_rows, col_widths=[5*cm, 12*cm]))
    story.append(create_spacer())
    
    # 4. Avaliação de Maturidade
    story.append(create_title("Avaliação de Maturidade"))
    pilares = data.get('pilares', [])
    story.append(create_pilares_table(pilares))
    story.append(create_spacer())
    story.append(PageBreak())
    
    # 5. Dores Identificadas
    story.append(create_title("Dores Identificadas"))
    dores = data.get('dores', [])
    story.extend(create_bullet_list(dores))
    story.append(create_spacer())
    
    # 6. Recomendações Prioritárias
    story.append(create_title("Recomendações Prioritárias"))
    recs = data.get('recomendacoes', [])
    for rec in recs:
        # Tenta pegar título e descrição ou string direta
        title = rec.get('titulo', 'Recomendação') if isinstance(rec, dict) else 'Ação Recomendada'
        desc = rec.get('descricao', str(rec)) if isinstance(rec, dict) else str(rec)
        card = create_card_simple(title, desc)
        story.append(KeepTogether([card, create_spacer(0.3)]))
    
    story.append(PageBreak())
    
    # 7. Plano de 30 Dias
    story.append(create_title("Plano de Ação - 30 Dias"))
    plano = data.get('plano_30_dias', {})
    
    for semana, tarefas in plano.items():
        story.append(create_paragraph(f"<b>{semana.replace('_', ' ').upper()}</b>", "Heading3"))
        if isinstance(tarefas, list):
            story.extend(create_bullet_list(tarefas))
        else:
            story.append(create_paragraph(str(tarefas)))
        story.append(create_spacer(0.3))
            
    # Notas Finais
    story.append(create_spacer(2))
    story.append(create_paragraph("Este relatório foi gerado automaticamente baseando-se nas respostas fornecidas.", "Small"))


# --- Template Intermediário ---
def render_template_intermediario(story, data):
    # 1. Capa
    story.extend(cover_page(data))
    
    # 1.5 Destaques Estratégicos
    story.append(create_title("Destaques Estratégicos"))
    destaques = data.get('destaques_estrategicos', {})
    d_rows = [
        [Paragraph("<b>Diagnóstico do nível atual</b><br/><font size='9' color='#666666'>Entenda sua maturidade digital hoje.</font>", styles['Normal']), destaques.get('diagnostico_nivel_atual', '-')],
        [Paragraph("<b>Identificação de gargalos</b><br/><font size='9' color='#666666'>Onde você está perdendo dinheiro e tempo.</font>", styles['Normal']), destaques.get('identificacao_gargalos', '-')],
        [Paragraph("<b>Foco estratégico</b><br/><font size='9' color='#666666'>O que você não deve priorizar agora.</font>", styles['Normal']), destaques.get('foco_estrategico', '-')],
        [Paragraph("<b>Próximos passos</b><br/><font size='9' color='#666666'>Um plano claro e prático para execução imediata.</font>", styles['Normal']), destaques.get('proximos_passos', '-')],
    ]
    story.append(create_table_data(d_rows, header_row=False, col_widths=[6*cm, 11*cm]))
    story.append(create_spacer())
    story.append(create_title("Visão Estratégica"))
    sumario = data.get('sumario_executivo', {})
    story.append(create_paragraph(sumario.get('texto_geral', 'Resumo da análise realizada.'), "Normal"))
    story.append(create_spacer())
    
    # Top 3 Prioridades
    story.append(create_paragraph("Top 3 Prioridades:", "Heading3"))
    prioridades = sumario.get('prioridades', [])
    story.extend(create_bullet_list(prioridades))
    story.append(create_spacer())
    
    # 3. Avaliação Detalhada por Pilar
    story.append(create_title("Diagnóstico Detalhado"))
    pilares = data.get('pilares', [])
    
    for p in pilares:
        # Bloco de cada pilar
        p_content = []
        p_content.append(Paragraph(f"{p.get('nome', '?')} (Nível {p.get('nivel', 0)})", styles['Heading2']))
        p_content.append(Paragraph(f"<b>O que falta:</b> {p.get('lacunas', '-')}", styles['Normal']))
        p_content.append(Paragraph(f"<b>Dependências:</b> {p.get('dependencias', '-')}", styles['Normal']))
        story.append(KeepTogether(p_content))
        story.append(create_spacer(0.5))
        
    story.append(PageBreak())
    
    # 4. Matriz Impacto x Esforço (Conceitual)
    story.append(create_title("Matriz de Priorização"))
    matriz = data.get('matriz_priorizacao', {})
    
    # Tabela 2x2 simulando a matriz
    # Q1: Quick Wins (Alta Imp, Baixo Esf) | Q2: Estratégicos (Alta Imp, Alto Esf)
    # Q3: Irrelevantes (Baixa Im, Baixo Esf) | Q4: Evitar (Baixa Imp, Alto Esf)
    
    q1 = "<br/>".join([f"• {x}" for x in matriz.get('quick_wins', [])])
    q2 = "<br/>".join([f"• {x}" for x in matriz.get('estrategicos', [])])
    
    rows = [
        [Paragraph("<b>Ganhos Rápidos (Alta Relevância, Baixo Esforço)</b>", styles['Heading3']), 
         Paragraph("<b>Estratégicos (Alta Relevância, Alto Esforço)</b>", styles['Heading3'])],
        [Paragraph(q1, styles['Normal']), Paragraph(q2, styles['Normal'])]
    ]
    
    story.append(create_table_data(rows, header_row=False, col_widths=[8.5*cm, 8.5*cm]))
    story.append(create_spacer())
    
    # 5. Roadmap 90 Dias
    story.append(create_title("Roadmap de 90 Dias"))
    roadmap = data.get('roadmap_90_dias', {}) # list of stages
    
    for fase in roadmap:
        title = fase.get('fase', 'Etapa')
        items = fase.get('entregas', [])
        content = [Paragraph("<b>Entregas:</b>", styles['Normal'])]
        if items:
            content.extend(create_bullet_list(items))
        
        card = create_card_simple(title, content)
        story.append(KeepTogether([card, create_spacer(0.5)]))
        
    story.append(PageBreak())
    
    # 6. Projetos Recomendados
    story.append(create_title("Portfólio de Projetos"))
    projetos = data.get('projetos', [])
    
    for proj in projetos:
        nome = proj.get('nome', 'Projeto')
        desc = proj.get('descricao', '')
        kp = proj.get('kpi', '-')
        
        texto = f"{desc}<br/><br/><b>KPI Principal:</b> {kp}"
        story.append(create_card_simple(nome, texto))
        story.append(create_spacer(0.5))


# --- Template Avançado ---
def render_template_avancado(story, data):
    # 1. Capa
    story.extend(cover_page(data))
    
    # 1.5 Destaques Estratégicos
    story.append(create_title("Destaques Estratégicos"))
    destaques = data.get('destaques_estrategicos', {})
    d_rows = [
        [Paragraph("<b>Diagnóstico do nível atual</b><br/><font size='9' color='#666666'>Entenda sua maturidade digital hoje.</font>", styles['Normal']), destaques.get('diagnostico_nivel_atual', '-')],
        [Paragraph("<b>Identificação de gargalos</b><br/><font size='9' color='#666666'>Onde você está perdendo dinheiro e tempo.</font>", styles['Normal']), destaques.get('identificacao_gargalos', '-')],
        [Paragraph("<b>Foco estratégico</b><br/><font size='9' color='#666666'>O que você não deve priorizar agora.</font>", styles['Normal']), destaques.get('foco_estrategico', '-')],
        [Paragraph("<b>Próximos passos</b><br/><font size='9' color='#666666'>Um plano claro e prático para execução imediata.</font>", styles['Normal']), destaques.get('proximos_passos', '-')],
    ]
    story.append(create_table_data(d_rows, header_row=False, col_widths=[6*cm, 11*cm]))
    story.append(create_spacer())
    story.append(create_title("Sumário Executivo (C-Level)"))
    exec_text = data.get('sumario_c_level', 'Análise aprofundada da maturidade digital e prontidão para IA.')
    story.append(create_paragraph(exec_text))
    story.append(create_spacer())
    
    # Tabela de Riscos de Negócio
    riscos = data.get('riscos_negocio', [])
    if riscos:
        story.append(create_title("Riscos e Mitigações", "Heading2"))
        r_rows = [["Risco", "Impacto", "Mitigação"]]
        for r in riscos:
            r_rows.append([r.get('risco'), r.get('impacto'), r.get('mitigacao')])
        story.append(create_table_data(r_rows, col_widths=[5*cm, 4*cm, 8*cm]))
    
    story.append(PageBreak())
    
    # 3. Diagnóstico e Arquitetura
    story.append(create_title("Arquitetura de Dados Alvo"))
    arq = data.get('arquitetura', {})
    
    principles = arq.get('principios', [])
    story.append(create_paragraph("<b>Princípios Norteadores:</b>", "Heading3"))
    story.extend(create_bullet_list(principles))
    story.append(create_spacer())
    
    camadas = arq.get('camadas', [])
    for camada in camadas:
        story.append(create_card_simple(camada.get('nome'), camada.get('descricao')))
        story.append(create_spacer(0.3))
        
    story.append(PageBreak())
    
    # 4. Roadmap 12 Meses (Trimestral)
    story.append(create_title("Plano Estratégico (12 Meses)"))
    roadmap = data.get('roadmap_anual', {}) # Dict T1, T2, T3, T4
    
    for trim, actions in roadmap.items():
        story.append(create_paragraph(f"<b>{trim}</b>", "Heading2"))
        story.extend(create_bullet_list(actions))
        story.append(create_spacer(0.5))
        
    story.append(create_spacer())
    
    # 5. Governança
    story.append(create_title("Framework de Governança"))
    gov = data.get('governanca', {})
    story.append(create_paragraph(gov.get('modelo', 'Modelo federado de governança.')))
    story.append(create_spacer())
    
    # Notas Finais
    story.append(create_spacer(2))
    story.append(create_paragraph("Relatório Confidencial - Uso Interno", "Small"))
