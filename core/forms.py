from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import Aluno, Aula, Disciplina, Presenca, Professor, Sala


def _sync_user_account(instancia, email, senha, grupo_nome):
    """Cria/atualiza o User vinculado, garante grupo e EmailAddress verificado.

    - Se a instância já tem user, atualiza email/senha desse user.
    - Se não tem, cria um novo User com email como username.
    - Senha só é trocada quando `senha` vem preenchida.
    """
    User = get_user_model()

    if instancia.user_id:
        user = instancia.user
        user.email = email
        user.username = email
    else:
        existente = User.objects.filter(username=email).first() or User.objects.filter(email__iexact=email).first()
        if existente:
            raise forms.ValidationError('Já existe uma conta de login com este email.')
        user = User(username=email, email=email)

    if senha:
        user.set_password(senha)
    elif not user.pk:
        user.set_unusable_password()

    user.save()

    grupo, _ = Group.objects.get_or_create(name=grupo_nome)
    user.groups.add(grupo)

    EmailAddress.objects.filter(user=user).exclude(email__iexact=email).update(primary=False)
    EmailAddress.objects.update_or_create(
        user=user, email=email,
        defaults={'verified': True, 'primary': True},
    )
    return user


class AlunoForm(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Na criação: senha inicial para login. Na edição: deixe em branco para manter.',
    )

    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'email', 'curso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['senha'].required = True
            self.fields['senha'].help_text = 'Senha inicial para login do aluno.'

    def save(self, commit=True):
        aluno = super().save(commit=False)
        user = _sync_user_account(
            aluno,
            email=self.cleaned_data['email'],
            senha=self.cleaned_data.get('senha'),
            grupo_nome='Alunos',
        )
        aluno.user = user
        if commit:
            aluno.save()
            self.save_m2m()
        return aluno


class ProfessorForm(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text='Na criação: senha inicial para login. Na edição: deixe em branco para manter.',
    )

    class Meta:
        model = Professor
        fields = ['nome', 'email', 'departamento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['senha'].required = True
            self.fields['senha'].help_text = 'Senha inicial para login do professor.'

    def save(self, commit=True):
        professor = super().save(commit=False)
        user = _sync_user_account(
            professor,
            email=self.cleaned_data['email'],
            senha=self.cleaned_data.get('senha'),
            grupo_nome='Professores',
        )
        professor.user = user
        if commit:
            professor.save()
            self.save_m2m()
        return professor


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'codigo', 'professor', 'semestre', 'alunos']
        widgets = {'alunos': forms.CheckboxSelectMultiple()}


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'predio', 'latitude', 'longitude', 'raio_permitido']


class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['disciplina', 'sala', 'data', 'horario_inicio', 'horario_fim']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }


class PresencaForm(forms.ModelForm):
    class Meta:
        model = Presenca
        fields = ['aluno', 'aula', 'status']
