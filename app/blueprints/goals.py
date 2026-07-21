from datetime import datetime, date, timedelta
from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from flask_login import login_required,current_user
from ..extensions import db, limiter
from ..models import Goal, GoalTemplate
from ..services import today,goals_for,can_create,set_status,unlock_achievements
from ..utils.constants import GOAL_CATEGORIES, GOAL_PRIORITIES, GOAL_STATUSES
from ..utils.validators import valid_link_url
bp=Blueprint('goals',__name__,url_prefix='/goals')
CATEGORIES=GOAL_CATEGORIES
BOARD_COLUMNS=(('pendente','A fazer'),('em_andamento','Em andamento'),('concluida','Concluída'))
PRIORITY_ORDER={'alta':0,'media':1,'baixa':2}
RECURRENCE_TYPES=('none','weekdays','weekends','count','forever')
MAX_TITLE_LEN=160
MAX_DESCRIPTION_LEN=2000
def owned(id):
    g=db.session.get(Goal,id)
    if not g or g.user_id!=current_user.id: abort(404)
    return g

def owned_template(id):
    template=db.session.get(GoalTemplate,id)
    if not template or template.user_id!=current_user.id: abort(404)
    return template
@bp.get('/')
@login_required
def index():
    rows=goals_for(current_user,today()-timedelta(days=365),today()+timedelta(days=30),include_undated=True); status=request.args.get('status','');priority=request.args.get('priority','');category=request.args.get('category','')
    rows=[x for x in rows if (not status or x['status']==status) and (not priority or x['goal'].priority==priority) and (not category or x['goal'].category==category)]
    today_date=today()
    for row in rows:
        row['is_overdue']=bool(row['date'] and row['date']<today_date and row['status']!='concluida')
    return render_template('goals.html',rows=rows,categories=CATEGORIES,status=status,priority=priority,category=category,today_date=today_date)
@bp.get('/board')
@login_required
def board():
    today_date=today()
    rows=[row for row in goals_for(current_user,today_date,today_date,include_undated=True) if row['goal'].show_on_board]
    rows.sort(key=lambda row:(PRIORITY_ORDER.get(row['goal'].priority,1),row['goal'].time or datetime.min.time()))
    today_rows=[row for row in rows if row['date']]
    undated_rows=[row for row in rows if not row['date']]
    overdue_by_goal={}
    for row in goals_for(current_user,today_date-timedelta(days=365),today_date-timedelta(days=1)):
        if row['goal'].show_on_board and row['status']!='concluida':
            # Para metas recorrentes, exibimos apenas a pendência mais recente da série.
            previous=overdue_by_goal.get(row['goal'].id)
            if not previous or row['date']>previous['date']:
                overdue_by_goal[row['goal'].id]=row
    overdue_rows=sorted(overdue_by_goal.values(),key=lambda row:(row['date'],PRIORITY_ORDER.get(row['goal'].priority,1),row['goal'].time or datetime.min.time()))
    columns=[{'status':key,'label':label,'goals':[row for row in today_rows if row['status']==key]} for key,label in BOARD_COLUMNS]
    undated_preview=undated_rows[:10]
    undated_columns=[{'status':key,'label':label,'goals':[row for row in undated_preview if row['status']==key]} for key,label in BOARD_COLUMNS]
    return render_template('goals_board.html',columns=columns,overdue_rows=overdue_rows,today_date=today_date,undated_columns=undated_columns,undated_total=len(undated_rows),undated_preview_count=len(undated_preview),categories=CATEGORIES)
@bp.route('/new',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def new():
    if request.method=='POST':
        if not can_create(current_user): flash('O plano gratuito permite até 5 metas ativas. Conheça o Premium!','error');return redirect(url_for('main.premium'))
        return save_goal(Goal(user=current_user))
    return render_template('goal_form.html',goal=None,categories=CATEGORIES)

@bp.get('/templates')
@login_required
def templates():
    rows=GoalTemplate.query.filter_by(user_id=current_user.id).order_by(GoalTemplate.created_at.desc()).all()
    return render_template('goal_templates.html',templates=rows,categories=CATEGORIES,today_date=today())

@bp.route('/templates/new',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def new_template():
    if request.method=='POST':
        return save_template(GoalTemplate(user_id=current_user.id))
    return render_template('goal_template_form.html',template=None,categories=CATEGORIES)

@bp.route('/templates/<int:id>/edit',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def edit_template(id):
    template=owned_template(id)
    if request.method=='POST':
        return save_template(template)
    return render_template('goal_template_form.html',template=template,categories=CATEGORIES)

def save_template(template):
    title=request.form.get('title','').strip(); link_url=request.form.get('link_url','').strip()
    template.title=title;template.description=request.form.get('description','').strip() or None;template.link_url=link_url or None
    template.priority=request.form.get('priority','media');template.category=request.form.get('category','pessoal');template.show_on_board='show_on_board' in request.form
    if len(title)>MAX_TITLE_LEN or (template.description and len(template.description)>MAX_DESCRIPTION_LEN):
        flash('Titulo ou descricao excede o tamanho permitido.','error');return render_template('goal_template_form.html',template=template,categories=CATEGORIES)
    if template.priority not in GOAL_PRIORITIES or template.category not in CATEGORIES:
        flash('Prioridade ou categoria invalida.','error');return render_template('goal_template_form.html',template=template,categories=CATEGORIES)
    try: template.time=datetime.strptime(request.form['time'],'%H:%M').time() if request.form.get('time') else None
    except ValueError:
        flash('Informe um horário válido.','error');return render_template('goal_template_form.html',template=template,categories=CATEGORIES)
    if not title:
        flash('O título é obrigatório.','error');return render_template('goal_template_form.html',template=template,categories=CATEGORIES)
    if not valid_link_url(link_url):
        flash('Informe um link válido que comece com http:// ou https://.','error');return render_template('goal_template_form.html',template=template,categories=CATEGORIES)
    db.session.add(template);db.session.commit();flash('Meta predefinida salva com sucesso.','success')
    return redirect(url_for('goals.templates'))

@bp.post('/templates/<int:id>/activate')
@login_required
@limiter.limit('30 per minute')
def activate_template(id):
    template=owned_template(id)
    if not can_create(current_user):
        flash('O plano gratuito permite até 5 metas ativas. Conheça o Premium!','error');return redirect(url_for('main.premium'))
    try: scheduled_date=datetime.strptime(request.form.get('date',''),'%Y-%m-%d').date()
    except ValueError:
        flash('Escolha uma data válida para ativar esta meta.','error');return redirect(url_for('goals.templates'))
    goal=Goal(user=current_user,title=template.title,description=template.description,link_url=template.link_url,date=scheduled_date,time=template.time,has_deadline=True,show_on_board=template.show_on_board,priority=template.priority,category=template.category,status='pendente')
    db.session.add(goal);db.session.commit()
    for achievement in unlock_achievements(current_user): flash(f"🏆 Conquista desbloqueada: {achievement['title']}",'success')
    flash(f'Meta ativada para {scheduled_date.strftime("%d/%m/%Y")}.','success')
    return redirect(url_for('goals.board') if scheduled_date==today() else url_for('goals.index'))

@bp.post('/templates/<int:id>/delete')
@login_required
@limiter.limit('30 per minute')
def delete_template(id):
    template=owned_template(id);db.session.delete(template);db.session.commit();flash('Meta predefinida removida.','success')
    return redirect(url_for('goals.templates'))
@bp.route('/<int:id>/edit',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def edit(id):
    g=owned(id)
    if request.method=='POST': return save_goal(g)
    return render_template('goal_form.html',goal=g,categories=CATEGORIES)
def save_goal(g):
    title=request.form.get('title','').strip(); rawdate=request.form.get('date','');link_url=request.form.get('link_url','').strip()
    if not title: flash('O título é obrigatório.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    # Preenche os campos simples já aqui: se a validação de link/data/horário abaixo falhar e
    # o formulário for redesenhado, o que o usuário digitou continua visível em vez de
    # reaparecer como o atributo ainda não definido (None) do objeto recém-criado.
    g.title=title;g.description=request.form.get('description','').strip() or None;g.link_url=link_url or None;g.priority=request.form.get('priority','media');g.category=request.form.get('category','pessoal');g.status=request.form.get('status','pendente')
    if len(title)>MAX_TITLE_LEN or (g.description and len(g.description)>MAX_DESCRIPTION_LEN):
        flash('Titulo ou descricao excede o tamanho permitido.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    if g.priority not in GOAL_PRIORITIES or g.category not in CATEGORIES or g.status not in GOAL_STATUSES:
        flash('Prioridade, categoria ou status invalido.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    if not valid_link_url(link_url):
        flash('Informe um link válido que comece com http:// ou https://.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    g.has_deadline='has_deadline' in request.form;g.show_on_board='show_on_board' in request.form
    if g.has_deadline:
        try: g.date=datetime.strptime(rawdate,'%Y-%m-%d').date() if rawdate else today()
        except ValueError: flash('Informe uma data válida.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
        try: g.time=datetime.strptime(request.form['time'],'%H:%M').time() if request.form.get('time') else None
        except ValueError: flash('Informe um horário válido.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    else:
        # Mantém uma data interna apenas para compatibilidade com bancos legados; ela nunca é exibida nem usada no planejamento.
        g.date=today(); g.time=None; g.recurrence_type='none'; g.recurrence_days=None; g.recurrence_end_date=None
    g.recurrence_type=request.form.get('recurrence_type','none') if g.has_deadline else 'none'
    if g.recurrence_type not in RECURRENCE_TYPES:
        flash('Tipo de repeticao invalido.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    try: g.recurrence_days=int(request.form.get('recurrence_days') or 0) or None if g.has_deadline else None
    except ValueError:
        flash('Quantidade de dias invalida.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    if g.recurrence_type=='count' and not g.recurrence_days:
        flash('Informe a quantidade de dias para a repeticao.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    if g.recurrence_type=='forever': g.recurrence_end_date=None
    elif request.form.get('recurrence_end_date'):
        try: g.recurrence_end_date=datetime.strptime(request.form['recurrence_end_date'],'%Y-%m-%d').date()
        except ValueError:
            flash('Data final invalida.','error');return render_template('goal_form.html',goal=g,categories=CATEGORIES)
    db.session.add(g);db.session.commit()
    for achievement in unlock_achievements(g.user): flash(f"🏆 Conquista desbloqueada: {achievement['title']}",'success')
    flash('Meta salva com sucesso.','success');return redirect(url_for('goals.index'))
@bp.post('/<int:id>/toggle')
@login_required
@limiter.limit('60 per minute')
def toggle(id):
    g=owned(id); occurrence=None
    if request.form.get('occurrence'):
        try: occurrence=datetime.strptime(request.form['occurrence'],'%Y-%m-%d').date()
        except ValueError: abort(400)
    current=next((row['status'] for row in goals_for(g.user,occurrence,occurrence) if row['goal'].id==g.id),g.status) if occurrence else g.status
    _,achievements=set_status(g,'pendente' if current=='concluida' else 'concluida',occurrence,include_achievements=True)
    for achievement in achievements: flash(f"🏆 Conquista desbloqueada: {achievement['title']}",'success')
    return redirect(request.referrer or url_for('goals.index'))
@bp.post('/<int:id>/activate-today')
@login_required
@limiter.limit('60 per minute')
def activate_today(id):
    g=owned(id)
    if g.status=='concluida':
        flash('Esta meta ja esta concluida. Reabra a meta antes de mover para hoje.','error');return redirect(request.referrer or url_for('goals.index'))
    g.has_deadline=True;g.date=today();g.show_on_board=True;g.recurrence_type='none';g.recurrence_days=None;g.recurrence_end_date=None
    db.session.commit();flash('Meta movida para hoje.','success')
    return redirect(url_for('goals.board'))
@bp.post('/<int:id>/delete')
@login_required
@limiter.limit('30 per minute')
def delete(id):
    g=owned(id);db.session.delete(g);db.session.commit();flash('Meta removida.','success');return redirect(url_for('goals.index'))
