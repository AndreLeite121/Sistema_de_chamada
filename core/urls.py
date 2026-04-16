from django.urls import path

from . import views

urlpatterns = [
    # Aluno
    path('alunos/', views.AlunoList.as_view(), name='aluno_list'),
    path('alunos/novo/', views.AlunoCreate.as_view(), name='aluno_create'),
    path('alunos/<int:pk>/', views.AlunoDetail.as_view(), name='aluno_detail'),
    path('alunos/<int:pk>/editar/', views.AlunoUpdate.as_view(), name='aluno_update'),
    path('alunos/<int:pk>/excluir/', views.AlunoDelete.as_view(), name='aluno_delete'),
    # Professor
    path('professores/', views.ProfessorList.as_view(), name='professor_list'),
    path('professores/novo/', views.ProfessorCreate.as_view(), name='professor_create'),
    path('professores/<int:pk>/', views.ProfessorDetail.as_view(), name='professor_detail'),
    path('professores/<int:pk>/editar/', views.ProfessorUpdate.as_view(), name='professor_update'),
    path('professores/<int:pk>/excluir/', views.ProfessorDelete.as_view(), name='professor_delete'),
    # Disciplina
    path('disciplinas/', views.DisciplinaList.as_view(), name='disciplina_list'),
    path('disciplinas/nova/', views.DisciplinaCreate.as_view(), name='disciplina_create'),
    path('disciplinas/<int:pk>/', views.DisciplinaDetail.as_view(), name='disciplina_detail'),
    path('disciplinas/<int:pk>/editar/', views.DisciplinaUpdate.as_view(), name='disciplina_update'),
    path('disciplinas/<int:pk>/excluir/', views.DisciplinaDelete.as_view(), name='disciplina_delete'),
    # Sala
    path('salas/', views.SalaList.as_view(), name='sala_list'),
    path('salas/nova/', views.SalaCreate.as_view(), name='sala_create'),
    path('salas/<int:pk>/', views.SalaDetail.as_view(), name='sala_detail'),
    path('salas/<int:pk>/editar/', views.SalaUpdate.as_view(), name='sala_update'),
    path('salas/<int:pk>/excluir/', views.SalaDelete.as_view(), name='sala_delete'),
    # Aula
    path('aulas/', views.AulaList.as_view(), name='aula_list'),
    path('aulas/nova/', views.AulaCreate.as_view(), name='aula_create'),
    path('aulas/<int:pk>/', views.AulaDetail.as_view(), name='aula_detail'),
    path('aulas/<int:pk>/editar/', views.AulaUpdate.as_view(), name='aula_update'),
    path('aulas/<int:pk>/excluir/', views.AulaDelete.as_view(), name='aula_delete'),
    path('aulas/<int:pk>/qrcode.png', views.aula_qrcode, name='aula_qrcode'),
    path('aulas/<int:pk>/imprimir/', views.aula_imprimir, name='aula_imprimir'),
    path('aulas/<int:pk>/regenerar-token/', views.aula_regenerar_token, name='aula_regenerar_token'),
    # Presenca
    path('presencas/', views.PresencaList.as_view(), name='presenca_list'),
    path('presencas/<int:pk>/', views.PresencaDetail.as_view(), name='presenca_detail'),
    path('presencas/<int:pk>/editar/', views.PresencaUpdate.as_view(), name='presenca_update'),
    path('presencas/<int:pk>/excluir/', views.PresencaDelete.as_view(), name='presenca_delete'),
    # Dashboard + Auditoria
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('auditoria/', views.auditoria_view, name='auditoria'),
]
