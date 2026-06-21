from flask import request
from flask_login import current_user

LOCALE_COOKIE = 'locale'


EN_US = {
    'Início': 'Home', 'Metas': 'Goals', 'Esteira': 'Board', 'Plano': 'Plan', 'Histórico': 'History', 'Perfil': 'Profile',
    'Rocket Premium': 'Rocket Premium', 'Sair': 'Sign out', 'Nova meta': 'New goal', 'Voltar': 'Back',
    'Título': 'Title', 'Descrição': 'Description', 'Data': 'Date', 'Horário': 'Time', 'Repetição': 'Repeat',
    'Prioridade': 'Priority', 'Categoria': 'Category', 'Status': 'Status', 'Tema': 'Theme', 'Nome': 'Name',
    'Salvar meta': 'Save goal', 'Salvar preferências': 'Save preferences', 'Editar': 'Edit', 'Remover': 'Delete',
    'Pendente': 'Pending', 'Em andamento': 'In progress', 'Concluída': 'Completed', 'Concluídas': 'Completed',
    'Não repetir': 'Do not repeat', 'Dias úteis': 'Weekdays', 'Finais de semana': 'Weekends',
    'Por quantidade de dias': 'For a number of days', 'Todos os dias continuamente': 'Every day continuously',
    'Quantidade de dias': 'Number of days', 'Até a data': 'Until date', 'Hoje': 'Today', 'Sem prazo': 'No due date',
    'A fazer': 'To do', 'Missão do dia': 'Today’s mission', 'Suas metas de hoje': 'Your goals for today',
    'Ver todas': 'View all', 'Criar primeira meta': 'Create your first goal', 'Nada para hoje.': 'Nothing for today.',
    'Nada no backlog.': 'Nothing in the backlog.', 'Backlog sem prazo': 'No-due-date backlog',
    'Frases motivacionais': 'Motivational quotes', 'Lembretes': 'Reminders', 'Idioma': 'Language',
    'Português (Brasil)': 'Portuguese (Brazil)', 'Inglês (Estados Unidos)': 'English (United States)',
    'Mostrar esta meta na Esteira': 'Show this goal on the Board', 'Mostrar metas sem prazo na Esteira': 'Show no-due-date goals on the Board',
    'Você escolhe o que entra no seu fluxo.': 'You choose what enters your workflow.',
    'Esta meta tem prazo para concluir': 'This goal has a due date', 'Quando fazer': 'When to do it',
    'Como essa meta se repete?': 'How does this goal repeat?', 'Organização': 'Organization',
    'opcional': 'optional', 'Claro': 'Light', 'Escuro': 'Dark', 'Personalizar frases e intervalo': 'Customize quotes and interval',
    'Ajustar frases e intervalo': 'Adjust quotes and interval', 'Recursos Premium': 'Premium features',
    'Pronto para decolar?': 'Ready for takeoff?', 'Entre e transforme suas intenções em trajetória.': 'Sign in and turn your intentions into a journey.',
    'E-mail': 'Email', 'Senha': 'Password', 'Entrar na missão': 'Start the mission', 'Esqueci minha senha': 'Forgot my password?',
    'Novo por aqui?': 'New here?', 'Criar conta': 'Create account', 'Inicie sua missão': 'Start your mission',
    'Seu nome': 'Your name', 'Criar minha conta': 'Create my account', 'Já tem conta?': 'Already have an account?',
    'Vamos recuperar': 'Let’s recover it', 'Nova senha': 'New password', 'Repita a nova senha': 'Repeat your new password',
    'Enviar link de recuperação': 'Send recovery link', 'Salvar nova senha': 'Save new password',
    'Conquistas': 'Achievements', 'Relatórios': 'Reports', 'Filtrar': 'Filter', 'Limpar': 'Clear',
    'Todos os status': 'All statuses', 'Todas prioridades': 'All priorities', 'Todas categorias': 'All categories',
    'Meta salva com sucesso.': 'Goal saved successfully.', 'Perfil atualizado.': 'Profile updated.',
    'Conquista desbloqueada:': 'Achievement unlocked:', 'Não foi possível mover a meta.': 'Could not move the goal.',
}

# These are short labels stored in the database but shown directly in the UI.
EN_US.update({
    'baixa': 'low', 'media': 'medium', 'alta': 'high', 'estudos': 'studies', 'trabalho': 'work',
    'saude': 'health', 'financas': 'finances', 'espiritual': 'spiritual', 'pessoal': 'personal',
    'familia': 'family', 'empreendedorismo': 'entrepreneurship', 'outros': 'other',
    'Centro de comando': 'Command center', 'Organize cada impulso da sua jornada.': 'Organize every step of your journey.',
    'Fluxo de trabalho': 'Workflow', 'As colunas principais mostram apenas as metas de hoje.': 'The main columns show only today’s goals.',
    'Trajetória': 'Trajectory', 'Semana': 'Week', 'Mês': 'Month', 'Inicie sua missão': 'Start your mission',
    'Ajuste seu cockpit pessoal.': 'Adjust your personal cockpit.', 'Painel do astronauta': 'Astronaut panel',
    'Quando terminar, marque o círculo da missão.': 'When you finish, check the goal circle.',
    'Sem prazo, sem pressa': 'No due date, no rush', 'Metas criadas': 'Goals created', 'Metas concluídas': 'Goals completed',
    'Recorde de sequência': 'Best streak', 'Conquistas desbloqueadas': 'Achievements unlocked',
})

EN_US.update({
    'SUA JORNADA COMEÇA AQUI': 'YOUR JOURNEY STARTS HERE', 'PROGRESSO DE HOJE': 'TODAY’S PROGRESS',
    'Concluídas hoje': 'Completed today', 'Pendentes hoje': 'Pending today', 'Sequência atual': 'Current streak',
    'Rumo à órbita': 'On your way', 'Seu próximo avanço está a uma meta de distância.': 'Your next step is one goal away.',
    'O céu está livre': 'The sky is clear', 'Criar primeira meta': 'Create your first goal',
    'Crie sua primeira meta e dê ignição ao seu dia.': 'Create your first goal and start your day.',
    'Defina o próximo ponto no seu mapa estelar.': 'Set the next point on your map.',
    'Esta meta ficará na sua lista geral, sem aparecer como atrasada ou prevista para hoje.': 'This goal stays in your general list and will not be shown as overdue or due today.',
    'Ajuste os filtros ou crie uma nova meta.': 'Adjust the filters or create a new goal.', 'Nada neste radar': 'Nothing on the radar',
    'Pendentes': 'Pending', 'Média': 'Medium', 'Baixa': 'Low', 'Alta': 'High',
    'Uma leitura clara do seu ritmo.': 'A clear view of your pace.', 'Conclusões nos últimos 7 dias': 'Completions in the last 7 days',
    'Total concluído': 'Total completed', 'Recorde': 'Best streak', 'TELEMETRIA': 'TELEMETRY',
    'Planejamento': 'Planning', 'Nenhuma meta nesta janela.': 'No goals in this range.',
    'MARCO A MARCO': 'MILESTONE BY MILESTONE', 'Todo avanço deixa uma estrela no caminho.': 'Every step leaves a star on the path.',
    'Conclua uma meta para começar a desbloquear conquistas.': 'Complete a goal to start unlocking achievements.',
    'PREMIUM': 'PREMIUM', 'Troca automática': 'Automatic rotation', 'Uma frase sua': 'Your own quote',
    'Intervalo': 'Interval', 'Nova frase': 'New quote', 'Adicionar frase': 'Add quote', 'Salvar intervalo': 'Save interval',
    'BIBLIOTECA': 'LIBRARY', 'SUAS FRASES': 'YOUR QUOTES', 'Ainda não há frases personalizadas. Escreva a primeira acima.': 'There are no custom quotes yet. Write the first one above.',
    'Escolha as palavras que acompanham sua jornada.': 'Choose the words that join your journey.',
    'Escolha de quanto em quanto tempo a frase do Início muda.': 'Choose how often the Home quote changes.',
    'Ela entrará na rotação junto com as frases do Rocket Forward.': 'It will join the rotation with Rocket Forward quotes.',
    'Dados que aceleram sua jornada.': 'Data that speeds up your journey.', 'Evolução diária': 'Daily progress',
    'Metas previstas': 'Scheduled goals', 'XP acumulado': 'XP earned', 'Conhecer o Premium': 'Explore Premium',
    'Limpar todos os dados': 'Clear all data', 'Remover foto': 'Remove photo',
})

# Telas de autenticação (sem usuário logado) e suas mensagens de flash.
EN_US.update({
    'Pequenos passos. Grande impulso.': 'Small steps. Big momentum.', 'Astronauta': 'Astronaut',
    'Entrar': 'Sign in', 'Digite seu e-mail. Se ele estiver cadastrado, enviaremos um link para criar uma nova senha.':
        'Enter your email. If it has an account, we will send a link to create a new password.',
    'Voltar para entrar': 'Back to sign in', 'Escolha uma senha com pelo menos 8 caracteres.': 'Choose a password with at least 8 characters.',
    'E-mail ou senha inválidos.': 'Invalid email or password.',
    'Se esse e-mail tiver uma conta, enviaremos um link para criar uma nova senha.': 'If that email has an account, we will send a link to create a new password.',
    'Este link de recuperação expirou ou já foi usado. Peça outro.': 'This recovery link has expired or was already used. Request another one.',
    'A senha deve ter pelo menos 8 caracteres.': 'Password must be at least 8 characters long.',
    'As senhas não são iguais.': 'Passwords do not match.',
    'Senha alterada. Você está de volta à missão!': 'Password changed. You are back on the mission!',
    'Informe um e-mail válido.': 'Enter a valid email.', 'Este e-mail já está em uso.': 'This email is already in use.',
    'Conta criada. Sua missão começa agora!': 'Account created. Your mission starts now!',
})


def current_locale():
    try:
        if current_user.is_authenticated:
            return 'en-US' if current_user.locale == 'en-US' else 'pt-BR'
    except AttributeError:
        pass
    # Sem usuário autenticado (telas de login/cadastro/recuperação), cai para a
    # preferência salva em cookie na última sessão.
    return 'en-US' if request.cookies.get(LOCALE_COOKIE) == 'en-US' else 'pt-BR'


def translate(text):
    return EN_US.get(text, text) if current_locale() == 'en-US' else text
