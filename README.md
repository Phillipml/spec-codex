# spec-codex

Backend de integração com a **Blizzard Game Data API** (World of Warcraft) para servir dados de raças, classes por raça, especializações (specs) e detalhes de cada spec (descrição, papel e habilidades PvP) ao front-end. Os dados são sincronizados periodicamente para o banco local; as rotas públicas de leitura **não** chamam a Blizzard em tempo real.

## Descrição do projeto

API REST em Django que:

1. Autentica na Blizzard com **Client Credentials** (OAuth).
2. Sincroniza **raças jogáveis** (`playable_races`).
3. Para cada raça, sincroniza as **classes permitidas** com ícone (`playable_race_classes`).
4. Sincroniza **classes globais** e suas **especializações** com ícones (`playable_classes`, `playable_class_specializations`).
5. Sincroniza **detalhes de cada spec**: descrição, papel (tank/healer/dps) e **skills PvP** com tooltip e ícone de spell (`playable_class_specialization_skills`).
6. Expõe endpoints de leitura para o front montar o fluxo de criação de personagem:

   **raça** → **classes da raça** → **specs no contexto da raça** → **detalhe de uma spec**

   Há também um catálogo global **classe → specs** (`/playable-classes/specs`), útil para referência ou telas que não dependem de `race_id`.

O front consome apenas `GET` no backend; atualização dos dados fica a cargo de cron job ou management commands.

### Convenção de rotas da API pública

Rotas de leitura sob `/api/`, sem prefixo `/wow` e sem sufixo `/index` nas listagens:

| Recurso | Rota |
|---------|------|
| Raças | `GET /api/playable-race/index` |
| Classes por raça | `GET /api/playable-race/{race_id}/playable-classes` |
| Specs (raça + classe) | `GET /api/playable-race/{race_id}/playable-classes/{class_id}/specs/` |
| Detalhe de uma spec | `GET /api/playable-race/{race_id}/playable-classes/{class_id}/specs/{spec_id}/` |
| Catálogo global classe/specs | `GET /api/playable-classes/specs` |

O endpoint de specs exige `race_id` e `class_id`: valida em `playable_race_classes` se a classe é permitida para a raça e enriquece com dados de `playable_classes` e `playable_class_specializations`.

O endpoint de detalhe de spec valida raça + classe da mesma forma e retorna `description`, `type` (papel) e `skills[]` (talentos PvP com tooltip).

## Tecnologias utilizadas

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.14+ |
| Framework | Django 6, Django REST Framework |
| HTTP cliente | httpx (com retry exponencial em `get_with_retry`) |
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
- Cinco tabelas de domínio, com nomes explícitos via `db_table`:

| Tabela | Modelo | Propósito |
|--------|--------|-----------|
| `playable_races` | `PlayableRace` | Raças (`race_id` único da Blizzard) |
| `playable_race_classes` | `PlayableRaceClass` | Classes permitidas por raça (N:N materializado) |
| `playable_classes` | `PlayableClass` | Classes globais com ícone |
| `playable_class_specializations` | `PlayableClassSpecialization` | Specs por classe (`description`, `role_name`, ícone) |
| `playable_class_specialization_skills` | `PlayableClassSpecializationSkill` | Skills PvP por spec (tooltip + ícone de spell) |

- `synced_at` em todos os modelos (`auto_now=True`) para rastrear última escrita no sync.
- Leitura do front sempre via ORM, com `prefetch_related` / `select_related` onde há relação pai-filho (specs, skills).
- **Migrations versionadas no Git** — toda alteração de schema via `manage.py makemigrations` / `migrate`.

### Integração com API (não é LLM)

Não há integração com LLM neste repositório. O padrão é **cache local**:

- **Sync (escrita):** cron ou CLI chama Blizzard → persiste no banco (`update_or_create` + remoção de registros órfãos).
- **Index (leitura):** front chama Django → resposta montada do banco.

Credenciais: `BNET_CLIENT_ID` e `BNET_CLIENT_SECRET`. Token em `BNET_TOKEN_URL`; dados em `BNET_API_BASE` (padrão `https://us.api.blizzard.com`).

Chamadas HTTP no sync usam `get_with_retry` (`client.py`): até 5 tentativas com backoff exponencial para status `429`, `502`, `503`, `504` e erros de rede (`ConnectError`, timeouts, etc.).

**Raças** (`sync_races.py`):

1. `GET /data/wow/playable-race/index` → itera raças.
2. Por raça: `GET` no `href` do detalhe → nome e facção (traduzida para pt quando possível).
3. Persiste em `playable_races`.

**Classes por raça** (`sync_race_classes.py`):

1. `GET /data/wow/playable-race/{id}` → lista `playable_classes`.
2. Para cada classe, `GET /data/wow/media/playable-class/{class_id}` → ícone (`assets[key=icon]`).
3. Persiste em `playable_race_classes`; remove classes que saíram da API para aquela raça.

**Classes e specs globais** (`sync_class_specs.py`):

1. `GET /data/wow/playable-class/index` → itera classes.
2. Por classe: `GET /data/wow/playable-class/{id}` (detalhe + lista de `specializations`) e mídia da classe.
3. Por spec: `GET /data/wow/media/playable-specialization/{spec_id}` → ícone.
4. Persiste em `playable_classes` e `playable_class_specializations`; remove specs órfãs por classe.

**Detalhes de specs** (`sync_spec_details.py`):

1. `GET /data/wow/playable-specialization/index` → itera specs.
2. Por spec: `GET /data/wow/playable-specialization/{id}` → `gender_description`, `role`, `pvp_talents`.
3. Mídia da spec: `GET /data/wow/media/playable-specialization/{spec_id}`.
4. Por talento PvP: `GET /data/wow/pvp-talent/{id}` → `spell.id` → `GET /data/wow/media/spell/{spell_id}` para ícone.
5. Persiste `description`, `role_name` e skills em `playable_class_specializations` / `playable_class_specialization_skills`; remove skills órfãs por spec.

Locale padrão: `pt_BR` para nomes e tooltips; mídia de specs e spells usa `en_US` por padrão (`spec_media_locale`, `spell_media_locale`), pois a API de mídia costuma responder melhor nesse locale.

### Multi-tenancy

**Não aplicável** nesta fase: API single-tenant, dados globais do jogo (sem isolamento por usuário/organização). Se o produto evoluir para contas/tenants, seria camada futura acima deste cache estático.

### Desafios encontrados

| Desafio | Solução |
|---------|---------|
| Volume de chamadas (raças × classes × specs × skills) | `httpx.Client` reutilizado no sync em lote; token OAuth por execução de sync |
| Rate limit / instabilidade da API Blizzard | `get_with_retry` com backoff exponencial (até 5 tentativas) |
| Classe **Aventureiro** (id 14) sem mídia útil / fora do criador padrão | Ignorada no sync (`_SKIP_CLASS_IDS` em `sync_race_classes`, `sync_class_specs` e `sync_spec_details`) |
| Ordem do cron para dados por raça | Sync de **raças** antes de **classes por raça** (`sync_all` lê `PlayableRace` do banco) |
| Specs independentes de raça | Sync de classes/specs e de detalhes pode rodar após raças; não depende de `playable_races` |
| Ícone de skill PvP não vem no payload da spec | Resolução em duas etapas: `pvp-talent/{id}` → `media/spell/{spell_id}` |
| Proteção dos endpoints de sync | `POST` exige `Authorization: Bearer <CRON_SYNC_SECRET>` (`secrets.compare_digest`) |
| Migrations no repositório | Commitar arquivos em `blizzard/migrations/` junto com alterações de `models.py` |

## Funcionalidades implementadas

### Obrigatórias

- [x] Listagem de raças jogáveis (`GET /api/playable-race/index`)
- [x] Sync de raças (`POST /api/playable-race/sync` + `sync_playable_races`)
- [x] Classes jogáveis por raça com nome e ícone (`GET /api/playable-race/{race_id}/playable-classes`)
- [x] Sync de classes por raça (`POST /api/playable-race/playable-classes/sync` + `sync_playable_race_classes`)
- [x] Listagem de classes com especializações e ícones (`GET /api/playable-classes/specs`)
- [x] Raça + classe + specs unificados (`GET /api/playable-race/{race_id}/playable-classes/{class_id}/specs/`)
- [x] Sync de classes e specs (`POST /api/playable-classes/specs/sync` + `sync_playable_class_specs`)
- [x] Detalhe de spec com descrição, papel e skills PvP (`GET /api/playable-race/{race_id}/playable-classes/{class_id}/specs/{spec_id}/`)
- [x] Sync de detalhes de specs (`POST /api/playable-classes/specs/details/sync` + `sync_playable_spec_details`)
- [x] Persistência nas cinco tabelas de domínio
- [x] Exclusão da classe Aventureiro (id 14) nos syncs

### Diferenciais / operação

- [x] Management commands para sync local e CI
- [x] Suporte a Postgres em produção via `DATABASE_URL`
- [x] Locale `pt_BR` e namespace `static-us` configuráveis nos commands (`--namespace`, `--locale`, `--spec-media-locale`, `--spell-media-locale`)
- [x] Tradução de facção (Aliança/Horda) a partir do payload da API
- [x] Retry automático em falhas transitórias da API Blizzard

### Fora do escopo (por enquanto)

- [ ] Front-end neste repositório
- [ ] Testes automatizados (`blizzard/tests.py` vazio)
- [ ] Endpoint único “sync completo” (raças + classes + specs + detalhes em um POST)
- [ ] LLM / multi-tenancy
- [ ] Django Admin registrado para os models

## Estrutura do repositório

```
spec-codex/
├── README.md
└── backend/
    ├── blizzard/
    │   ├── client.py              # OAuth, helpers HTTP e get_with_retry
    │   ├── models.py
    │   ├── sync_races.py
    │   ├── sync_race_classes.py
    │   ├── sync_class_specs.py
    │   ├── sync_spec_details.py   # description, role, skills PvP
    │   ├── views.py
    │   ├── urls.py
    │   ├── migrations/
    │   └── management/commands/
    │       ├── sync_playable_races.py
    │       ├── sync_playable_race_classes.py
    │       ├── sync_playable_class_specs.py
    │       └── sync_playable_spec_details.py
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
poetry run python manage.py sync_playable_spec_details
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

### Fluxo de leitura (criador de personagem)

```mermaid
flowchart LR
  A["GET /playable-race/index"] --> B["GET /playable-race/{race_id}/playable-classes"]
  B --> C["GET /playable-race/{race_id}/playable-classes/{class_id}/specs/"]
  C --> D["GET /playable-race/{race_id}/playable-classes/{class_id}/specs/{spec_id}/"]
  E["GET /playable-classes/specs"] -.->|catálogo global| F[Referência opcional]
```

| Passo | Rota | Tabelas consultadas |
|-------|------|---------------------|
| 1 | `GET /playable-race/index` | `playable_races` |
| 2 | `GET /playable-race/{race_id}/playable-classes` | `playable_races`, `playable_race_classes` |
| 3 | `GET /playable-race/{race_id}/playable-classes/{class_id}/specs/` | `playable_races`, `playable_race_classes` (validação), `playable_classes`, `playable_class_specializations` |
| 4 | `GET /playable-race/{race_id}/playable-classes/{class_id}/specs/{spec_id}/` | idem + `playable_class_specialization_skills` |

### Leitura (front)

| Método | Rota | View | Descrição |
|--------|------|------|-----------|
| GET | `/playable-race/index` | `PlayableRaceListView` | Lista raças: `id`, `name`, `faction` |
| GET | `/playable-race/{race_id}/playable-classes` | `PlayableRaceClassesListView` | Raça + `playable_classes[]` (`class_id`, `name`, `image`) |
| GET | `/playable-race/{race_id}/playable-classes/{class_id}/specs/` | `PlayableRaceClassSpecsDetailView` | Raça + objeto `class` com `specializations[]` |
| GET | `/playable-race/{race_id}/playable-classes/{class_id}/specs/{spec_id}/` | `PlayableRaceClassSpecDetailView` | Raça + `class` com `specialization` (detalhe + `skills[]`) |
| GET | `/playable-classes/specs` | `PlayableClassSpecsListView` | Catálogo global: todas as classes com `specializations[]` |

Exemplo — classes por raça:

```http
GET /api/playable-race/10/playable-classes
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

Exemplo — raça, classe e specs (fluxo do criador de personagem):

```http
GET /api/playable-race/70/playable-classes/13/specs/
```

```json
{
  "id": 70,
  "race_id": 70,
  "race_name": "Dracthyr",
  "faction": "Horda",
  "class": {
    "id": 13,
    "name": "Evocador",
    "image": "https://render.worldofwarcraft.com/...",
    "specializations": [
      { "id": 1467, "name": "Devastação", "image": "https://render.worldofwarcraft.com/..." },
      { "id": 1468, "name": "Preservação", "image": "https://render.worldofwarcraft.com/..." },
      { "id": 1473, "name": "Aprimoramento", "image": "https://render.worldofwarcraft.com/..." }
    ]
  }
}
```

Exemplo — detalhe de uma spec (descrição, papel e skills PvP):

```http
GET /api/playable-race/70/playable-classes/13/specs/1467/
```

```json
{
  "id": 70,
  "race_id": 70,
  "race_name": "Dracthyr",
  "faction": "Horda",
  "class": {
    "id": 13,
    "name": "Evocador",
    "image": "https://render.worldofwarcraft.com/...",
    "specialization": {
      "id": 1467,
      "name": "Devastação",
      "image": "https://render.worldofwarcraft.com/...",
      "description": "Dracthyr Evocadores que canalizam o poder dracônico...",
      "type": "Dano",
      "skills": [
        {
          "id": 12345,
          "name": "Nome do Talento",
          "image": "https://render.worldofwarcraft.com/...",
          "description": "Descrição do efeito...",
          "cast_time": "Instantâneo",
          "power_cost": "2 Poder Arcano",
          "range": "40 m",
          "cooldown": "45 s"
        }
      ]
    }
  }
}
```

Campos opcionais em `skills[]`: `power_cost`, `range`, `cooldown` — omitidos quando vazios.

**Erros `404` (leitura) — campo `detail`:**

| Rota | `detail` |
|------|----------|
| `/playable-race/{race_id}/playable-classes` | `"Raça não encontrada."` |
| `/playable-race/{race_id}/playable-classes` | `"Classes ainda não sincronizadas para esta raça."` |
| `/playable-classes/specs` | `"Classes e specs ainda não sincronizadas."` |
| `/playable-race/{race_id}/playable-classes/{class_id}/specs/` | `"Raça não encontrada."` |
| `/playable-race/{race_id}/playable-classes/{class_id}/specs/` | `"Classe não disponível para esta raça."` |
| `/playable-race/{race_id}/playable-classes/{class_id}/specs/` | `"Classe não encontrada."` |
| `/playable-race/{race_id}/playable-classes/{class_id}/specs/` | `"Specs ainda não sincronizadas para esta classe."` |
| `/playable-race/.../specs/{spec_id}/` | `"Raça não encontrada."` |
| `/playable-race/.../specs/{spec_id}/` | `"Classe não disponível para esta raça."` |
| `/playable-race/.../specs/{spec_id}/` | `"Spec não encontrada para esta classe."` |
| `/playable-race/.../specs/{spec_id}/` | `"Detalhes da spec ainda não sincronizados."` |

### Sincronização (cron — requer Bearer)

Header: `Authorization: Bearer <CRON_SYNC_SECRET>`

| Método | Rota | View | Resposta |
|--------|------|------|----------|
| POST | `/playable-race/sync` | `PlayableRaceSyncView` | `{"synced": N}` |
| POST | `/playable-race/playable-classes/sync` | `PlayableRaceClassesSyncView` | `{"races": N, "classes": M}` |
| POST | `/playable-classes/specs/sync` | `PlayableClassSpecsSyncView` | `{"classes": N, "specializations": M}` |
| POST | `/playable-classes/specs/details/sync` | `PlayableClassSpecDetailsSyncView` | `{"specializations": N, "skills": M}` |

**Ordem recomendada no cron:**

1. Raças (`/playable-race/sync`)
2. Classes por raça (`/playable-race/playable-classes/sync`) — depende de raças no banco
3. Classes e specs globais (`/playable-classes/specs/sync`) — independente de raças
4. Detalhes de specs (`/playable-classes/specs/details/sync`) — enriquece specs já existentes (pode rodar após o passo 3)

```bash
curl -X POST https://SEU_HOST/api/playable-race/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/playable-race/playable-classes/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/playable-classes/specs/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/playable-classes/specs/details/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"
```

Equivalente CLI:

```bash
poetry run python manage.py sync_playable_races
poetry run python manage.py sync_playable_race_classes
poetry run python manage.py sync_playable_class_specs
poetry run python manage.py sync_playable_spec_details
```

Opções do sync de specs e detalhes:

```bash
poetry run python manage.py sync_playable_class_specs \
  --namespace static-us \
  --locale pt_BR \
  --spec-media-locale en_US

poetry run python manage.py sync_playable_spec_details \
  --namespace static-us \
  --locale pt_BR \
  --spec-media-locale en_US \
  --spell-media-locale en_US
```

## Deploy (produção)

1. Definir variáveis de ambiente (sem commitar `.env`): `DJANGO_SECRET_KEY`, `BNET_*`, `CRON_SYNC_SECRET`, `DATABASE_URL`, `ALLOWED_HOSTS`, `DJANGO_DEBUG=0`.
2. Instalar dependências e aplicar migrations:

```bash
cd backend
poetry install --no-dev
poetry run python manage.py migrate --noinput
```

3. Subir o app com Gunicorn:

```bash
poetry run gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

4. Executar sync inicial (cron ou commands da seção anterior), na ordem: raças → classes por raça → classes/specs globais → detalhes de specs.
5. Validar leitura pós-deploy:

```bash
curl https://SEU_HOST/api/playable-race/index
curl https://SEU_HOST/api/playable-race/70/playable-classes
curl https://SEU_HOST/api/playable-race/70/playable-classes/13/specs/
curl https://SEU_HOST/api/playable-race/70/playable-classes/13/specs/1467/
curl https://SEU_HOST/api/playable-classes/specs
```

6. Configurar cron jobs com as rotas POST documentadas acima.

## Licença

Ver [LICENSE](LICENSE).
