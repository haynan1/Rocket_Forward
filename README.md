# Rocket Forward — Planejamento Diário

Aplicação Flask de planejamento diário em português, com tema espacial, metas recorrentes, gamificação, histórico, API JSON e camada Premium demonstrativa.

## Organização

- `app/blueprints/`: rotas por domínio (autenticação, metas, páginas e API).
- `app/models/`: um módulo por entidade persistida.
- `app/services/`: regras de negócio (metas, recorrência, métricas e conquistas).
- `app/utils/`: constantes e datas no fuso de São Paulo, sem acoplamento ao Flask.
- `app/templates/` e `app/static/`: interface Jinja, CSS e JavaScript.
- `tests/`: testes de regras essenciais.

## Configuração

Copie `.env.example` para `.env` e gere uma chave própria — a aplicação não inicia sem `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Em produção, defina `FLASK_ENV=production` (força debug desligado e cookies de sessão só por HTTPS) e `DEMO_MODE=0` (desativa o botão de ativar Premium sem cobrança).

## Executar localmente

```powershell
python run.py
```

Na primeira execução, `run.py` cria automaticamente a `venv`, instala as
dependências de `requirements.txt` e inicia a aplicação usando esse ambiente.
Se quiser ativá-lo manualmente depois:

```powershell
.\venv\Scripts\Activate.ps1
```

Abra `http://127.0.0.1:5000`. Crie uma conta ou use o usuário demonstrativo:

```powershell
flask --app run.py demo-user
```

Credenciais: `demo@rocket.forward` / `foguete123`.

## Banco de dados

Por padrão, usa SQLite. Para PostgreSQL, defina em `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/rocket_forward
```

O esquema é versionado com Flask-Migrate/Alembic em `migrations/`. A aplicação roda
`flask db upgrade` automaticamente a cada boot (basta `python run.py`). Para criar uma
nova migração depois de alterar um modelo:

```powershell
flask --app run.py db migrate -m "descrição da mudança"
flask --app run.py db upgrade
```

## Testes

```powershell
pytest
```

Os testes cobrem limite gratuito, mudança de status, recorrência, XP/nível e isolamento de dados. O fuso de negócio é `America/Sao_Paulo`.

## API protegida

Após autenticação, estão disponíveis `GET/POST /api/goals`, `GET/PATCH/DELETE /api/goals/<id>`, `POST /api/goals/<id>/toggle-complete`, `POST /api/goals/<id>/cycle-status`, `/api/stats`, `/api/achievements`, `/api/reports/monthly` e `/api/profile`.

## Lembretes

O APScheduler é iniciado junto da aplicação e o modelo de notificações está incluído. O adaptador de envio é propositalmente local/mock nesta primeira versão: lembretes reais exigem configurar um provedor de e-mail/push e registrar os jobs a partir de `Notification`.
