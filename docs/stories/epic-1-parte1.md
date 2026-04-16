# Épico 1 — Parte 1: Autenticação, QR Code e CRUD

**Fonte:** `Roteiro_Trabalho_Sistemas_Distribuidos.pdf` — Parte 1
**Objetivo:** Entregar a base funcional do sistema de frequência: autenticação com roles, modelos de domínio, CRUD, geração de QR Code, registro de presença validado (IP + geolocalização) e dashboard por perfil.

## Stories

| ID | Título | Status |
|----|--------|--------|
| 1.1 | Modelos de domínio + Roles + Auditoria | Ready for Review |
| 1.2 | CRUD das entidades com permissões por role | Ready for Review |
| 1.3 | Geração de QR Code por Aula | Ready for Review |
| 1.4 | Registro de Presença com validação (IP + Geo + horário) | Ready for Review |
| 1.5 | Dashboard personalizado por perfil + histórico | Ready for Review |
| 1.6 | Migração para PostgreSQL + requirements.txt | Ready for Review |

## Dependências
1.1 → 1.2 → 1.3 → 1.4 → 1.5
1.6 pode rodar em paralelo a partir da 1.1.
