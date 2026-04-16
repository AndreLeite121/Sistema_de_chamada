from django import forms

from .models import Aluno, Aula, Disciplina, Presenca, Professor, Sala


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['user', 'nome', 'matricula', 'email', 'curso']


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['user', 'nome', 'email', 'departamento']


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
