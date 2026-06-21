from datetime import date, timedelta
from app.extensions import db
from app.models import User, Goal, MotivationalPhrase
from app.services import goals_for, today
from app.blueprints.auth import password_reset_token


def _register(client, email, password='12345678', name='A'):
    return client.post('/auth/register', data={'name': name, 'email': email, 'password': password}, follow_redirects=True)


def _logout(client):
    client.get('/auth/logout')


def _login(client, email, password='12345678'):
    return client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)


def test_register_and_login_roundtrip(client):
    assert _register(client, 'owner@rocket.test').status_code == 200
    _logout(client)
    assert _login(client, 'owner@rocket.test').status_code == 200


def test_invalid_login_does_not_authenticate(client):
    _register(client, 'owner2@rocket.test')
    _logout(client)
    _login(client, 'owner2@rocket.test', password='senha-errada')
    # sem sessão válida, a home redireciona pro login em vez de mostrar o dashboard
    assert client.get('/').status_code in (302, 308)


def test_password_can_be_reset_with_a_valid_temporary_link(app, client):
    _register(client, 'reset@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='reset@rocket.test').first()
        token = password_reset_token(user)
    _logout(client)

    response = client.post(f'/auth/reset-password/{token}', data={'password': 'nova-senha', 'password_confirmation': 'nova-senha'}, follow_redirects=True)

    assert response.status_code == 200
    _logout(client)
    assert _login(client, 'reset@rocket.test', 'nova-senha').status_code == 200


def test_password_recovery_request_does_not_reveal_if_email_exists(client):
    response = client.post('/auth/forgot-password', data={'email': 'nao-existe@rocket.test'}, follow_redirects=True)

    assert response.status_code == 200
    assert 'Se esse e-mail tiver uma conta'.encode() in response.data


def test_static_assets_are_not_cached(client):
    response = client.get('/static/css/app.css')

    assert response.headers['Cache-Control'] == 'no-store, max-age=0, must-revalidate'


def test_login_background_images_are_in_the_login_folder(client):
    for image in ('imagem1.png', 'imagem2.png', 'imagem3.png', 'imagem4.png'):
        assert client.get(f'/static/images/login/{image}').status_code == 200


def test_phrase_personalization_is_premium_only(app, client):
    _register(client, 'phrases@rocket.test')
    assert client.get('/phrases', follow_redirects=True).status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='phrases@rocket.test').first()
        user.is_premium = True
        db.session.commit()
    _logout(client)
    _login(client, 'phrases@rocket.test')

    response = client.post('/phrases', data={'interval': '5', 'text': 'Um passo de cada vez.'}, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='phrases@rocket.test').first()
        assert user.phrase_interval_minutes == 5
        assert MotivationalPhrase.query.filter_by(user_id=user.id, text='Um passo de cada vez.').count() == 1


def test_user_can_choose_per_goal_to_show_undated_goals_on_board(app, client):
    _register(client, 'undated-board@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='undated-board@rocket.test').first()
        db.session.add(Goal(user=user, title='meta sem prazo', date=today(), has_deadline=False, show_on_board=False))
        db.session.commit()

    assert b'meta sem prazo' not in client.get('/goals/board').data
    with app.app_context():
        goal = Goal.query.filter_by(title='meta sem prazo').first()
        goal.show_on_board = True
        db.session.commit()

    response = client.get('/goals/board')
    assert b'meta sem prazo' in response.data
    assert b'Backlog sem prazo' in response.data


def test_undated_board_backlog_is_limited_to_ten_goals(app, client):
    _register(client, 'backlog@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='backlog@rocket.test').first()
        for index in range(11):
            db.session.add(Goal(user=user, title=f'backlog {index}', date=today(), has_deadline=False, show_on_board=True))
        db.session.commit()

    response = client.get('/goals/board')

    assert b'backlog 0' in response.data
    assert b'backlog 9' in response.data
    assert b'backlog 10' not in response.data
    assert b'11 metas guardadas aqui' in response.data


def test_goal_link_is_saved_and_rendered_as_a_shortcut(app, client):
    _register(client, 'goal-link@rocket.test')

    response = client.post('/goals/new', data={'title': 'Ler documentacao', 'link_url': 'https://example.com/docs', 'has_deadline': 'on'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'bi-link-45deg' in response.data
    with app.app_context():
        assert Goal.query.filter_by(title='Ler documentacao').first().link_url == 'https://example.com/docs'


def test_goal_link_rejects_non_web_address(client):
    _register(client, 'invalid-link@rocket.test')

    response = client.post('/goals/new', data={'title': 'Link invalido', 'link_url': 'javascript:alert(1)', 'has_deadline': 'on'})

    assert response.status_code == 200
    assert 'Informe um link válido'.encode() in response.data


def test_editing_a_goal_with_an_invalid_link_keeps_the_new_title_on_the_redisplayed_form(app, client):
    _register(client, 'edit-link@rocket.test')
    client.post('/goals/new', data={'title': 'Titulo original', 'has_deadline': 'on'}, follow_redirects=True)
    with app.app_context():
        goal_id = Goal.query.filter_by(title='Titulo original').first().id

    response = client.post(f'/goals/{goal_id}/edit', data={'title': 'Titulo editado', 'link_url': 'javascript:alert(1)', 'has_deadline': 'on'})

    assert response.status_code == 200
    assert 'Informe um link válido'.encode() in response.data
    assert b'value="Titulo editado"' in response.data


def test_user_can_save_english_us_as_interface_language(app, client):
    _register(client, 'english@rocket.test')

    response = client.post('/profile', data={'name': 'A', 'locale': 'en-US'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'data-locale="en-US"' in response.data
    with app.app_context():
        assert User.query.filter_by(email='english@rocket.test').first().locale == 'en-US'


def test_login_screen_keeps_english_after_logout(client):
    _register(client, 'english2@rocket.test')
    client.post('/profile', data={'name': 'A', 'locale': 'en-US'})

    _logout(client)
    response = client.get('/auth/login')

    # a tradução acontece no cliente a partir de data-locale/data-translations;
    # o que o servidor precisa garantir é que a preferência salva sobrevive ao logout
    assert b'data-locale="en-US"' in response.data
    assert b'lang="en-US"' in response.data


def test_goal_filter_keeps_the_selected_value(app, client):
    _register(client, 'filter@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='filter@rocket.test').first()
        db.session.add(Goal(user=user, title='alta prioridade', date=date.today(), priority='alta'))
        db.session.commit()

    response = client.get('/goals/?priority=alta')

    assert b'<option value="alta" selected>Alta</option>' in response.data
    assert b'Limpar' in response.data


def test_new_goal_without_a_date_uses_today_and_appears_on_dashboard(app, client):
    _register(client, 'today@rocket.test')

    response = client.post('/goals/new', data={'title': 'meta de hoje', 'has_deadline': 'on'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'meta de hoje' in response.data
    with app.app_context():
        goal = Goal.query.filter_by(title='meta de hoje').first()
        assert goal.date == today()


def test_unlocking_an_achievement_is_shown_after_saving_a_goal(client):
    _register(client, 'achievement@rocket.test')

    response = client.post('/goals/new', data={'title': 'primeira meta', 'has_deadline': 'on'}, follow_redirects=True)

    assert 'Conquista desbloqueada'.encode() in response.data


def test_board_shows_only_goals_scheduled_for_today(app, client):
    _register(client, 'board@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='board@rocket.test').first()
        db.session.add_all([
            Goal(user=user, title='meta de hoje', date=today()),
            Goal(user=user, title='meta antiga', date=today() - timedelta(days=1)),
        ])
        db.session.commit()

    response = client.get('/goals/board')

    assert b'meta de hoje' in response.data
    assert b'meta antiga' not in response.data


def test_board_status_update_applies_to_todays_recurrence(app, client):
    _register(client, 'recurring@rocket.test')
    with app.app_context():
        user = User.query.filter_by(email='recurring@rocket.test').first()
        goal = Goal(user=user, title='recorrente', date=today() - timedelta(days=1), recurrence_type='forever')
        db.session.add(goal)
        db.session.commit()
        goal_id = goal.id

    response = client.patch(f'/api/goals/{goal_id}', json={'status': 'concluida', 'occurrence': today().isoformat()})

    assert response.status_code == 200
    with app.app_context():
        goal = db.session.get(Goal, goal_id)
        row = goals_for(goal.user, today(), today())[0]
        assert goal.status == 'pendente'
        assert row['status'] == 'concluida'


def _create_private_goal(app, owner_email):
    with app.app_context():
        owner = User(name='Owner', email=owner_email)
        owner.set_password('12345678')
        db.session.add(owner)
        db.session.commit()
        goal = Goal(user=owner, title='privada', date=date.today())
        db.session.add(goal)
        db.session.commit()
        return goal.id


def test_api_blocks_access_to_another_users_goal(app, client):
    goal_id = _create_private_goal(app, 'owner3@rocket.test')
    _register(client, 'intruder@rocket.test')

    assert client.get(f'/api/goals/{goal_id}').status_code == 404
    assert client.patch(f'/api/goals/{goal_id}', json={'title': 'hackeado'}).status_code == 404
    assert client.delete(f'/api/goals/{goal_id}').status_code == 404


def test_html_blocks_edit_and_delete_of_another_users_goal(app, client):
    goal_id = _create_private_goal(app, 'owner4@rocket.test')
    _register(client, 'intruder2@rocket.test')

    assert client.get(f'/goals/{goal_id}/edit').status_code == 404
    assert client.post(f'/goals/{goal_id}/delete').status_code == 404
