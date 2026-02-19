"""
Forms do CRM.
"""
from django import forms
from decimal import Decimal


class ColetarLeadsForm(forms.Form):
    keyword = forms.CharField(
        max_length=200,
        label='Palavra-chave / Categoria',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: imobiliária, restaurante, clínica'
        })
    )
    cidade = forms.CharField(
        max_length=150,
        label='Cidade',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Florianópolis'
        })
    )
    bairro = forms.CharField(
        max_length=150,
        required=False,
        label='Bairro (opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Jurerê'
        })
    )
    usar_raio = forms.BooleanField(
        required=False,
        initial=False,
        label='Buscar em raio a partir do local',
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input'})
    )
    raio_km = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        min_value=Decimal('1'),
        max_value=Decimal('50'),
        label='Raio em km (1-50)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 50,
            'step': 0.5,
            'placeholder': 'Ex: 5'
        })
    )

    def clean(self):
        data = super().clean()
        if data.get('usar_raio') and not data.get('raio_km'):
            self.add_error('raio_km', 'Informe o raio em km quando usar busca por raio.')
        return data
