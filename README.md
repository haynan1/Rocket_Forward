# 🚀 Rocket Forward

> Um pequeno painel para transformar coisas que você quer fazer em missões do dia.

Pense assim: você escreve uma missão, faz a missão e ganha XP. É como cuidar de um foguete: um passinho por vez leva você mais longe. 🌟

## ✨ O que dá para fazer?

- Criar metas para hoje ou para outro dia.
- Marcar metas como **pendente**, **em andamento** ou **concluída**.
- Repetir uma meta em dias úteis, finais de semana ou todos os dias.
- Ver as missões de hoje no **Início** e na **Esteira**.
- Ganhar XP e desbloquear conquistas ao concluir missões.
- Acompanhar sequência, histórico e relatórios.

## ▶️ Como abrir o foguete

Você vai precisar de um computador com **Python 3.10 ou mais novo** instalado.

### 1. Prepare a chave secreta

Na pasta do projeto, faça uma cópia do arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Agora abra o arquivo `.env` com o Bloco de Notas e coloque uma chave depois de `SECRET_KEY=`.

Para criar uma chave, rode este comando e copie o resultado:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Exemplo de como o começo do `.env` deve ficar:

```env
SECRET_KEY=cole_a_chave_grande_aqui
```

> Não mostre essa chave para outras pessoas. Ela é a senha da porta do foguete.

### 2. Ligue o programa

```powershell
python run.py
```

Na primeira vez, o projeto prepara sozinho uma caixinha com as ferramentas de que precisa (`venv`) e instala tudo.

### 3. Abra no navegador

Com o programa ligado, abra:

```text
http://127.0.0.1:5000
```

Pronto! Crie sua conta e escolha uma primeira missão.

Para parar o programa, volte ao terminal e aperte `Ctrl + C`.

### Esqueceu a senha?

Na tela de entrada, clique em **Esqueci minha senha**. O Rocket Forward envia um link que vale por uma hora para você criar uma nova senha.

No computador local, configure as opções `SMTP_...` no arquivo `.env` para receber esse link por e-mail. Sem e-mail configurado, o programa registra o link temporário apenas no terminal.

## 🧑‍🚀 Como usar

1. Clique em **Nova meta**.
2. Escreva uma coisa pequena para fazer, como “Ler 10 páginas”.
3. A data começa em **hoje**. Você pode trocar se quiser.
4. Salve a meta.
5. Quando terminar, marque o círculo da meta.
6. Veja o XP, a sequência e as conquistas crescerem.

### O que cada tela faz?

| Tela | Para que serve |
| --- | --- |
| **Início** | Mostra as missões de hoje. |
| **Metas** | Mostra todas as suas metas e permite filtrar. |
| **Esteira** | Organiza somente as metas de hoje em colunas de status. |
| **Plano** | Mostra as metas da semana ou do mês. |
| **Histórico** | Mostra seu avanço recente. |
| **Perfil** | Altera nome, foto, tema e preferências. |

## 🏆 XP e conquistas

- Criar uma meta pode desbloquear conquistas de criação, como **Primeiro lançamento**.
- Concluir uma meta dá XP.
- Concluir missões em dias seguidos cria uma sequência.
- Quando uma conquista é desbloqueada, um aviso aparece na tela.

## 👨‍🔧 Para quem cuida do projeto

### Rodar os testes

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

### Usar uma conta de demonstração

Depois de executar o projeto uma vez:

```powershell
.\venv\Scripts\python.exe -m flask --app run.py demo-user
```

Entre com:

```text
E-mail: demo@rocket.forward
Senha: foguete123
```

### Onde as coisas ficam?

| Pasta ou arquivo | O que guarda |
| --- | --- |
| `app/blueprints/` | As páginas e as rotas do sistema. |
| `app/models/` | Os formatos dos dados, como usuário e meta. |
| `app/services/` | As regras de XP, sequência, recorrência e conquistas. |
| `app/templates/` | As telas em HTML. |
| `app/static/` | Cores, estilos, JavaScript e imagens. |
| `tests/` | Testes automáticos. |
| `instance/rocket_forward.db` | O banco local com as informações do programa. |

### Banco de dados

Por padrão, o Rocket Forward guarda os dados no próprio computador usando SQLite. Para uma instalação maior, é possível trocar para PostgreSQL no arquivo `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/rocket_forward
```

As atualizações do banco são aplicadas automaticamente ao iniciar o projeto.

### Modo de demonstração

No `.env`, esta opção deixa o botão Premium funcionar sem pagamento real:

```env
DEMO_MODE=1
```

Em um sistema de verdade com pagamento, use `DEMO_MODE=0`.

## 💾 Cuide dos seus dados

Como o banco é local, fazer uma cópia deste arquivo protege suas metas:

```text
instance/rocket_forward.db
```

É só copiar esse arquivo para uma pasta segura de vez em quando. Assim, se algo acontecer com o computador, sua jornada continua. 🚀
