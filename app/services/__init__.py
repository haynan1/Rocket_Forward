from collections import Counter
from datetime import date, datetime, timedelta
from sqlalchemy.orm import selectinload
from ..extensions import db
from ..models import User, Goal, GoalOccurrenceOverride, Achievement, UserAchievement
from ..utils.constants import ACTIVE_STATUSES, MAX_STREAK_LOOKBACK_DAYS
from ..utils.dates import SAO_PAULO, local_now, local_today
from .achievements_data import ACHIEVEMENT_DEFINITIONS

TZ = SAO_PAULO
def today(): return local_today()
def active_count(user): return Goal.query.filter_by(user_id=user.id).filter(Goal.status.in_(ACTIVE_STATUSES)).count()
def can_create(user): return user.is_premium or active_count(user) < 5
def occurrence_dates(goal, start, end):
    first=max(goal.date, start); last=min(goal.recurrence_end_date or end, end)
    if goal.recurrence_type == 'none': return [goal.date] if start <= goal.date <= end else []
    out=[]; d=first
    while d <= last:
        days=(d-goal.date).days
        ok = goal.recurrence_type == 'forever' or (goal.recurrence_type == 'weekdays' and d.weekday()<5) or (goal.recurrence_type == 'weekends' and d.weekday()>=5) or (goal.recurrence_type == 'count' and days < (goal.recurrence_days or 0))
        if ok: out.append(d)
        d += timedelta(days=1)
    return out
def goals_for(user, start, end, include_undated=False):
    # Metas recorrentes podem ter começado antes de `start` e ainda gerar ocorrências
    # dentro da janela; metas avulsas (recurrence_type='none') só importam se a própria
    # data delas cair na janela — isso evita carregar todo o histórico avulso do usuário.
    # selectinload evita N+1: sem isso, cada meta dispara uma query separada para suas overrides.
    base=Goal.query.options(selectinload(Goal.overrides)).filter_by(user_id=user.id).filter(Goal.date <= end).filter(db.or_(Goal.recurrence_type != 'none', Goal.date >= start)).all(); rows=[]
    for g in base:
        if not g.has_deadline:
            if include_undated:
                rows.append({'goal':g,'date':None,'status':g.status,'completed_at':g.completed_at})
            continue
        overrides={o.occurrence_date:o for o in g.overrides}
        for d in occurrence_dates(g,start,end):
            o=overrides.get(d); rows.append({'goal':g,'date':d,'status':o.status if o else g.status,'completed_at':o.completed_at if o else g.completed_at})
    return sorted(rows,key=lambda x:(x['date'] is None, x['date'] or date.max, x['goal'].time or datetime.max.time(), {'alta':0,'media':1,'baixa':2}.get(x['goal'].priority,1),x['goal'].created_at))
def set_status(goal, value, occurrence=None, include_achievements=False):
    completed = local_now().replace(tzinfo=None) if value == 'concluida' else None
    if occurrence and (goal.recurrence_type != 'none' or occurrence != goal.date):
        override=GoalOccurrenceOverride.query.filter_by(goal_id=goal.id, occurrence_date=occurrence).first() or GoalOccurrenceOverride(goal=goal,occurrence_date=occurrence,status=value)
        override.status=value; override.completed_at=completed; db.session.add(override)
    else: goal.status=value; goal.completed_at=completed
    db.session.commit(); achievements=unlock_achievements(goal.user)
    return (value, achievements) if include_achievements else value
def cycle(goal, occurrence=None):
    current=next((x['status'] for x in goals_for(goal.user, occurrence or goal.date, occurrence or goal.date) if x['goal'].id==goal.id),goal.status)
    return set_status(goal, {'pendente':'em_andamento','em_andamento':'concluida','concluida':'pendente'}[current], occurrence)
def completed_dates(user):
    dates=set()
    for x in goals_for(user, today()-timedelta(days=MAX_STREAK_LOOKBACK_DAYS), today()):
        if x['status']=='concluida': dates.add(x['date'])
    return dates
def streak(user, dates=None):
    ds=completed_dates(user) if dates is None else dates; cursor=today() if today() in ds else today()-timedelta(days=1); n=0
    while cursor in ds: n+=1; cursor-=timedelta(days=1)
    return n
def max_streak(user, dates=None):
    ds=sorted(completed_dates(user) if dates is None else dates); best=run=0; prev=None
    for d in ds:
        run=run+1 if prev and d==prev+timedelta(days=1) else 1; best=max(best,run); prev=d
    return best
def stats(user):
    done=Goal.query.filter_by(user_id=user.id,status='concluida').count(); xp=done*10; level=1; remaining=xp
    while remaining >= level*150: remaining-=level*150; level+=1
    # Calcula completed_dates uma única vez: streak/max_streak não devem refazer o próprio scan.
    dates=completed_dates(user)
    return {'created':Goal.query.filter_by(user_id=user.id).count(),'completed':done,'xp':xp,'level':level,'level_xp':remaining,'needed':level*150,'streak':streak(user,dates),'record':max_streak(user,dates),'productive_days':len(dates)}
def achievement_context(user):
    s=stats(user)
    completed_goals=Goal.query.filter_by(user_id=user.id,status='concluida').all()
    categories_completed={g.category for g in completed_goals}
    category_counts=Counter(g.category for g in completed_goals)
    priority_counts=Counter(g.priority for g in completed_goals)
    timestamps=[g.completed_at for g in completed_goals if g.completed_at]
    per_day=Counter(t.date() for t in timestamps)
    return {
        **s,
        'categories_completed':categories_completed,
        'max_category_count':max(category_counts.values(),default=0),
        'priority_alta':priority_counts.get('alta',0),
        'priority_media':priority_counts.get('media',0),
        'priority_baixa':priority_counts.get('baixa',0),
        'priorities_completed':sum(1 for p in ('alta','media','baixa') if priority_counts.get(p,0)>0),
        'has_avatar':bool(user.avatar_path),
        'renamed':user.name!='Astronauta',
        'account_days':(datetime.now()-user.created_at).days,
        'is_premium':user.is_premium,
        'light_theme':user.theme_mode=='light',
        'notifications_on':user.notifications_enabled,
        'early_bird':any(t.hour<7 for t in timestamps),
        'night_owl':any(t.hour>=22 for t in timestamps),
        'weekend_completed':any(t.weekday()>=5 for t in timestamps),
        'undated_completed':any(not g.has_deadline for g in completed_goals),
        'max_per_day':max(per_day.values(),default=0),
        'completion_rate':(s['completed']/s['created']) if s['created'] else 0,
        'pioneer':user.id<=50,
    }
def unlock_achievements(user):
    ctx=achievement_context(user)
    existing={a.key:a for a in Achievement.query.all()}
    defined_keys={d['key'] for d in ACHIEVEMENT_DEFINITIONS}
    stale=[a for a in existing.values() if a.key not in defined_keys]
    if stale:
        UserAchievement.query.filter(UserAchievement.achievement_id.in_([a.id for a in stale])).delete(synchronize_session=False)
        for a in stale: existing.pop(a.key); db.session.delete(a)
    for d in ACHIEVEMENT_DEFINITIONS:
        a=existing.get(d['key'])
        if not a:
            a=Achievement(key=d['key'],title=d['title'],description=d['description'],icon=d['icon'],group=d['group'])
            db.session.add(a); existing[d['key']]=a
        elif (a.title,a.description,a.icon,a.group)!=(d['title'],d['description'],d['icon'],d['group']):
            a.title,a.description,a.icon,a.group=d['title'],d['description'],d['icon'],d['group']
    db.session.flush()
    unlocked_ids={x.achievement_id for x in UserAchievement.query.filter_by(user_id=user.id)}
    unlocked=[]
    for d in ACHIEVEMENT_DEFINITIONS:
        a=existing[d['key']]
        if a.id not in unlocked_ids and d['condition'](ctx):
            db.session.add(UserAchievement(user_id=user.id,achievement_id=a.id))
            unlocked.append({'title':a.title,'icon':a.icon})
    db.session.commit()
    return unlocked
def create_demo_user():
    if not User.query.filter_by(email='demo@rocket.forward').first():
        u=User(name='Astronauta Demo',email='demo@rocket.forward');u.set_password('foguete123');db.session.add(u);db.session.commit()
