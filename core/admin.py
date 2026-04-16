from django.contrib import admin

from .models import Aluno, Aula, Disciplina, Presenca, Professor, Sala


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'email', 'curso')
    search_fields = ('matricula', 'nome', 'email')
    list_filter = ('curso',)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'departamento')
    search_fields = ('nome', 'email')
    list_filter = ('departamento',)


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'professor', 'semestre')
    search_fields = ('codigo', 'nome')
    list_filter = ('semestre', 'professor')
    filter_horizontal = ('alunos',)


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('predio', 'nome', 'latitude', 'longitude', 'raio_permitido')
    search_fields = ('nome', 'predio')
    list_filter = ('predio',)


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'sala', 'data', 'horario_inicio', 'horario_fim')
    search_fields = ('disciplina__codigo', 'disciplina__nome')
    list_filter = ('data', 'disciplina', 'sala')
    readonly_fields = ('token_qrcode',)


@admin.register(Presenca)
class PresencaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'aula', 'horario_registro', 'status', 'ip_registrado')
    search_fields = ('aluno__matricula', 'aluno__nome', 'aula__disciplina__codigo')
    list_filter = ('status', 'aula__data', 'aula__disciplina')
    readonly_fields = ('horario_registro',)
