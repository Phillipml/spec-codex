# spec-codex

Backend de integração com a **Blizzard Game Data API** (World of Warcraft) para servir dados de raças e classes jogáveis ao front-end. Os dados são sincronizados periodicamente para o banco local; as rotas públicas de leitura **não** chamam a Blizzard em tempo real.

## Descrição do projeto

API REST em Django que:

1. Autentica na Blizzard com **Client Credentials** (OAuth).
2. Sincroniza **raças jogáveis** (`playable_races`) e, para cada raça, as **classes permitidas** com ícone (`playable_race_classes`).
3. Expõe endpoints de leitura para o front montar fluxos de criação de personagem (escolha de raça → classes da raça).

O front consome apenas `GET` no backend; atualização dos dados fica a cargo de cron job ou commands de management.

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
- Tabelas explícitas: `playable_races` e `playable_race_classes`, com `race_id` / `(race, class_id)` alinhados aos IDs da Blizzard.
- `synced_at` em ambos os modelos para rastrear última escrita no sync.
- Leitura do front sempre via ORM (rápida, sem rate limit da Blizzard no caminho crítico).

### Integração com API (não é LLM)

Não há integração com LLM neste repositório. A “inteligência” do fluxo é:

- **Sync (escrita):** cron ou CLI chama Blizzard → persiste no banco.
- **Index (leitura):** front chama Django → resposta montada do banco.

Credenciais: `BNET_CLIENT_ID` e `BNET_CLIENT_SECRET`. Token obtido em `BNET_TOKEN_URL`; dados em `BNET_API_BASE` (padrão `https://us.api.blizzard.com`).

Fluxo de classes por raça:

1. `GET /data/wow/playable-race/{id}` → lista `playable_classes`.
2. Para cada classe, `GET /data/wow/media/playable-class/{class_id}` → URL do ícone (`assets[key=icon]`).
3. `update_or_create` em `playable_race_classes`; remove classes que deixaram de existir na API para aquela raça.

### Multi-tenancy

**Não aplicável** nesta fase: API single-tenant, dados globais do jogo (sem isolamento por usuário/organização). Se o produto evoluir para contas/tenants, seria camada futura acima deste cache estático.

### Desafios encontrados

| Desafio | Solução |
|---------|---------|
| Volume de chamadas (raças × classes) | Um `httpx.Client` reutilizado no sync em lote; token OAuth uma vez por execução de sync por raça no loop interno |
| Classe **Aventureiro** (id 14) na API sem endpoint de mídia (404) | Ignorada no sync (`_SKIP_CLASS_IDS`); não aparece no front |
| Ordem do cron | Sync de **raças** antes de **classes** (`sync_all` lê `PlayableRace` do banco) |
| `synced_at` no model sem migration aplicada | Rodar `python manage.py migrate` |
| Proteção do sync | `POST` de sync exige `Authorization: Bearer <CRON_SYNC_SECRET>` |

## Funcionalidades implementadas

### Obrigatórias

- [x] Listagem de raças jogáveis (`GET /api/wow/playable-race/index`)
- [x] Sync de raças a partir da Blizzard (`POST /api/wow/playable-race/sync` + command `sync_playable_races`)
- [x] Classes jogáveis por raça com nome, facção da raça e ícone (`GET /api/wow/playable-race/{race_id}/playable-classes/index`)
- [x] Sync de todas as classes de todas as raças no banco (`POST /api/wow/playable-race/playable-classes/sync` + command `sync_playable_race_classes`)
- [x] Persistência em `playable_races` e `playable_race_classes`
- [x] Exclusão da classe Aventureiro (id 14) no sync

### Diferenciais / operação

- [x] Management commands para sync local e CI
- [x] Suporte a Postgres em produção via `DATABASE_URL`
- [x] Locale `pt_BR` e namespace `static-us` configuráveis nos syncs

### Fora do escopo (por enquanto)

- [ ] Front-end neste repositório
- [ ] Testes automatizados
- [ ] Endpoint único “sync completo” (raças + classes em um POST)
- [ ] LLM / multi-tenancy

## Estrutura do repositório

```
spec-codex/
├── README.md
└── backend/
    ├── blizzard/          # app Django (models, sync, views, API)
    ├── config/            # settings, urls raiz
    ├── manage.py
    └── .env.example
```

## Configuração local

```bash
cd backend
cp .env.example .env
# Edite .env com DJANGO_SECRET_KEY, BNET_* e opcionalmente CRON_SYNC_SECRET

poetry install
poetry run python manage.py migrate
poetry run python manage.py sync_playable_races
poetry run python manage.py sync_playable_race_classes
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

Exemplo:

```http
GET /api/wow/playable-race/10/playable-classes/index
```

Resposta (estrutura):

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

### Sincronização (cron — requer Bearer)

Header: `Authorization: Bearer <CRON_SYNC_SECRET>`

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/wow/playable-race/sync` | Atualiza todas as raças → `{"synced": N}` |
| POST | `/wow/playable-race/playable-classes/sync` | Atualiza classes de todas as raças → `{"races": N, "classes": M}` |

**Ordem recomendada no cron:** raças primeiro, depois classes.

```bash
curl -X POST https://SEU_HOST/api/wow/playable-race/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"

curl -X POST https://SEU_HOST/api/wow/playable-race/playable-classes/sync \
  -H "Authorization: Bearer SEU_CRON_SYNC_SECRET"
```

Equivalente CLI:

```bash
poetry run python manage.py sync_playable_races
poetry run python manage.py sync_playable_race_classes
```

## Deploy (produção)

1. Definir variáveis de ambiente (sem commitar `.env`).
2. `python manage.py migrate --noinput`
3. Subir app (ex.: Gunicorn + `config.wsgi`)
4. Executar sync inicial (cron ou commands acima)
5. Validar `GET .../playable-race/10/playable-classes/index`

## Licença

Ver [LICENSE](LICENSE).
