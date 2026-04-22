import io
import uuid

import qrcode
from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import AlunoForm, AulaForm, DisciplinaForm, PresencaForm, ProfessorForm, SalaForm
from .models import Aluno, Aula, Disciplina, Presenca, Professor, Sala


def log_action(user, obj, flag, message=''):
    LogEntry.objects.create(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=flag,
        change_message=message or '',
    )


class StrictPermissionRequiredMixin(PermissionRequiredMixin):
    """Retorna 403 em vez de redirecionar quando permissão negada (AC9)."""
    raise_exception = True


class AuditedCreateView(LoginRequiredMixin, StrictPermissionRequiredMixin, CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, self.object, ADDITION, 'Criado via CRUD')
        return response


class AuditedUpdateView(LoginRequiredMixin, StrictPermissionRequiredMixin, UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, self.object, CHANGE, 'Editado via CRUD')
        return response


class AuditedDeleteView(LoginRequiredMixin, StrictPermissionRequiredMixin, DeleteView):
    def form_valid(self, form):
        obj = self.get_object()
        log_action(self.request.user, obj, DELETION, 'Excluído via CRUD')
        return super().form_valid(form)


def _is_professor(user):
    return user.groups.filter(name='Professores').exists()


def _is_aluno(user):
    return user.groups.filter(name='Alunos').exists()


# ========== ALUNO ==========
class AlunoList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Aluno
    permission_required = 'core.view_aluno'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(matricula__icontains=q))
        return qs


class AlunoDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Aluno
    permission_required = 'core.view_aluno'


class AlunoCreate(AuditedCreateView):
    model = Aluno
    form_class = AlunoForm
    permission_required = 'core.add_aluno'
    success_url = reverse_lazy('aluno_list')


class AlunoUpdate(AuditedUpdateView):
    model = Aluno
    form_class = AlunoForm
    permission_required = 'core.change_aluno'
    success_url = reverse_lazy('aluno_list')


class AlunoDelete(AuditedDeleteView):
    model = Aluno
    permission_required = 'core.delete_aluno'
    success_url = reverse_lazy('aluno_list')


# ========== PROFESSOR ==========
class ProfessorList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Professor
    permission_required = 'core.view_professor'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs


class ProfessorDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Professor
    permission_required = 'core.view_professor'


class ProfessorCreate(AuditedCreateView):
    model = Professor
    form_class = ProfessorForm
    permission_required = 'core.add_professor'
    success_url = reverse_lazy('professor_list')


class ProfessorUpdate(AuditedUpdateView):
    model = Professor
    form_class = ProfessorForm
    permission_required = 'core.change_professor'
    success_url = reverse_lazy('professor_list')


class ProfessorDelete(AuditedDeleteView):
    model = Professor
    permission_required = 'core.delete_professor'
    success_url = reverse_lazy('professor_list')


# ========== DISCIPLINA ==========
class DisciplinaList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Disciplina
    permission_required = 'core.view_disciplina'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('professor')
        user = self.request.user
        if _is_professor(user) and not user.is_staff:
            qs = qs.filter(professor__user=user)
        elif _is_aluno(user) and not user.is_staff:
            qs = qs.filter(alunos__user=user)
        prof = self.request.GET.get('professor')
        if prof and prof.isdigit():
            qs = qs.filter(professor_id=prof)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
        return qs.distinct()


class DisciplinaDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Disciplina
    permission_required = 'core.view_disciplina'


class DisciplinaCreate(AuditedCreateView):
    model = Disciplina
    form_class = DisciplinaForm
    permission_required = 'core.add_disciplina'
    success_url = reverse_lazy('disciplina_list')


class DisciplinaUpdate(UserPassesTestMixin, AuditedUpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    permission_required = 'core.change_disciplina'
    success_url = reverse_lazy('disciplina_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.professor_id == u.professor.pk


class DisciplinaDelete(UserPassesTestMixin, AuditedDeleteView):
    model = Disciplina
    permission_required = 'core.delete_disciplina'
    success_url = reverse_lazy('disciplina_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.professor_id == u.professor.pk


# ========== SALA ==========
class SalaList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Sala
    permission_required = 'core.view_sala'
    paginate_by = 25


class SalaDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Sala
    permission_required = 'core.view_sala'


class SalaCreate(AuditedCreateView):
    model = Sala
    form_class = SalaForm
    permission_required = 'core.add_sala'
    success_url = reverse_lazy('sala_list')


class SalaUpdate(AuditedUpdateView):
    model = Sala
    form_class = SalaForm
    permission_required = 'core.change_sala'
    success_url = reverse_lazy('sala_list')


class SalaDelete(AuditedDeleteView):
    model = Sala
    permission_required = 'core.delete_sala'
    success_url = reverse_lazy('sala_list')


# ========== AULA ==========
class AulaList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Aula
    permission_required = 'core.view_aula'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('disciplina', 'sala', 'disciplina__professor')
        user = self.request.user
        if _is_professor(user) and not user.is_staff:
            qs = qs.filter(disciplina__professor__user=user)
        elif _is_aluno(user) and not user.is_staff:
            qs = qs.filter(disciplina__alunos__user=user)
        disc = (self.request.GET.get('disciplina') or '').strip()
        if disc:
            qs = qs.filter(
                Q(disciplina__nome__icontains=disc)
                | Q(disciplina__codigo__icontains=disc)
            )
        data = self.request.GET.get('data')
        if data:
            qs = qs.filter(data=data)
        return qs.distinct()


class AulaDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Aula
    permission_required = 'core.view_aula'


class AulaCreate(AuditedCreateView):
    model = Aula
    form_class = AulaForm
    permission_required = 'core.add_aula'
    success_url = reverse_lazy('aula_list')


class AulaUpdate(UserPassesTestMixin, AuditedUpdateView):
    model = Aula
    form_class = AulaForm
    permission_required = 'core.change_aula'
    success_url = reverse_lazy('aula_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.disciplina.professor_id == u.professor.pk


class AulaDelete(UserPassesTestMixin, AuditedDeleteView):
    model = Aula
    permission_required = 'core.delete_aula'
    success_url = reverse_lazy('aula_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.disciplina.professor_id == u.professor.pk


# ========== PRESENCA ==========
class PresencaList(LoginRequiredMixin, StrictPermissionRequiredMixin, ListView):
    model = Presenca
    permission_required = 'core.view_presenca'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related('aluno', 'aula', 'aula__disciplina')
        user = self.request.user
        if _is_professor(user) and not user.is_staff:
            qs = qs.filter(aula__disciplina__professor__user=user)
        elif _is_aluno(user) and not user.is_staff:
            qs = qs.filter(aluno__user=user)
        aluno = self.request.GET.get('aluno')
        if aluno and aluno.isdigit():
            qs = qs.filter(aluno_id=aluno)
        disc = self.request.GET.get('disciplina')
        if disc and disc.isdigit():
            qs = qs.filter(aula__disciplina_id=disc)
        data = self.request.GET.get('data')
        if data:
            qs = qs.filter(aula__data=data)
        return qs


class PresencaDetail(LoginRequiredMixin, StrictPermissionRequiredMixin, DetailView):
    model = Presenca
    permission_required = 'core.view_presenca'


class PresencaUpdate(UserPassesTestMixin, AuditedUpdateView):
    """Somente professor da aula ou admin pode editar presença."""
    model = Presenca
    form_class = PresencaForm
    permission_required = 'core.change_presenca'
    success_url = reverse_lazy('presenca_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.aula.disciplina.professor_id == u.professor.pk


class PresencaDelete(UserPassesTestMixin, AuditedDeleteView):
    model = Presenca
    permission_required = 'core.delete_presenca'
    success_url = reverse_lazy('presenca_list')

    def test_func(self):
        u = self.request.user
        if u.is_staff:
            return True
        obj = self.get_object()
        return hasattr(u, 'professor') and obj.aula.disciplina.professor_id == u.professor.pk




# ========== QR CODE ==========
def _user_can_manage_aula(user, aula):
    if user.is_staff:
        return True
    return hasattr(user, 'professor') and aula.disciplina.professor_id == user.professor.pk


def _build_presenca_url(aula):
    return f'{settings.SITE_URL}/presenca?id={aula.pk}&token={aula.token_qrcode}'


@login_required
def aula_qrcode(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if not _user_can_manage_aula(request.user, aula):
        raise PermissionDenied
    img = qrcode.make(_build_presenca_url(aula))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required
def aula_imprimir(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if not _user_can_manage_aula(request.user, aula):
        raise PermissionDenied
    return render(request, 'core/aula_imprimir.html', {
        'aula': aula,
        'presenca_url': _build_presenca_url(aula),
    })


@login_required
@require_POST
def aula_regenerar_token(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if not _user_can_manage_aula(request.user, aula):
        raise PermissionDenied
    aula.token_qrcode = uuid.uuid4()
    aula.save(update_fields=['token_qrcode'])
    log_action(request.user, aula, CHANGE, 'Token do QR Code regenerado')
    return redirect('aula_imprimir', pk=aula.pk)


# ========== REGISTRO DE PRESENCA ==========
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .utils import get_client_ip, haversine_m, ip_in_ranges


def _get_aluno_for_user(user):
    if not hasattr(user, 'aluno'):
        return None
    return user.aluno


def _validate_presenca(user, aula, token, latitude, longitude, client_ip):
    """Retorna (ok, status_code, mensagem). Ordem: auth → token → horário → duplicidade → IP → geo."""
    aluno = _get_aluno_for_user(user)
    if aluno is None:
        return False, 403, 'Apenas alunos podem registrar presença.'

    if str(aula.token_qrcode) != str(token):
        return False, 400, 'QR Code inválido.'

    from datetime import datetime as _dt
    now = timezone.localtime()
    inicio = timezone.make_aware(_dt.combine(aula.data, aula.horario_inicio))
    fim = timezone.make_aware(_dt.combine(aula.data, aula.horario_fim))
    if not (inicio <= now <= fim):
        return False, 400, 'A aula não está em andamento.'

    if Presenca.objects.filter(aluno=aluno, aula=aula).exists():
        return False, 409, 'Presença já registrada para esta aula.'

    if not ip_in_ranges(client_ip, settings.UNIVERSITY_IP_RANGES):
        return False, 403, 'Você precisa estar conectado à rede da universidade.'

    try:
        lat_f = float(latitude)
        lng_f = float(longitude)
    except (TypeError, ValueError):
        return False, 400, 'Localização inválida.'

    distancia = haversine_m(lat_f, lng_f, aula.sala.latitude, aula.sala.longitude)
    if distancia > aula.sala.raio_permitido:
        return False, 403, f'Você está fora do raio permitido da sala ({int(distancia)}m).'

    return True, 200, 'OK'


@ensure_csrf_cookie
def presenca_view(request):
    aula_id = request.GET.get('id') or request.POST.get('aula_id')
    token = request.GET.get('token') or request.POST.get('token')

    if not request.user.is_authenticated:
        # Allauth redireciona para login e volta aqui via `next`
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    if not (aula_id and aula_id.isdigit() and token):
        return render(request, 'core/presenca.html', {
            'erro': 'Link de presença inválido.',
        }, status=400)

    aula = get_object_or_404(Aula, pk=int(aula_id))

    if request.method == 'GET':
        return render(request, 'core/presenca.html', {
            'aula': aula,
            'token': token,
        })

    # POST → valida e registra
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    client_ip = get_client_ip(request)

    ok, status_code, mensagem = _validate_presenca(
        request.user, aula, token, latitude, longitude, client_ip
    )
    if not ok:
        return JsonResponse({'ok': False, 'mensagem': mensagem}, status=status_code)

    presenca = Presenca.objects.create(
        aluno=request.user.aluno,
        aula=aula,
        ip_registrado=client_ip or None,
        latitude=float(latitude),
        longitude=float(longitude),
        status='PRESENTE',
    )
    log_action(request.user, presenca, ADDITION, 'Presença registrada via QR Code')
    return JsonResponse({
        'ok': True,
        'mensagem': 'Presença registrada com sucesso.',
        'presenca_id': presenca.pk,
    })


# ========== DASHBOARD + AUDITORIA ==========
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date


@login_required
def dashboard_view(request):
    user = request.user
    ctx = {
        'is_admin': user.is_staff,
        'is_professor': _is_professor(user),
        'is_aluno': _is_aluno(user),
    }
    hoje = timezone.localdate()

    if user.is_staff:
        ctx.update({
            'total_usuarios': user.__class__.objects.count(),
            'total_alunos': Aluno.objects.count(),
            'total_professores': Professor.objects.count(),
            'total_disciplinas': Disciplina.objects.count(),
            'aulas_hoje': Aula.objects.filter(data=hoje).count(),
            'presencas_hoje': Presenca.objects.filter(aula__data=hoje).count(),
        })

    elif _is_professor(user) and hasattr(user, 'professor'):
        prof = user.professor
        minhas_disciplinas = Disciplina.objects.filter(professor=prof)
        ctx.update({
            'disciplinas': minhas_disciplinas,
            'proximas_aulas': Aula.objects.filter(
                disciplina__professor=prof, data__gte=hoje
            ).select_related('disciplina', 'sala').order_by('data', 'horario_inicio')[:10],
            'ultimas_presencas': Presenca.objects.filter(
                aula__disciplina__professor=prof
            ).select_related('aluno', 'aula__disciplina').order_by('-horario_registro')[:10],
        })

    elif _is_aluno(user) and hasattr(user, 'aluno'):
        aluno = user.aluno
        minhas_disciplinas = Disciplina.objects.filter(alunos=aluno)
        proxima = Aula.objects.filter(
            disciplina__alunos=aluno, data__gte=hoje
        ).order_by('data', 'horario_inicio').first()

        frequencia = []
        for d in minhas_disciplinas:
            total = Aula.objects.filter(disciplina=d, data__lte=hoje).count()
            presentes = Presenca.objects.filter(
                aluno=aluno, aula__disciplina=d, status='PRESENTE'
            ).count()
            pct = (presentes / total * 100) if total else 0
            frequencia.append({'disciplina': d, 'total': total, 'presentes': presentes, 'pct': round(pct, 1)})

        ctx.update({
            'disciplinas': minhas_disciplinas,
            'proxima_aula': proxima,
            'total_presencas': Presenca.objects.filter(aluno=aluno).count(),
            'frequencia': frequencia,
        })

    return render(request, 'core/dashboard.html', ctx)


@staff_member_required
def auditoria_view(request):
    qs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')

    usuario = request.GET.get('usuario')
    if usuario and usuario.isdigit():
        qs = qs.filter(user_id=usuario)

    acao = request.GET.get('acao')
    if acao and acao.isdigit():
        qs = qs.filter(action_flag=acao)

    modelo = request.GET.get('modelo')
    if modelo:
        qs = qs.filter(content_type__model=modelo.lower())

    desde = request.GET.get('desde')
    d1 = parse_date(desde) if desde else None
    if d1:
        qs = qs.filter(action_time__date__gte=d1)

    ate = request.GET.get('ate')
    d2 = parse_date(ate) if ate else None
    if d2:
        qs = qs.filter(action_time__date__lte=d2)

    page = Paginator(qs, 50).get_page(request.GET.get('page'))
    return render(request, 'core/auditoria.html', {
        'page_obj': page,
        'object_list': page.object_list,
        'is_paginated': page.has_other_pages(),
    })
