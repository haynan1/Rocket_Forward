from datetime import date, timedelta
from app.extensions import db
from app.models import User, Goal
from app.services import goals_for, today


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
