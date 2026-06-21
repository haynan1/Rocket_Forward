GOAL_CATEGORIES = (
    'estudos', 'trabalho', 'saude', 'financas', 'espiritual',
    'pessoal', 'familia', 'empreendedorismo', 'outros',
)
GOAL_PRIORITIES = ('baixa', 'media', 'alta')
GOAL_STATUSES = ('pendente', 'em_andamento', 'concluida')
ACTIVE_STATUSES = ('pendente', 'em_andamento')
# Janela máxima olhada para trás ao calcular sequência/recorde. Nenhuma sequência
# diária real passa disso; evita reprocessar o histórico completo da conta a cada chamada.
MAX_STREAK_LOOKBACK_DAYS = 400
