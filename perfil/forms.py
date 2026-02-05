from django import forms
from .models import (
    PerfilEmpresa,
    CanalAquisicaoCliente,
    SistemaUtilizado,
    ObjetivoProximo12Meses,
    RestricaoCritica,
    PerfilEmpresaCanaisAquisicao,
    PerfilEmpresaSistemasUtilizados,
    PerfilEmpresaObjetivos,
    PerfilEmpresaRestricoes,
)

from .constants import SETORES_SEGMENTOS, DEFAULT_SEGMENTS

class PerfilEmpresaForm(forms.ModelForm):
    """
    Formulário para o Perfil da Empresa.
    Inclui campos de múltipla escolha para gerenciar as relações N:N personalizadas.
    """
    
    segmento_especifico = forms.ChoiceField(
        label="Segmento específico",
        required=True,
        help_text="Lista dinâmica com base no setor selecionado.",
    )

    # Campos de múltipla escolha manuais (tabelas de ligação personalizadas)
    canais_aquisicao_selecionados = forms.ModelMultipleChoiceField(
        queryset=CanalAquisicaoCliente.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Canais de Aquisição de Clientes",
        help_text="Quais canais sua empresa utiliza para atrair clientes?"
    )
    
    sistemas_utilizados_selecionados = forms.ModelMultipleChoiceField(
        queryset=SistemaUtilizado.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Sistemas Utilizados Atualmente",
        help_text="Quais ferramentas e softwares fazem parte do dia a dia?"
    )
    
    objetivos_selecionados = forms.ModelMultipleChoiceField(
        queryset=ObjetivoProximo12Meses.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Objetivos para os Próximos 12 meses",
        help_text="O que é prioridade para o futuro do negócio?"
    )
    
    restricoes_selecionadas = forms.ModelMultipleChoiceField(
        queryset=RestricaoCritica.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Restrições e Desafios Críticos",
        help_text="Quais obstáculos mais atrapalham a operação hoje?"
    )

    class Meta:
        model = PerfilEmpresa
        # Excluímos o usuário pois ele será injetado pela view (request.user)
        exclude = ('usuario',)
        
        # Widgets para estilização e placeholders
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'placeholder': 'Nome da Empresa'}),
            'pais': forms.TextInput(attrs={'placeholder': 'Ex: Brasil'}),
            'segmento_especifico': forms.Select(), # Agora é ChoiceField via __init__, mas garantimos widget
            'meses_pico': forms.TextInput(attrs={'placeholder': 'Ex: Jan, Dez'}),
            'estado': forms.Select(),
            'cidade': forms.Select(),
            
            # Campos com < 7 escolhas -> RadioSelect
            'fase_negocio': forms.RadioSelect(),
            'faixa_ano_fundacao': forms.RadioSelect(),
            'faixa_funcionarios': forms.RadioSelect(),
            'decisao_estrategica': forms.RadioSelect(),
            'responsavel_tecnologia_processos': forms.RadioSelect(),
            'regime_tributario': forms.RadioSelect(),
            'tipo_receita_predominante': forms.RadioSelect(),
            'ticket_medio_venda': forms.RadioSelect(),
            'principal_canal_vendas': forms.RadioSelect(),
            'estrutura_operacional': forms.RadioSelect(),
            'quantidade_unidades': forms.RadioSelect(),
            'abrangencia_geografica': forms.RadioSelect(),
            'sazonalidade_negocio': forms.RadioSelect(),
            'possui_equipe_ti_dados': forms.RadioSelect(),
            'alfabetizacao_digital_equipe': forms.RadioSelect(),
            'ferramentas_gestao': forms.RadioSelect(),
            'residencia_dados': forms.RadioSelect(),
            'prioridade_estrategica_ano': forms.RadioSelect(),
            'conformidade_lgpd': forms.RadioSelect(),
            'preferencia_entrega_recomendacoes': forms.RadioSelect(),

            # Campos adicionais (add_to_class)
            'setor_outro': forms.TextInput(attrs={'placeholder': 'Descreva seu setor se marcou Outro'}),
            'cargo_outro': forms.TextInput(attrs={'placeholder': 'Descreva seu cargo se marcou Outro'}),
            'segmento_outro': forms.TextInput(attrs={'placeholder': 'Descreva seu segmento se marcou Outro'}),
            'sistemas_outros': forms.TextInput(attrs={'placeholder': 'Outros sistemas não listados'}),
            'tipo_volume_mensal': forms.TextInput(attrs={'placeholder': 'Ex: Pedidos, Atendimentos'}),
            'faixa_volume_mensal': forms.TextInput(attrs={'placeholder': 'Ex: 0-100, 101-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # População dinâmica de segmentos com base no setor atual ou default
        # Priorizamos o valor do POST (data) se houver, caso contrário o da instância
        setor_atual = None
        if self.data and 'setor_atuacao' in self.data:
            setor_atual = self.data.get('setor_atuacao')
        elif self.instance and self.instance.pk:
            setor_atual = self.instance.setor_atuacao
        
        self.fields['segmento_especifico'].choices = [('', '---------')] + SETORES_SEGMENTOS.get(setor_atual, DEFAULT_SEGMENTS)

        # Aplicamos classes CSS e organizamos os campos
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'custom-control-input'
            else:
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_class} form-control".strip()
        
        # Se for uma edição, carregamos os valores das relações N:N
        if self.instance.pk:
            self.fields['canais_aquisicao_selecionados'].initial = list(self.instance.canais_aquisicao.values_list('canal_aquisicao', flat=True))
            self.fields['sistemas_utilizados_selecionados'].initial = list(self.instance.sistemas_utilizados.values_list('sistema_utilizado', flat=True))
            self.fields['objetivos_selecionados'].initial = list(self.instance.objetivos_12_meses.values_list('objetivo', flat=True))
            self.fields['restricoes_selecionadas'].initial = list(self.instance.restricoes_criticas.values_list('restricao', flat=True))

    def save(self, commit=True):
        """
        Sobrescreve o salvamento para processar as tabelas de ligação personalizadas.
        """
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            self._save_custom_m2m(instance)
            
        return instance

    def _save_custom_m2m(self, instance):
        """
        Sincroniza as escolhas de múltipla escolha com as tabelas de ligação.
        """
        # Canais de Aquisição
        if 'canais_aquisicao_selecionados' in self.cleaned_data:
            instance.canais_aquisicao.all().delete()
            for obj in self.cleaned_data['canais_aquisicao_selecionados']:
                PerfilEmpresaCanaisAquisicao.objects.create(perfil_empresa=instance, canal_aquisicao=obj)
        
        # Sistemas
        if 'sistemas_utilizados_selecionados' in self.cleaned_data:
            instance.sistemas_utilizados.all().delete()
            for obj in self.cleaned_data['sistemas_utilizados_selecionados']:
                PerfilEmpresaSistemasUtilizados.objects.create(perfil_empresa=instance, sistema_utilizado=obj)
                
        # Objetivos
        if 'objetivos_selecionados' in self.cleaned_data:
            instance.objetivos_12_meses.all().delete()
            for obj in self.cleaned_data['objetivos_selecionados']:
                PerfilEmpresaObjetivos.objects.create(perfil_empresa=instance, objetivo=obj)
                
        # Restrições
        if 'restricoes_selecionadas' in self.cleaned_data:
            instance.restricoes_criticas.all().delete()
            for obj in self.cleaned_data['restricoes_selecionadas']:
                PerfilEmpresaRestricoes.objects.create(perfil_empresa=instance, restricao=obj)
