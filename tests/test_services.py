from datetime import date,timedelta
from app.extensions import db
from app.models import User,Goal
from app.services import can_create,set_status,occurrence_dates,streak,stats
def user(email='a@a.com'):
 u=User(name='A',email=email);u.set_password('123456');db.session.add(u);db.session.commit();return u
def test_free_plan_limit(app):
 with app.app_context():
  u=user()
  for i in range(5):db.session.add(Goal(user=u,title=str(i),date=date.today()))
  db.session.commit();assert not can_create(u)
def test_complete_and_reopen(app):
 with app.app_context():
  u=user();g=Goal(user=u,title='x',date=date.today());db.session.add(g);db.session.commit()
  set_status(g,'concluida');assert g.status=='concluida' and g.completed_at
  set_status(g,'pendente');assert g.status=='pendente' and g.completed_at is None
def test_recurrence_weekdays(app):
 with app.app_context():
  u=user();g=Goal(user=u,title='x',date=date(2026,6,15),recurrence_type='weekdays',recurrence_end_date=date(2026,6,21));db.session.add(g);db.session.commit()
  assert len(occurrence_dates(g,date(2026,6,15),date(2026,6,21)))==5
def test_xp_level(app):
 with app.app_context():
  u=user()
  for i in range(16):db.session.add(Goal(user=u,title=str(i),date=date.today(),status='concluida'))
  db.session.commit();s=stats(u);assert s['xp']==160 and s['level']==2 and s['level_xp']==10
def test_user_isolation(app):
 with app.app_context():
  a=user();b=user('b@b.com');db.session.add(Goal(user=a,title='privada',date=date.today()));db.session.commit();assert Goal.query.filter_by(user_id=b.id).count()==0
def test_goal_without_deadline_is_not_planned(app):
 from app.services import goals_for
 with app.app_context():
  u=user();g=Goal(user=u,title='estudar sem prazo',date=date.today(),has_deadline=False);db.session.add(g);db.session.commit()
  assert goals_for(u,date.today(),date.today()) == []
  rows=goals_for(u,date.today(),date.today(),include_undated=True)
  assert len(rows)==1 and rows[0]['date'] is None and not rows[0]['goal'].has_deadline
def test_old_goal_without_deadline_stays_in_backlog(app):
 from app.services import goals_for
 with app.app_context():
  u=user();g=Goal(user=u,title='sem prazo antiga',date=date.today()-timedelta(days=1),has_deadline=False);db.session.add(g);db.session.commit()
  rows=goals_for(u,date.today(),date.today(),include_undated=True)
  assert len(rows)==1 and rows[0]['goal'].title=='sem prazo antiga' and rows[0]['date'] is None
