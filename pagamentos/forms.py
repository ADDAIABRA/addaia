from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class CadastroUsuarioForm(UserCreationForm):
    nome_completo = forms.CharField(
        label='Nome Completo', 
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'})
    )
    email = forms.EmailField(
        label='Email', 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    telefone = forms.CharField(
        label='Celular/WhatsApp', 
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'})
    )

    class Meta:
        model = User
        fields = ('email',)  # Apenas campos que existem no modelo User

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este email já está cadastrado.")
        return email

    def save(self, commit=True):
        user = super(CadastroUsuarioForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Username é o email
        
        # Split nome
        names = self.cleaned_data['nome_completo'].strip().split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
            
        if commit:
            user.save()
            Perfil.objects.create(usuario=user, telefone=self.cleaned_data['telefone'])
        return user
