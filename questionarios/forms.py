from django import forms
from .models import (
    PilarQuestionario,
    PerguntaQuestionario,
    RespostaPergunta,
    RespostaQuestionario,
    AvaliacaoMaturidade
)

class RespostaPilarForm(forms.Form):
    """
    Formulário dinâmico para responder as perguntas de um pilar específico.
    As perguntas são carregadas do banco de dados com base no pilar fornecido.
    """
    def __init__(self, pilar, *args, **kwargs):
        self.pilar = pilar
        super().__init__(*args, **kwargs)
        
        # Busca todas as perguntas ativas deste pilar
        perguntas = PerguntaQuestionario.objects.filter(pilar=pilar, ativo=True).order_by('ordem')
        
        for pergunta in perguntas:
            choices = [
                ('a', f"A) {pergunta.alternativa_a}"),
                ('b', f"B) {pergunta.alternativa_b}"),
                ('c', f"C) {pergunta.alternativa_c}"),
                ('d', f"D) {pergunta.alternativa_d}"),
                ('e', f"E) {pergunta.alternativa_e}"),
            ]
            
            field_name = f'pergunta_{pergunta.id}'
            self.fields[field_name] = forms.ChoiceField(
                label=pergunta.enunciado,
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True,
                help_text=pergunta.codigo
            )

    def save(self, avaliacao):
        """
        Salva as respostas e calcula a pontuação do pilar.
        """
        # 1. Obter ou criar a RespostaQuestionario (o pilar na avaliação)
        resposta_pilar, _ = RespostaQuestionario.objects.get_or_create(
            avaliacao=avaliacao,
            pilar=self.pilar
        )
        
        total_pontos = 0
        mapa_pontos = {'a': 0, 'b': 25, 'c': 50, 'd': 75, 'e': 100}
        perguntas_respondidas = 0
        
        # 2. Salvar cada resposta individual
        for field_name, escolha in self.cleaned_data.items():
            if field_name.startswith('pergunta_'):
                pergunta_id = field_name.split('_')[1]
                pergunta = PerguntaQuestionario.objects.get(id=pergunta_id)
                pontos = mapa_pontos.get(escolha, 0)
                
                RespostaPergunta.objects.update_or_create(
                    resposta_questionario=resposta_pilar,
                    pergunta=pergunta,
                    defaults={
                        'alternativa_escolhida': escolha,
                        'pontuacao': pontos
                    }
                )
                total_pontos += pontos
                perguntas_respondidas += 1
        
        # 3. Calcular e atualizar a média do pilar
        if perguntas_respondidas > 0:
            media = total_pontos / perguntas_respondidas
            resposta_pilar.pontuacao_pilar = media
            
            # Definir estágio do pilar
            if media <= 25:
                resposta_pilar.estagio_pilar = RespostaQuestionario.Estagio.INICIAL
            elif media <= 55:
                resposta_pilar.estagio_pilar = RespostaQuestionario.Estagio.EM_EVOLUCAO
            elif media <= 80:
                resposta_pilar.estagio_pilar = RespostaQuestionario.Estagio.ESTRUTURADO
            else:
                resposta_pilar.estagio_pilar = RespostaQuestionario.Estagio.AVANCADO
                
            resposta_pilar.save()
            
            # Recalcular resultados globais da avaliação
            avaliacao.calcular_resultados()
            
        return resposta_pilar

class AvaliacaoMaturidadeForm(forms.ModelForm):
    """
    Formulário básico para criar/editar a Avaliação (cabeçalho).
    """
    class Meta:
        model = AvaliacaoMaturidade
        fields = ['perfil_empresa', 'titulo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'perfil_empresa': forms.Select(attrs={'class': 'form-control'}),
        }
