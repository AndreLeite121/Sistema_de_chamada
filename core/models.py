import uuid

from django.conf import settings
from django.db import models


class Aluno(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='aluno',
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    curso = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f'{self.matricula} - {self.nome}'


class Professor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='professor',
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    departamento = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Disciplina(models.Model):
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20, unique=True)
    professor = models.ForeignKey(
        Professor, on_delete=models.PROTECT, related_name='disciplinas'
    )
    semestre = models.CharField(max_length=10, help_text='Ex.: 2026.1')
    alunos = models.ManyToManyField(Aluno, related_name='disciplinas', blank=True)

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class Sala(models.Model):
    nome = models.CharField(max_length=50)
    predio = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    raio_permitido = models.PositiveIntegerField(
        default=50, help_text='Raio em metros'
    )

    class Meta:
        ordering = ['predio', 'nome']
        unique_together = [('predio', 'nome')]

    def __str__(self):
        return f'{self.predio} - {self.nome}'


class Aula(models.Model):
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name='aulas'
    )
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name='aulas')
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    token_qrcode = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-data', '-horario_inicio']

    def __str__(self):
        return f'{self.disciplina.codigo} - {self.data} {self.horario_inicio}'


class Presenca(models.Model):
    STATUS_CHOICES = [
        ('PRESENTE', 'Presente'),
        ('AUSENTE', 'Ausente'),
        ('JUSTIFICADA', 'Justificada'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='presencas')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='presencas')
    horario_registro = models.DateTimeField(auto_now_add=True)
    ip_registrado = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENTE')

    class Meta:
        ordering = ['-horario_registro']
        unique_together = [('aluno', 'aula')]

    def __str__(self):
        return f'{self.aluno.matricula} @ {self.aula} [{self.status}]'
