from datetime import datetime, timedelta
from flask import Blueprint,jsonify,request,abort
from flask_login import login_required,current_user
from ..extensions import db, limiter
from ..models import Goal, Achievement, UserAchievement
from ..services import today,goals_for,stats,set_status,cycle,can_create
from ..utils.constants import GOAL_STATUSES, GOAL_PRIORITIES, GOAL_CATEGORIES
bp=Blueprint('api',__name__,url_prefix='/api')
MAX_TITLE_LEN=160
MAX_DESCRIPTION_LEN=2000
MAX_NAME_LEN=80
def goal_json(row):
 g=row['goal'];return {'id':g.id,'title':g.title,'description':g.description,'date':row['date'].isoformat() if row['date'] else None,'has_deadline':g.has_deadline,'time':g.time.isoformat() if g.time else None,'priority':g.priority,'category':g.category,'status':row['status'],'recurrence_type':g.recurrence_type}
def owned(id):
 g=db.session.get(Goal,id)
 if not g or g.user_id!=current_user.id: abort(404)
 return g
@bp.route('/goals',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def goals_api():
 if request.method=='GET': return jsonify([goal_json(x) for x in goals_for(current_user,today()-timedelta(days=365),today()+timedelta(days=30),include_undated=True)])
 if not can_create(current_user): return jsonify(error='Limite gratuito de 5 metas ativas.',premium=True),403
 d=request.get_json() or {}; title=str(d.get('title','')).strip(); description=d.get('description')
 if not title or len(title)>MAX_TITLE_LEN:return jsonify(error=f'Título obrigatório, até {MAX_TITLE_LEN} caracteres.'),400
 if description is not None and len(str(description))>MAX_DESCRIPTION_LEN:return jsonify(error=f'Descrição deve ter até {MAX_DESCRIPTION_LEN} caracteres.'),400
 if d.get('priority','media') not in GOAL_PRIORITIES: return jsonify(error='Prioridade inválida.'),400
 if d.get('category','pessoal') not in GOAL_CATEGORIES: return jsonify(error='Categoria inválida.'),400
 try: due=datetime.strptime(d.get('date',today().isoformat()),'%Y-%m-%d').date()
 except ValueError:return jsonify(error='Data inválida.'),400
 has_deadline=bool(d.get('has_deadline',True));g=Goal(user=current_user,title=title,date=due,has_deadline=has_deadline,description=description,priority=d.get('priority','media'),category=d.get('category','pessoal'));db.session.add(g);db.session.commit();return jsonify(id=g.id),201
@bp.route('/goals/<int:id>',methods=['GET','PATCH','DELETE'])
@login_required
@limiter.limit('30 per minute', methods=['PATCH','DELETE'])
def goal_api(id):
 g=owned(id)
 if request.method=='GET':return jsonify(goal_json({'goal':g,'date':g.date,'status':g.status}))
 if request.method=='DELETE':db.session.delete(g);db.session.commit();return '',204
 d=request.get_json() or {}
 if 'status' in d and d['status'] not in GOAL_STATUSES: return jsonify(error='Status inválido.'),400
 if 'priority' in d and d['priority'] not in GOAL_PRIORITIES: return jsonify(error='Prioridade inválida.'),400
 if 'category' in d and d['category'] not in GOAL_CATEGORIES: return jsonify(error='Categoria inválida.'),400
 if 'title' in d and (not str(d['title']).strip() or len(str(d['title']))>MAX_TITLE_LEN): return jsonify(error=f'Título obrigatório, até {MAX_TITLE_LEN} caracteres.'),400
 if 'description' in d and d['description'] is not None and len(str(d['description']))>MAX_DESCRIPTION_LEN: return jsonify(error=f'Descrição deve ter até {MAX_DESCRIPTION_LEN} caracteres.'),400
 for k in ('title','description','priority','category'):
  if k in d:setattr(g,k,d[k])
 if 'has_deadline' in d:g.has_deadline=bool(d['has_deadline']);g.time=None if not g.has_deadline else g.time
 if 'date' in d:
  try: g.date=datetime.strptime(d['date'],'%Y-%m-%d').date()
  except ValueError: return jsonify(error='Data inválida.'),400
 occurrence=None
 if 'occurrence' in d:
  try: occurrence=datetime.strptime(d['occurrence'],'%Y-%m-%d').date()
  except ValueError: return jsonify(error='Data invÃ¡lida.'),400
 db.session.commit()
 achievements=[]
 if 'status' in d: _,achievements=set_status(g,d['status'],occurrence,include_achievements=True)
 return jsonify(ok=True,achievements=achievements)
@bp.post('/goals/<int:id>/toggle-complete')
@login_required
@limiter.limit('60 per minute')
def toggle_api(id):
 g=owned(id); occurrence=request.json.get('date') if request.is_json else None
 d=None
 if occurrence:
  try: d=datetime.strptime(occurrence,'%Y-%m-%d').date()
  except ValueError: return jsonify(error='Data inválida.'),400
 status,achievements=set_status(g,'pendente' if g.status=='concluida' else 'concluida',d,include_achievements=True)
 return jsonify(status=status,achievements=achievements)
@bp.post('/goals/<int:id>/cycle-status')
@login_required
@limiter.limit('60 per minute')
def cycle_api(id):return jsonify(status=cycle(owned(id)))
@bp.get('/stats')
@login_required
def stats_api():return jsonify(stats(current_user))
@bp.get('/achievements')
@login_required
def achievements_api():
 unlocked={x.achievement_id for x in UserAchievement.query.filter_by(user_id=current_user.id)};return jsonify([{'key':a.key,'title':a.title,'unlocked':a.id in unlocked} for a in Achievement.query.all()])
@bp.get('/reports/monthly')
@login_required
def report_api():
 if not current_user.is_premium:return jsonify(error='Recurso Premium'),403
 rows=goals_for(current_user,today()-timedelta(days=29),today());return jsonify(total=len(rows),completed=sum(x['status']=='concluida' for x in rows))
@bp.route('/profile',methods=['GET','PATCH'])
@login_required
@limiter.limit('30 per minute', methods=['PATCH'])
def profile_api():
 if request.method=='PATCH':
  d=request.get_json() or {}
  name=d.get('name',current_user.name)
  if not str(name).strip() or len(str(name))>MAX_NAME_LEN: return jsonify(error=f'Nome obrigatório, até {MAX_NAME_LEN} caracteres.'),400
  current_user.name=name;current_user.theme_mode=d.get('theme_mode',current_user.theme_mode);db.session.commit()
 return jsonify(name=current_user.name,theme_mode=current_user.theme_mode,is_premium=current_user.is_premium)
