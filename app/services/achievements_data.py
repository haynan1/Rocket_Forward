from ..utils.constants import GOAL_CATEGORIES

CATEGORY_TITLES = {
    'estudos': 'Mente em expansão', 'trabalho': 'Missão profissional', 'saude': 'Corpo em órbita',
    'financas': 'Cofre estelar', 'espiritual': 'Conexão com o cosmos', 'pessoal': 'Jornada interior',
    'familia': 'Tripulação de casa', 'empreendedorismo': 'Fundador de mundos', 'outros': 'Território inexplorado',
}
CATEGORY_ICONS = {
    'estudos': 'book-fill', 'trabalho': 'briefcase-fill', 'saude': 'heart-pulse-fill',
    'financas': 'piggy-bank-fill', 'espiritual': 'stars', 'pessoal': 'person-fill',
    'familia': 'people-fill', 'empreendedorismo': 'rocket-fill', 'outros': 'compass-fill',
}

def _tiers(prefix, group, icon, stat_key, desc_template, tiers):
    return [
        {
            'key': f'{prefix}_{threshold}', 'title': title, 'description': desc_template.format(n=threshold),
            'icon': icon, 'group': group, 'condition': (lambda ctx, t=threshold, sk=stat_key: ctx[sk] >= t),
        }
        for threshold, title in tiers
    ]

ACHIEVEMENT_DEFINITIONS = []

ACHIEVEMENT_DEFINITIONS += _tiers('created', 'Lançamentos', 'rocket-takeoff-fill', 'created', 'Crie {n} metas', [
    (1, 'Primeiro lançamento'), (5, 'Plataforma de lançamento'), (10, 'Em órbita'),
    (25, 'Velocidade de escape'), (50, 'Rumo à Lua'), (100, 'Cinturão de asteroides'),
    (200, 'Vizinhança de Marte'), (500, 'Sistema solar interior'), (1000, 'Espaço interestelar'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('completed', 'Conquistas', 'check-circle-fill', 'completed', 'Conclua {n} metas', [
    (1, 'Primeira conquista'), (5, 'Propulsão'), (10, 'Combustão total'), (25, 'Estágio 2'),
    (50, 'Órbita estável'), (100, 'Centena estelar'), (200, 'Constelação própria'),
    (500, 'Galáxia pessoal'), (1000, 'Lenda cósmica'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('streak', 'Sequência', 'fire', 'streak', 'Mantenha uma sequência de {n} dias', [
    (3, 'Ignição'), (5, 'Combustível estável'), (7, 'Semana estelar'), (14, 'Quinzena orbital'),
    (21, 'Hábito em órbita'), (30, 'Mês sem gravidade'), (60, 'Dois meses no espaço'),
    (90, 'Trimestre estelar'), (180, 'Meio ano além da atmosfera'), (365, 'Um ano ao redor do sol'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('record', 'Recorde', 'trophy-fill', 'record', 'Alcance um recorde de {n} dias seguidos', [
    (3, 'Marca pessoal'), (7, 'Recorde de uma semana'), (14, 'Recorde de duas semanas'),
    (30, 'Recorde de um mês'), (60, 'Recorde de dois meses'), (90, 'Recorde de um trimestre'),
    (180, 'Recorde de meio ano'), (365, 'Recorde de um ano'), (730, 'Recorde de dois anos'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('level', 'Nível', 'award-fill', 'level', 'Alcance o nível {n}', [
    (2, 'Decolagem'), (3, 'Subindo de órbita'), (5, 'Piloto júnior'), (10, 'Piloto'),
    (15, 'Comandante de missão'), (20, 'Capitão estelar'), (25, 'Almirante da frota'),
    (30, 'Explorador veterano'), (40, 'Navegador cósmico'), (50, 'Mestre do cosmos'),
    (75, 'Lenda da frota'), (100, 'Imperador das estrelas'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('focus_days', 'Disciplina', 'calendar-check-fill', 'productive_days', 'Tenha {n} dias produtivos', [
    (1, 'Primeiro dia produtivo'), (7, 'Semana de foco'), (14, 'Quinzena de foco'),
    (30, 'Mês de disciplina'), (60, 'Dois meses de disciplina'), (100, 'Cem dias produtivos'),
    (200, 'Duzentos dias produtivos'), (365, 'Um ano de disciplina'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('priority_alta', 'Prioridade', 'exclamation-circle-fill', 'priority_alta', 'Conclua {n} metas de prioridade alta', [
    (1, 'Primeira prioridade'), (5, 'Foco no essencial'), (10, 'Dez alvos críticos'),
    (25, 'Mestre das prioridades'), (50, 'Disciplina de elite'), (100, 'Cem missões críticas'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('priority_media', 'Prioridade', 'dash-circle-fill', 'priority_media', 'Conclua {n} metas de prioridade média', [
    (1, 'Equilíbrio inicial'), (10, 'Rotina estável'), (50, 'Constância média'),
])

ACHIEVEMENT_DEFINITIONS += _tiers('priority_baixa', 'Prioridade', 'circle-fill', 'priority_baixa', 'Conclua {n} metas de prioridade baixa', [
    (1, 'Sem pressa'), (10, 'Passo a passo'), (50, 'Leveza constante'),
])

for _cat in GOAL_CATEGORIES:
    ACHIEVEMENT_DEFINITIONS.append({
        'key': f'category_{_cat}', 'title': CATEGORY_TITLES[_cat],
        'description': f'Conclua uma meta na categoria {_cat}', 'icon': CATEGORY_ICONS[_cat], 'group': 'Categorias',
        'condition': (lambda ctx, c=_cat: c in ctx['categories_completed']),
    })

ACHIEVEMENT_DEFINITIONS += [
    {'key': 'avatar_set', 'title': 'Identidade definida', 'description': 'Defina uma foto de perfil', 'icon': 'camera-fill', 'group': 'Comando', 'condition': lambda ctx: ctx['has_avatar']},
    {'key': 'renamed', 'title': 'Nome de batalha', 'description': 'Escolha um nome para o seu perfil', 'icon': 'person-badge-fill', 'group': 'Comando', 'condition': lambda ctx: ctx['renamed']},
    {'key': 'account_30d', 'title': 'Astronauta veterano', 'description': 'Tenha conta há 30 dias', 'icon': 'calendar3', 'group': 'Comando', 'condition': lambda ctx: ctx['account_days'] >= 30},
    {'key': 'account_90d', 'title': 'Tripulação experiente', 'description': 'Tenha conta há 90 dias', 'icon': 'calendar3', 'group': 'Comando', 'condition': lambda ctx: ctx['account_days'] >= 90},
    {'key': 'account_365d', 'title': 'Um ano de missão', 'description': 'Tenha conta há 1 ano', 'icon': 'calendar3', 'group': 'Comando', 'condition': lambda ctx: ctx['account_days'] >= 365},
    {'key': 'premium', 'title': 'Comandante Premium', 'description': 'Torne-se Premium', 'icon': 'gem', 'group': 'Comando', 'condition': lambda ctx: ctx['is_premium']},
    {'key': 'light_theme', 'title': 'Painel claro', 'description': 'Ative o tema claro', 'icon': 'brightness-high-fill', 'group': 'Comando', 'condition': lambda ctx: ctx['light_theme']},
    {'key': 'notifications_on', 'title': 'Em sintonia', 'description': 'Ative os lembretes', 'icon': 'bell-fill', 'group': 'Comando', 'condition': lambda ctx: ctx['notifications_on']},
    {'key': 'pioneer', 'title': 'Pioneiro', 'description': 'Esteja entre os primeiros astronautas da base', 'icon': 'flag-fill', 'group': 'Comando', 'condition': lambda ctx: ctx['pioneer']},
    {'key': 'early_bird', 'title': 'Madrugador', 'description': 'Conclua uma meta antes das 7h', 'icon': 'sunrise-fill', 'group': 'Ritmo', 'condition': lambda ctx: ctx['early_bird']},
    {'key': 'night_owl', 'title': 'Coruja noturna', 'description': 'Conclua uma meta depois das 22h', 'icon': 'moon-stars-fill', 'group': 'Ritmo', 'condition': lambda ctx: ctx['night_owl']},
    {'key': 'weekend_warrior', 'title': 'Guerreiro de fim de semana', 'description': 'Conclua uma meta no fim de semana', 'icon': 'cup-fill', 'group': 'Ritmo', 'condition': lambda ctx: ctx['weekend_completed']},
    {'key': 'undated_done', 'title': 'Sem prazo, sem pressa', 'description': 'Conclua uma meta sem prazo definido', 'icon': 'infinity', 'group': 'Estilo de missão', 'condition': lambda ctx: ctx['undated_completed']},
    {'key': 'daily_5', 'title': 'Maratonista', 'description': 'Conclua 5 metas em um único dia', 'icon': 'lightning-fill', 'group': 'Estilo de missão', 'condition': lambda ctx: ctx['max_per_day'] >= 5},
    {'key': 'daily_10', 'title': 'Ultramaratonista', 'description': 'Conclua 10 metas em um único dia', 'icon': 'lightning-charge-fill', 'group': 'Estilo de missão', 'condition': lambda ctx: ctx['max_per_day'] >= 10},
    {'key': 'all_categories', 'title': 'Explorador completo', 'description': 'Conclua ao menos uma meta em todas as categorias', 'icon': 'globe-americas', 'group': 'Categorias', 'condition': lambda ctx: len(ctx['categories_completed']) >= len(GOAL_CATEGORIES)},
    {'key': 'category_master_10', 'title': 'Especialista de categoria', 'description': 'Conclua 10 metas em uma mesma categoria', 'icon': 'patch-check-fill', 'group': 'Categorias', 'condition': lambda ctx: ctx['max_category_count'] >= 10},
    {'key': 'category_master_25', 'title': 'Autoridade na área', 'description': 'Conclua 25 metas em uma mesma categoria', 'icon': 'patch-check-fill', 'group': 'Categorias', 'condition': lambda ctx: ctx['max_category_count'] >= 25},
    {'key': 'all_priorities', 'title': 'Visão 360', 'description': 'Conclua metas de todas as prioridades', 'icon': 'aspect-ratio-fill', 'group': 'Prioridade', 'condition': lambda ctx: ctx['priorities_completed'] >= 3},
    {'key': 'rate_50', 'title': 'Equilíbrio orbital', 'description': 'Atinja 50% de metas concluídas (mín. 10 criadas)', 'icon': 'pie-chart-fill', 'group': 'Consistência', 'condition': lambda ctx: ctx['created'] >= 10 and ctx['completion_rate'] >= 0.5},
    {'key': 'rate_75', 'title': 'Trajetória precisa', 'description': 'Atinja 75% de metas concluídas (mín. 10 criadas)', 'icon': 'pie-chart-fill', 'group': 'Consistência', 'condition': lambda ctx: ctx['created'] >= 10 and ctx['completion_rate'] >= 0.75},
    {'key': 'rate_100', 'title': 'Acerto perfeito', 'description': 'Conclua 100% das metas criadas (mín. 10 criadas)', 'icon': 'bullseye', 'group': 'Consistência', 'condition': lambda ctx: ctx['created'] >= 10 and ctx['completion_rate'] >= 1},
]
