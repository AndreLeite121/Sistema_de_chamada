# Sistema de Controle de Frequência por QR Code

Trabalho da disciplina de **Sistemas Distribuídos**
Prof. Alessandro Vivas Andrade

**Integrantes:**
- André Leite
- André Alexandre
- Lavínia Charrua
- Iasmin Torres

---

Sistema distribuído (em construção) para controle de presença em sala de aula
usando QR Code, com validação de rede institucional, geolocalização e autenticação.

**Parte 1 (concluída):** Autenticação, modelos de domínio, CRUD, QR Code,
registro de presença validado, dashboard e histórico.

## Stack

- Python 3.10+ · Django 5.2 · django-allauth
- SQLite (default em dev) · PostgreSQL (opcional)
- `qrcode[pil]` para geração de QR
- Tailwind (CDN) + JS vanilla no frontend

## Setup rápido (Linux / macOS) — 5 passos com SQLite

Esse é o caminho recomendado para avaliar o projeto: **não precisa instalar
PostgreSQL nem configurar banco**. O SQLite vem embutido no Python.

### 1. Clonar e criar virtualenv
```bash
git clone https://github.com/AndreLeite121/Sistema_de_chamada.git
cd Sistema_de_chamada
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Copiar o arquivo de ambiente
```bash
cp .env.example .env
```

> **Nota:** `.env` é arquivo oculto (começa com `.`). Para confirmar que ele
> foi criado, use `ls -a`. Para abrir e editar, `nano .env` ou `code .env`.
> Por padrão ele já vem configurado para SQLite — não precisa mudar nada
> para o setup rápido.

### 3. Aplicar migrations e popular dados de demonstração
```bash
python manage.py migrate
python manage.py seed_demo
```

`seed_demo` cria os grupos, três usuários de teste, uma disciplina, sala e
duas aulas (uma "em andamento" para testar o fluxo de presença).

> Para criar um superuser próprio em vez do demo, use
> `python manage.py createsuperuser`.

### 4. Rodar
```bash
python manage.py runserver
```

Acesse http://localhost:8000 e faça login com um dos usuários abaixo.

---

## Setup com PostgreSQL (opcional)

Use este caminho apenas se quiser rodar o projeto contra PostgreSQL real.
Faça os passos 1 e 2 do setup rápido normalmente, depois:

### 1. Instalar PostgreSQL
```bash
# Ubuntu / Debian
sudo apt update
sudo apt install postgresql postgresql-client
sudo service postgresql start

# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16
```

### 2. Criar usuário com senha e o banco
```bash
sudo -u postgres psql
```
Dentro do `psql`:
```sql
ALTER USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE sistema_freq;
\q
```

### 3. Apontar o `.env` para PostgreSQL
Abra `.env` (`nano .env`) e troque o bloco de banco para:
```env
DB_ENGINE=postgresql
DB_NAME=sistema_freq
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
```

> **Dica:** prefira `127.0.0.1` a `localhost`. Em alguns sistemas Linux
> `localhost` força autenticação `peer` (via socket Unix) e ignora a senha,
> o que costuma confundir o erro.

### 4. Aplicar migrations e seguir
```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Usuários de teste (após `seed_demo`)

Login é feito por **e-mail** em `/accounts/login/`.

| Papel        | Email                  | Senha          |
|--------------|------------------------|----------------|
| Administrador | `admin@demo.local`     | `admin123`     |
| Professor    | `professor@demo.local` | `professor123` |
| Aluno        | `aluno@demo.local`     | `aluno123`     |

Cada um cai em um dashboard diferente conforme o papel:
- **Admin** vê totais, auditoria e CRUD completo.
- **Professor** vê suas disciplinas, próximas aulas e últimas presenças.
- **Aluno** vê suas disciplinas, próxima aula e percentual de frequência.

> Senhas são apenas para demonstração local — **não** use em produção.

## Papéis (Groups)

O sistema cria automaticamente 3 grupos (via data migration):
- **Administradores** — CRUD total
- **Professores** — gerencia suas disciplinas, aulas, QR Code
- **Alunos** — visualiza aulas, registra presença

Adicione usuários aos grupos pelo admin do Django (`/admin/`).
Para Professores e Alunos, também crie um registro em
`core.Professor` ou `core.Aluno` ligado ao User
(ou use os formulários internos de `/core/alunos/novo/` e
`/core/professores/novo/`, que já criam o User vinculado).

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

## Solução de problemas comuns

- **`pip install` falha em `Django==X`**: confirme que o `requirements.txt`
  está fixado em `Django==5.2.7`. Versões 6.x ainda não foram lançadas.
- **`No module named 'django'`**: você esqueceu de ativar o venv. Rode
  `source venv/bin/activate` antes de qualquer `python manage.py …`.
- **`.env` não aparece no `ls`**: arquivos com `.` no início são ocultos.
  Use `ls -a`.
- **(PostgreSQL) `password authentication failed for user "postgres"`**:
  a senha do usuário `postgres` no seu PostgreSQL não bate com a do `.env`.
  Veja o passo 2 do "Setup com PostgreSQL".
- **(PostgreSQL) `database "sistema_freq" does not exist`**: o banco não
  foi criado. Refaça `CREATE DATABASE sistema_freq;` dentro do `psql`.
- **Login "não acontece nada"**: o login é por **e-mail**, não username.
  Use `admin@demo.local` em vez de `admin`.

## Observações

- `USE_I18N=False` é definido em `settings.py` para evitar dependência de
  arquivos `.mo` de tradução. As labels dos modelos já estão em PT no código.
- Auditoria usa `django.contrib.admin.models.LogEntry` (nativo do Django).
  Visível em `/core/auditoria/` (staff) e `/admin/admin/logentry/`.

## Roadmap

- **Parte 1:** ✅ Autenticação, QR Code, CRUD, registro de presença, dashboard
- **Parte 2:** ⏳ API REST (DRF), microserviços, Redis, RabbitMQ/Kafka, dashboards com gráficos
