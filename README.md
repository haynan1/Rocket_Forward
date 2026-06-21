# 🚀 Rocket Forward

> Um foguete de tarefas: você escreve uma missão, faz a missão e vê sua jornada crescer.

## 🌟 O que é isto?

O Rocket Forward ajuda você a lembrar das coisas que quer fazer.

Imagine que cada tarefa é uma pequena missão:

- “Ler um livro” 📚
- “Fazer a lição” ✏️
- “Beber água” 💧
- “Arrumar o quarto” 🧸

Quando você termina uma missão, marca como concluída. Assim, ganha XP, conquista medalhas e tenta manter uma sequência de dias produtivos.

## 🧭 O que tem no foguete?

| Lugar | O que ele faz |
| --- | --- |
| **Início** | Mostra as missões de hoje. |
| **Metas** | Mostra todas as suas missões e os filtros. |
| **Esteira** | Organiza as missões de hoje em “A fazer”, “Em andamento” e “Concluída”. |
| **Plano** | Mostra as missões da semana ou do mês. |
| **Histórico** | Mostra os dias em que você avançou. |
| **Perfil** | Guarda suas preferências, foto e tema. |
| **Conquistas** | Mostra as medalhas que você desbloqueou. |

## ▶️ Como abrir o Rocket Forward

Você precisa ter o **Python** instalado no computador. Python é uma ferramenta que faz o foguete funcionar.

### Passo 1: faça a chave secreta

Na pasta do Rocket Forward, copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Agora abra o arquivo chamado `.env` com o Bloco de Notas.

Crie uma chave com este comando:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado e coloque depois do sinal `=`:

```env
SECRET_KEY=cole_a_chave_grande_aqui
```

> A chave secreta é como a chave da porta de casa. Não mostre para outras pessoas.

### Passo 2: ligue o foguete

Abra o PowerShell dentro da pasta do projeto e escreva:

```powershell
python run.py
```

Na primeira vez, o projeto prepara sozinho uma caixinha de ferramentas chamada `venv`. Isso pode demorar alguns minutos. Depois, é só esperar a mensagem de que o servidor está funcionando.

### Passo 3: abra a página

Abra o navegador e visite:

```text
http://127.0.0.1:5000
```

Pronto! Agora você pode criar uma conta e começar sua jornada. ✨

## 🧑‍🚀 Como brincar de missões

1. Clique em **Nova meta**.
2. Escreva uma missão pequena, por exemplo: “Guardar os brinquedos”.
3. A data começa em **hoje**.
4. Clique em **Salvar meta**.
5. Quando terminar, marque o círculo da missão.
6. Veja seu XP e suas conquistas crescerem.

### O que significam os status?

- **Pendente:** ainda não começou.
- **Em andamento:** você está fazendo.
- **Concluída:** você terminou. 🎉

Na **Esteira**, você pode arrastar as missões entre essas três colunas.

### Metas que se repetem

Você pode dizer que uma missão acontece:

- Só uma vez.
- Em dias úteis.
- Nos finais de semana.
- Por alguns dias.
- Todos os dias.

O Rocket Forward mostra apenas os campos que você precisa para cada escolha. Assim a tela não fica cheia de coisas sem utilidade.

### Missões sem prazo

Algumas coisas não precisam ser feitas em um dia certo, como “Estudar inglês”.

No **Perfil**, existe a opção:

```text
Metas sem prazo na Esteira
```

Se ligar essa opção, essas missões também aparecem na Esteira. Se deixar desligada, a Esteira mostra apenas as missões de hoje.

## ⭐ XP, sequência e conquistas

### XP

Você ganha XP quando conclui uma meta. Criar uma missão não dá XP, porque o prêmio é por fazer a missão.

### Sequência

Se você concluir pelo menos uma meta hoje, amanhã e depois amanhã, sua sequência cresce:

```text
Dia 1 → Dia 2 → Dia 3 🔥
```

O programa não precisa ficar ligado para contar a sequência. Ele guarda os dias que você concluiu missões e calcula tudo quando você abre o Rocket Forward de novo.

### Conquistas

Algumas ações dão medalhas, como criar a primeira meta ou concluir muitas missões. Quando uma conquista aparece, o Rocket Forward mostra um aviso na tela.

## 💬 Frases motivacionais

No Perfil, você pode ligar ou desligar as frases motivacionais.

Quem tem **Premium** também pode:

- Ver as frases que já existem.
- Criar frases próprias.
- Apagar as frases próprias.
- Escolher se elas mudam a cada 1, 5, 15, 30 ou 60 minutos.

As frases aparecem no Início e trocam sozinhas enquanto a página está aberta.

## 👑 O que é Premium?

Premium é a parte especial do foguete. Nesta versão de demonstração, ela pode ser ligada sem pagar de verdade.

Ela libera recursos como:

- Frases personalizadas.
- Escolha do tempo de troca das frases.
- Lembretes.

No arquivo `.env`, esta opção deixa o botão de demonstração ligado:

```env
DEMO_MODE=1
```

## 🔐 Esqueci minha senha

Na tela de entrada, clique em **Esqueci minha senha**.

O sistema cria um link que vale por uma hora para você criar outra senha.

Para receber o link por e-mail, um adulto precisa configurar as opções `SMTP_...` no arquivo `.env`. Sem essa configuração, o link aparece apenas no terminal onde o Rocket Forward está rodando.

## 🖼️ Imagens do login

As imagens do fundo da tela de entrada ficam aqui:

```text
app/static/images/login/
```

Elas trocam automaticamente a cada 30 segundos. O formulário fica em cima com uma camada escura para você conseguir ler tudo.

## 💾 Onde ficam as missões?

As informações ficam guardadas neste arquivo:

```text
instance/rocket_forward.db
```

Esse arquivo é como o baú onde ficam suas metas, perfil e progresso.

Faça uma cópia dele de vez em quando para uma pasta segura ou um pendrive. Assim suas missões ficam protegidas.

## 🪟 Ligar junto com o computador

> **Isto é opcional.** O Rocket Forward não precisa de nenhum arquivo `.bat` para funcionar. Para usar normalmente, basta abrir o terminal e executar `python run.py`.

Existe um arquivo chamado:

```text
iniciar_rocket_forward.bat
```

Ele liga o Rocket Forward minimizado.

Para fazer isso acontecer sempre que o Windows ligar:

1. Clique com o botão direito em `iniciar_rocket_forward.bat`.
2. Escolha **Criar atalho**.
3. Aperte `Windows + R`.
4. Escreva `shell:startup` e aperte `Enter`.
5. Coloque o atalho dentro da pasta que abriu.

> Primeiro, rode `python run.py` uma vez para confirmar que tudo está funcionando.

## 🛑 Parar o Rocket Forward

> **Isto também é opcional.** O jeito mais simples de parar o sistema é apertar `Ctrl + C` no terminal que está aberto. Os scripts abaixo são só ajudantes para quem prefere clicar em um arquivo.

Se o terminal do Rocket Forward estiver aberto, aperte:

```text
Ctrl + C
```

Também existe este ajudante:

```text
parar_servidor_flask.bat
```

Ele procura quem está usando a porta `5000`, mostra o nome do processo e pergunta se você quer parar.

Para parar um programa em outra porta, use:

```powershell
.\parar_servidor_flask.ps1 -Port 5001
```

> Olhe o nome do processo antes de responder `S`. Assim você não para outro programa sem querer.

## 🧰 Para quem cuida do foguete

Esta parte é para adultos que gostam de mexer no código.

### Testar se está tudo bem

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

### Criar uma conta de demonstração

```powershell
.\venv\Scripts\python.exe -m flask --app run.py demo-user
```

Depois entre com:

```text
E-mail: demo@rocket.forward
Senha: foguete123
```

### Onde ficam as peças do foguete?

| Pasta | Para que serve |
| --- | --- |
| `app/blueprints/` | As páginas e os caminhos do site. |
| `app/models/` | Os formatos das informações guardadas. |
| `app/services/` | As regras de metas, XP, frases e conquistas. |
| `app/templates/` | As telas que aparecem no navegador. |
| `app/static/` | Cores, animações, JavaScript e imagens. |
| `migrations/` | As mudanças no baú de dados. |
| `tests/` | Os testes automáticos. |

### Banco de dados maior

Por padrão, o projeto usa o banco local SQLite. Um adulto pode trocar para PostgreSQL no `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/rocket_forward
```

As mudanças necessárias no banco são aplicadas automaticamente quando o projeto liga.

---

Feito um pequeno passo hoje? Então seu foguete já está indo para frente. 🚀
