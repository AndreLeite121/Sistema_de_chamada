# Sistema de Controle de Frequência por QR Code

Sistema distribuído (em construção) para controle de presença em sala de aula
usando QR Code, com validação de rede institucional, geolocalização e autenticação.

**Parte 1 (concluída):** Autenticação, modelos de domínio, CRUD, QR Code,
registro de presença validado, dashboard e histórico.

## Stack

- Python 3.12 · Django 6 · django-allauth
- PostgreSQL (produção) · SQLite (dev, opcional)
- `qrcode[pil]` para geração de QR
- Tailwind (CDN) + JS vanilla no frontend

## Setup (Linux / macOS)

### 1. Clonar e criar virtualenv
```bash
git clone <repo>
cd SistemaOpr
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# edite .env com os valores reais (banco, SECRET_KEY etc.)
```

### 3. Subir o PostgreSQL e criar o banco
```bash
# instale o PostgreSQL localmente, depois:
createdb sistema_freq
# ou via psql:
psql -U postgres -c "CREATE DATABASE sistema_freq;"
```

> **Alternativa rápida em dev:** deixe `DB_ENGINE=sqlite3` no `.env`
> para não precisar de PostgreSQL.

### 4. Aplicar migrations e criar superusuário
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Rodar
```bash
python manage.py runserver
```

Acesse http://localhost:8000.

## Papéis (Groups)

O sistema cria automaticamente 3 grupos (via data migration):
- **Administradores** — CRUD total
- **Professores** — gerencia suas disciplinas, aulas, QR Code
- **Alunos** — visualiza aulas, registra presença

Adicione usuários aos grupos pelo admin do Django (`/admin/`).
Para Professores e Alunos, também crie um registro em
`core.Professor` ou `core.Aluno` ligado ao User.

## Fluxo de presença

1. Professor cria Aula → gera QR Code em `/core/aulas/<id>/imprimir/`
2. Imprime e leva à sala
3. Aluno escaneia → abre `/presenca?id=X&token=UUID` → faz login
4. Sistema valida (em ordem):
   - autenticação + role Aluno
   - token do QR
   - horário da aula (está acontecendo agora?)
   - duplicidade (já registrou?)
   - IP dentro de `UNIVERSITY_IP_RANGES`
   - distância haversine ≤ `sala.raio_permitido`
5. Presença registrada + entrada em `LogEntry`

## Comandos úteis

```bash
python manage.py test core       # 11 testes (utils de IP e haversine)
python manage.py check           # sanidade do projeto
python manage.py createsuperuser
```

## Observações

- `USE_I18N=False` — workaround para bug de .mo corrompido em Django 6 (pt).
  Não afeta as labels dos modelos (já em PT no código).
- Auditoria usa `django.contrib.admin.models.LogEntry` (nativo).
  Visível em `/core/auditoria/` (staff) e `/admin/admin/logentry/`.

## Roadmap

- **Parte 1:** ✅ Autenticação, QR Code, CRUD, registro de presença, dashboard
- **Parte 2:** ⏳ API REST (DRF), microserviços, Redis, RabbitMQ/Kafka, dashboards com gráficos
