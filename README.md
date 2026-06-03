# spec-codex

Backend de integração com a **Blizzard Game Data API** (World of Warcraft) para servir dados de raças, classes por raça e especializações (specs) ao front-end. Os dados são sincronizados periodicamente para o banco local; as rotas públicas de leitura **não** chamam a Blizzard em tempo real.

## Descrição do projeto

API REST em Django que:

1. Autentica na Blizzard com **Client Credentials** (OAuth).
2. Sincroniza **raças jogáveis** (`playable_races`).
3. Para cada raça, sincroniza as **classes permitidas** com ícone (`playable_race_classes`).
4. Sincroniza **classes globais** e suas **especializações** com ícones (`playable_classes`, `playable_class_specializations`).
5. Expõe endpoints de leitura para o front montar fluxos de criação de personagem (raça → classes da raça; árvore classe → specs, lista ou por `class_id`).

O front consome apenas `GET` no backend; atualização dos dados fica a cargo de cron job ou management commands.

## Tecnologias utilizadas

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.14+ |
| Framework | Django 6, Django REST Framework |
| HTTP cliente | httpx |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL via `DATABASE_URL` |
| Config | python-dotenv, dj-database-url |
| Servidor WSGI | Gunicorn |
| Gerenciador de deps | Poetry |
| Linter | Ruff |
| API externa | Blizzard Battle.net / WoW Game Data (`us`, `static-us`, `pt_BR`) |

## Decisões técnicas

### Banco de dados

- **SQLite** em desenvolvimento (`backend/db.sqlite3`) quando `DATABASE_URL` não está definido.
- **PostgreSQL** em produção usando `DATABASE_URL` (compatível com hosts como Railway, Render, etc.).
- Quatro tabelas de domínio, com nomes explícitos via `db_table`:

| Tabela | Modelo | Propósito |
|--------|--------|-----------|
| `playable_races` | `PlayableRace` | Raças (`race_id` único da Blizzard) |
| `playable_race_classes` | `PlayableRaceClass` | Classes permitidas por raça (N:N materializado) |
| `playable_classes` | `PlayableClass` | Classes globais com ícone |
| `playable_class_specializations` | `PlayableClassSpecialization` | Specs por classe (`unique_together` em `playable_class` + `spec_id`) |

- `synced_at` em todos os modelos (`auto_now=True`) para rastrear última escrita no sync.
- Leitura do front sempre via ORM, com `prefetch_related` onde há relação pai-filho (specs).
- **Migrations versionadas no Git** — toda alteração de schema via `manage.py makemigrations` / `migrate`.

### Integração com API (não é LLM)

Não há integração com LLM neste repositório. O padrão é **cache local**:

- **Sync (escrita):** cron ou CLI chama Blizzard → persiste no banco (`update_or_create` + remoção de registros órfãos).
- **Index (leitura):** front chama Django → resposta montada do banco.

Credenciais: `BNET_CLIENT_ID` e `BNET_CLIENT_SECRET`. Token em `BNET_TOKEN_URL`; dados em `BNET_API_BASE` (padrão `https://us.api.blizzard.com`).

**Classes por raça** (`sync_race_classes.py`):

1. `GET /data/wow/playable-race/{id}` → lista `playable_classes`.
2. Para cada classe, `GET /data/wow/media/playable-class/{class_id}` → ícone (`assets[key=icon]`).
3. Persiste em `playable_race_classes`; remove classes que saíram da API para aquela raça.

**Classes e specs globais** (`sync_class_specs.py`):

1. `GET /data/wow/playable-class/index` → itera classes.
2. Por classe: `GET /data/wow/playable-class/{id}` (detalhe + lista de `specializations`) e mídia da classe.
3. Por spec: `GET /data/wow/media/playable-specialization/{spec_id}` → ícone.
4. Persiste em `playable_classes` e `playable_class_specializations`; remove specs órfãs por classe.

Locale padrão: `pt_BR` para nomes; mídia de specs usa `en_US` por padrão (`spec_media_locale`), pois a API de mídia costuma responder melhor nesse locale.

### Multi-tenancy

**Não aplicável** nesta fase: API single-tenant, dados globais do jogo (sem isolamento por usuário/organização). Se o produto evoluir para contas/tenants, seria camada futura acima deste cache estático.

### Desafios encontrados

| Desafio | Solução |
|---------|---------|
| Volume de chamadas (raças × classes × specs) | `httpx.Client` reutilizado no sync em lote; token OAuth por execução de sync |
| Classe **Aventureiro** (id 14) sem mídia útil / fora do criador padrão | Ignorada no sync (`_SKIP_CLASS_IDS` em `sync_race_classes` e `sync_class_specs`) |
| Ordem do cron para dados por raça | Sync de **raças** antes de **classes por raça** (`sync_all` lê `PlayableRace` do banco) |
| Specs independentes de raça | Sync de classes/specs pode rodar em paralelo ou após raças; não depende de `playable_races` |
| Proteção dos endpoints de sync | `POST` exige `Authorization: Bearer <CRON_SYNC_SECRET>` (`secrets.compare_digest`) |
| Migrations no repositório | Commitar arquivos em `blizzard/migrations/` junto com alterações de `models.py` |

## Funcionalidades implementadas

### Obrigatórias

- [x] Listagem de raças jogáveis (`GET /api/wow/playable-race/index`)
- [x] Sync de raças (`POST /api/wow/playable-race/sync` + `sync_playable_races`)
- [x] Classes jogáveis por raça com nome, facção e ícone (`GET /api/wow/playable-race/{race_id}/playable-classes/index`)
- [x] Sync de classes por raça (`POST /api/wow/playable-race/playable-classes/sync` + `sync_playable_race_classes`)
- [x] Listagem de classes com especializações e ícones (`GET /api/playable-classes/specs/index`)
- [x] Detalhe de uma classe com specs (`GET /api/playable-classes/{class_id}/specs/`)
- [x] Sync de classes e specs (`POST /api/playable-classes/specs/sync` + `sync_playable_class_specs`)
- [x] Persistência nas quatro tabelas de domínio
- [x] Exclusão da classe Aventureiro (id 14) nos syncs

### Diferenciais / operação

- [x] Management commands para sync local e CI
- [x] Suporte a Postgres em produção via `DATABASE_URL`
- [x] Locale `pt_BR` e namespace `static-us` configuráveis nos commands (`--namespace`, `--locale`, `--spec-media-locale`)
- [x] Tradução de facção (Aliança/Horda) a partir do payload da API

### Fora do escopo (por enquanto)

- [ ] Front-end neste repositório
- [ ] Testes automatizados (`blizzard/tests.py` vazio)
- [ ] Endpoint único “sync completo” (raças + classes + specs em um POST)
- [ ] LLM / multi-tenancy
- [ ] Django Admin registrado para os models

## Estrutura do repositório

```
spec-codex/
├── README.md
└── backend/
    ├── blizzard/
    │   ├── client.py              # OAuth e helpers HTTP Blizzard
    │   ├── models.py
    │   ├── sync_races.py
    │   ├── sync_race_classes.py
    │   ├── sync_class_specs.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── migrations/
    │   └── management/commands/
    │       ├── sync_playable_races.py
    │       ├── sync_playable_race_classes.py
    │       └── sync_playable_class_specs.py
    ├── config/                    # settings, urls raiz
    ├── manage.py
    └── .env.example
```

## Configuração local

```bash
cd backend
cp .env.example .env
# Edite .env: DJANGO_SECRET_KEY, BNET_*, CRON_SYNC_SECRET

poetry install
poetry run python manage.py migrate
poetry run python manage.py sync_playable_races
poetry run python manage.py sync_playable_race_classes
poetry run python manage.py sync_playable_class_specs
poetry run python manage.py runserver
```

## Variáveis de ambiente

Veja `backend/.env.example`. Principais:

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DJANGO_SECRET_KEY` | Sim | Chave secreta do Django |
| `BNET_CLIENT_ID` | Sim (sync) | Client ID Blizzard |
| `BNET_CLIENT_SECRET` | Sim (sync) | Client Secret Blizzard |
| `CRON_SYNC_SECRET` | Sim (POST sync) | Token Bearer para endpoints de sincronização |
| `DATABASE_URL` | Prod | URL Postgres; omitir usa SQLite |
| `ALLOWED_HOSTS` | Prod | Hosts permitidos, separados por vírgula |
| `DJANGO_DEBUG` | Não | `0` em produção |

## API HTTP

Base: `/api/`

### Leitura (front)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/wow/playable-race/index` | Lista raças: `id`, `name`, `faction` |
| GET | `/wow/playable-race/{race_id}/playable-classes/index` | Raça + `playable_classes[]` (`class_id`, `name`, `image`) |
| GET | `/playable-classes/specs/index` | Todas as classes com `specializations[]` (`id`, `name`, `image`) |
| GET | `/playable-classes/{class_id}/specs/` | Uma classe com `specializations[]` (mesmo formato de item do index) |

Exemplo — classes por raça:

```http
GET /api/wow/playable-race/10/playable-classes/index
```

```json
{
  "id": 10,
  "race_id": 10,
  "race_name": "Elfo Sangrento",
  "faction": "Horda",
  "playable_classes": [
    { "class_id": 2, "name": "Paladino", "image": "https://render.worldofwarcraft.com/..." }
  ]
}
```

Exemplo — classes e specs (lista):

```http
GET /api/playable-classes/specs/index
```

```json
[
  {
    "id": 2,
    "name": "Paladino",
    "image": "https://render.worldofwarcraft.com/...",
    "specializations": [
      { "id": 65, "name": "Proteção", "image": "https://render.worldofwarcraft.com/..." }
    ]
  }
]
```

Exemplo — uma classe e suas specs:

```http
GET /api/playable-classes/2/specs/
```

```json
{
  "id": 2,
  "name": "Paladino",
  "image": "https://render.worldofwarcraft.com/...",
  "specializations": [
    { "id": 65, "name": "Proteção", "image": "https://render.worldofwarcraft.com/..." },
    { "id": 66, "name": "Sagrado", "image": "https://render.worldofwarcraft.com/..." },
    { "id": 70, "name": "Retribuição", "image": "https://render.worldofwarcraft.com/..." }
  ]
}
```

**Erros `404` (leitura):**

| Rota | Motivo |
|------|--------|
| `/playable-classes/specs/index` | Nenhuma classe/spec sincronizada ainda |
| `/playable-classes/{class_id}/specs/` | Classe inexistente, ou specs ainda não sincronizadas para essa classe |
| `/wow/playable-race/{race_id}/playable-classes/index` | Raça inexistente, ou classes da raça ainda não sincronizadas |

### Sincronização (cron — requer Bearer)

Header: `Authorization: Bearer <CRON_SYNC_SECRET>`

| Método | Rota | Resposta |
|--------|------|----------|
| POST | `/wow/playable-race/sync` | `{"synced": N}` |
| POST | `/wow/playable-race/playable-classes/sync` | `{"races": N, "classes": M}` |
| POST | `/playable-classes/specs/sync` | `{"classes": N, "specializations": M}` |

**Ordem recomendada no cron:**

1. Raças (`/wow/playable-race/sync`)
2. Classes por raça (`/wow/playable-race/playable-classes/sync`) — depende de raças no banco
3. Classes e specs globais (`/playable-classes/specs/sync`) — independente de raças

```bash
curl -X POST https://SEU_HOST/api/wow/playable-race/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/wow/playable-race/playable-classes/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/playable-classes/specs/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"
```

Equivalente CLI:

```bash
poetry run python manage.py sync_playable_races
poetry run python manage.py sync_playable_race_classes
poetry run python manage.py sync_playable_class_specs
```

Opções do sync de specs:

```bash
poetry run python manage.py sync_playable_class_specs \
  --namespace static-us \
  --locale pt_BR \
  --spec-media-locale en_US
```

## Deploy (produção)

1. Definir variáveis de ambiente (sem commitar `.env`).
2. `python manage.py migrate --noinput`
3. Subir app (ex.: Gunicorn + `config.wsgi`)
4. Executar sync inicial (cron ou commands acima)
5. Validar leitura: `GET .../wow/playable-race/index`, `GET .../playable-classes/specs/index` e `GET .../playable-classes/{class_id}/specs/`

## Licença

Ver [LICENSE](LICENSE).
