from datetime import datetime, date, timedelta
from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from flask_login import login_required,current_user
from ..extensions import db, limiter
from ..models import Goal
from ..services import today,goals_for,can_create,set_status,unlock_achievements
from ..utils.constants import GOAL_CATEGORIES
from ..utils.validators import valid_link_url
bp=Blueprint('goals',__name__,url_prefix='/goals')
CATEGORIES=GOAL_CATEGORIES
BOARD_COLUMNS=(('pendente','A fazer'),('em_andamento','Em andamento'),('concluida','Concluída'))
PRIORITY_ORDER={'alta':0,'media':1,'baixa':2}
def owned(id):
    g=db.session.get(Goal,id)
    if not g or g.user_id!=current_user.id: abort(404)
    return g
@bp.get('/')
@login_required
def index():
    rows=goals_for(current_user,today()-timedelta(days=365),today()+timedelta(days=30),include_undated=True); status=request.args.get('status','');priority=request.args.get('priority','');category=request.args.get('category','')
    rows=[x for x in rows if (not status or x['status']==status) and (not priority or x['goal'].priority==priority) and (not category or x['goal'].category==category)]
    return render_template('goals.html',rows=rows,categories=CATEGORIES,status=status,priority=priority,category=category)
@bp.get('/board')
@login_required
def board():
    rows=[row for row in goals_for(current_user,today(),today(),include_undated=True) if row['goal'].show_on_board]
    rows.sort(key=lambda row:(PRIORITY_ORDER.get(row['goal'].priority,1),row['goal'].time or datetime.min.time()))
    today_rows=[row for row in rows if row['date']]
    undated_rows=[row for row in rows if not row['date']]
    columns=[{'status':key,'label':label,'goals':[row for row in today_rows if row['status']==key]} for key,label in BOARD_COLUMNS]
    undated_preview=undated_rows[:10]
    undated_columns=[{'status':key,'label':label,'goals':[row for row in undated_preview if row['status']==key]} for key,label in BOARD_COLUMNS]
    return render_template('goals_board.html',columns=columns,undated_columns=undated_columns,undated_total=len(undated_rows),undated_preview_count=len(undated_preview),categories=CATEGORIES)
@bp.route('/new',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def new():
    if request.method=='POST':
        if not can_create(current_user): flash('O plano gratuito permite até 5 metas ativas. Conheça o Premium!','error');return redirect(url_for('main.premium'))
        return save_goal(Goal(user=current_user))
    return render_template('goal_form.html',goal=None,categories=CATEGORIES)
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
    g.recurrence_type=request.form.get('recurrence_type','none') if g.has_deadline else 'none';g.recurrence_days=int(request.form.get('recurrence_days') or 0) or None if g.has_deadline else None
    if g.recurrence_type=='forever': g.recurrence_end_date=None
    elif request.form.get('recurrence_end_date'): g.recurrence_end_date=datetime.strptime(request.form['recurrence_end_date'],'%Y-%m-%d').date()
    db.session.add(g);db.session.commit()
    for achievement in unlock_achievements(g.user): flash(f"🏆 Conquista desbloqueada: {achievement['title']}",'success')
    flash('Meta salva com sucesso.','success');return redirect(url_for('goals.index'))
@bp.post('/<int:id>/toggle')
@login_required
@limiter.limit('60 per minute')
def toggle(id):
    g=owned(id); _,achievements=set_status(g,'pendente' if g.status=='concluida' else 'concluida',include_achievements=True)
    for achievement in achievements: flash(f"🏆 Conquista desbloqueada: {achievement['title']}",'success')
    return redirect(request.referrer or url_for('goals.index'))
@bp.post('/<int:id>/delete')
@login_required
@limiter.limit('30 per minute')
def delete(id):
    g=owned(id);db.session.delete(g);db.session.commit();flash('Meta removida.','success');return redirect(url_for('goals.index'))
