from datetime import datetime

DEFAULT_MOTIVATIONAL_PHRASES = (
    'A direção importa mais do que a velocidade quando você está construindo uma vida.',
    'Pequenos passos repetidos criam grandes distâncias.',
    'A sua missão de hoje é o combustível do amanhã.',
    'Comece pequeno, mas continue em movimento.',
    'Cada meta concluída deixa sua jornada mais forte.',
    'Não precisa ser perfeito. Precisa ser possível hoje.',
)


def phrases_for(user):
    return [*DEFAULT_MOTIVATIONAL_PHRASES, *(phrase.text for phrase in user.custom_phrases)]


def current_phrase(phrases, interval_minutes):
    if not phrases:
        return ''
    slot = int(datetime.now().timestamp() // (interval_minutes * 60))
    return phrases[slot % len(phrases)]
