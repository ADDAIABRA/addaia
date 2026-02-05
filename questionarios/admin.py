from django.contrib import admin
from .models import (
    AvaliacaoMaturidade,
    PilarQuestionario,
    PerguntaQuestionario,
    RespostaQuestionario,
    RespostaPergunta
)

class PerguntaQuestionarioInline(admin.TabularInline):
    model = PerguntaQuestionario
    extra = 1
    fields = ('ordem', 'codigo', 'enunciado', 'ativo')

@admin.register(PilarQuestionario)
class PilarQuestionarioAdmin(admin.ModelAdmin):
    list_display = ('pilar', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')
    inlines = [PerguntaQuestionarioInline]

@admin.register(PerguntaQuestionario)
class PerguntaQuestionarioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'pilar', 'ordem', 'enunciado_curto', 'ativo')
    list_filter = ('pilar', 'ativo')
    search_fields = ('codigo', 'enunciado')
    list_editable = ('ordem', 'ativo')

    def enunciado_curto(self, obj):
        return obj.enunciado[:60]
    enunciado_curto.short_description = "Enunciado"

class RespostaPerguntaInline(admin.TabularInline):
    model = RespostaPergunta
    extra = 0
    readonly_fields = ('pergunta', 'alternativa_escolhida', 'pontuacao')
    can_delete = False

@admin.register(RespostaQuestionario)
class RespostaQuestionarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'avaliacao', 'pilar', 'pontuacao_pilar', 'estagio_pilar')
    list_filter = ('pilar', 'estagio_pilar')
    readonly_fields = ('pontuacao_pilar', 'estagio_pilar')
    inlines = [RespostaPerguntaInline]

class RespostaQuestionarioInline(admin.TabularInline):
    model = RespostaQuestionario
    extra = 0
    readonly_fields = ('pilar', 'pontuacao_pilar', 'estagio_pilar')
    can_delete = False

@admin.register(AvaliacaoMaturidade)
class AvaliacaoMaturidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil_empresa', 'titulo', 'pontuacao_geral', 'estagio_geral', 'criado_em')
    list_filter = ('estagio_geral', 'criado_em')
    search_fields = ('titulo', 'perfil_empresa__nome_empresa')
    readonly_fields = ('pontuacao_geral', 'estagio_geral')
    inlines = [RespostaQuestionarioInline]

@admin.register(RespostaPergunta)
class RespostaPerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pergunta', 'alternativa_escolhida', 'pontuacao')
    list_filter = ('alternativa_escolhida',)
