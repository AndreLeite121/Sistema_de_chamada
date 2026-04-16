from datetime import date, time, timedelta

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Aluno, Aula, Disciplina, Presenca, Professor, Sala


class Command(BaseCommand):
    help = 'Cria usuários, grupos e dados de demo para testar o sistema.'

    def handle(self, *args, **options):
        User = get_user_model()

        # --- Usuários ---
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@demo.local', 'is_staff': True, 'is_superuser': True},
        )
        admin.set_password('admin123')
        admin.email = 'admin@demo.local'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        EmailAddress.objects.update_or_create(
            user=admin, email=admin.email,
            defaults={'verified': True, 'primary': True},
        )

        prof_user, _ = User.objects.get_or_create(
            username='professor',
            defaults={'email': 'professor@demo.local'},
        )
        prof_user.set_password('professor123')
        prof_user.email = 'professor@demo.local'
        prof_user.save()
        EmailAddress.objects.update_or_create(
            user=prof_user, email=prof_user.email,
            defaults={'verified': True, 'primary': True},
        )

        aluno_user, _ = User.objects.get_or_create(
            username='aluno',
            defaults={'email': 'aluno@demo.local'},
        )
        aluno_user.set_password('aluno123')
        aluno_user.email = 'aluno@demo.local'
        aluno_user.save()
        EmailAddress.objects.update_or_create(
            user=aluno_user, email=aluno_user.email,
            defaults={'verified': True, 'primary': True},
        )

        # --- Groups ---
        prof_user.groups.add(Group.objects.get(name='Professores'))
        aluno_user.groups.add(Group.objects.get(name='Alunos'))

        # --- Entidades de domínio ---
        professor, _ = Professor.objects.update_or_create(
            email='professor@demo.local',
            defaults={
                'user': prof_user,
                'nome': 'Prof. Alessandro Vivas',
                'departamento': 'Computação',
            },
        )

        aluno, _ = Aluno.objects.update_or_create(
            matricula='2026001',
            defaults={
                'user': aluno_user,
                'nome': 'João da Silva',
                'email': 'aluno@demo.local',
                'curso': 'Sistemas de Informação',
            },
        )

        disciplina, _ = Disciplina.objects.update_or_create(
            codigo='SDIST01',
            defaults={
                'nome': 'Sistemas Distribuídos',
                'professor': professor,
                'semestre': '2026.1',
            },
        )
        disciplina.alunos.add(aluno)

        sala, _ = Sala.objects.update_or_create(
            predio='ICET',
            nome='Lab 1',
            defaults={
                # Coordenadas de UFVJM (Diamantina/MG) — ajuste para testar localmente
                'latitude': -18.2478,
                'longitude': -43.6031,
                'raio_permitido': 100,
            },
        )

        # --- Aulas: uma agora (para testar presença) + próximas ---
        hoje = timezone.localdate()
        agora = timezone.localtime().time()
        inicio = time(max(agora.hour - 1, 0), 0)
        fim = time(min(agora.hour + 2, 23), 0)

        aula_agora, _ = Aula.objects.update_or_create(
            disciplina=disciplina, data=hoje, horario_inicio=inicio,
            defaults={'sala': sala, 'horario_fim': fim},
        )

        Aula.objects.update_or_create(
            disciplina=disciplina, data=hoje + timedelta(days=2), horario_inicio=time(14, 0),
            defaults={'sala': sala, 'horario_fim': time(16, 0)},
        )

        self.stdout.write(self.style.SUCCESS('✓ Seed concluído!'))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Usuários de teste (senha = username + "123"):'))
        self.stdout.write('  admin       / admin123       (superuser)')
        self.stdout.write('  professor   / professor123   (group Professores)')
        self.stdout.write('  aluno       / aluno123       (group Alunos)')
        self.stdout.write('')
        self.stdout.write(f'Aula em andamento (para testar presença): #{aula_agora.pk}')
        self.stdout.write(f'Token QR: {aula_agora.token_qrcode}')
        self.stdout.write(f'URL presença: http://localhost:8000/presenca?id={aula_agora.pk}&token={aula_agora.token_qrcode}')
