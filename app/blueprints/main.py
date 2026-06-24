import os,secrets
from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required,current_user
from PIL import Image, UnidentifiedImageError
from ..extensions import db, limiter
from ..models import Goal, GoalTemplate, UserAchievement, MotivationalPhrase
from ..services import today,goals_for,stats,completed_dates,unlock_achievements
from ..services.achievements_data import ACHIEVEMENT_DEFINITIONS
from ..services.phrases import DEFAULT_MOTIVATIONAL_PHRASES, current_phrase, phrases_for
bp=Blueprint('main',__name__)

ALLOWED_AVATAR_EXTENSIONS={'png','jpg','jpeg','webp'}
AVATAR_SIZE=(256,256)

def _save_avatar(file_storage,user):
    if not file_storage or not file_storage.filename:
        raise ValueError('Selecione uma imagem para enviar.')
    ext=file_storage.filename.rsplit('.',1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise ValueError('Formato não suportado. Envie uma imagem PNG, JPG ou WEBP.')
    try:
        image=Image.open(file_storage.stream)
        image.verify()
        file_storage.stream.seek(0)
        image=Image.open(file_storage.stream)
        image.load()
        image=image.convert('RGB')
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise ValueError('Arquivo inválido. Envie uma imagem de verdade.')
    w,h=image.size; side=min(w,h)
    image=image.crop(((w-side)//2,(h-side)//2,(w+side)//2,(h+side)//2)).resize(AVATAR_SIZE,Image.LANCZOS)
    upload_dir=os.path.join(current_app.static_folder,'uploads','avatars')
    os.makedirs(upload_dir,exist_ok=True)
    filename=f"{user.id}_{secrets.token_hex(8)}.webp"
    image.save(os.path.join(upload_dir,filename),format='WEBP',quality=88)
    _delete_avatar_file(user.avatar_path)
    return f"uploads/avatars/{filename}"

def _delete_avatar_file(avatar_path):
    if not avatar_path:
        return
    upload_dir=os.path.realpath(os.path.join(current_app.static_folder,'uploads','avatars'))
    abs_path=os.path.realpath(os.path.join(current_app.static_folder,avatar_path))
    if os.path.commonpath([abs_path,upload_dir])==upload_dir and os.path.isfile(abs_path):
        try: os.remove(abs_path)
        except OSError: pass
@bp.get('/')
@login_required
def dashboard():
    rows=goals_for(current_user,today(),today()); done=sum(x['status']=='concluida' for x in rows)
    s=stats(current_user)
    phrases=phrases_for(current_user)
    return render_template('dashboard.html', rows=rows, done=done, total=len(rows), stats=s, phrases=phrases, phrase=current_phrase(phrases,current_user.phrase_interval_minutes), phrase_interval_ms=current_user.phrase_interval_minutes*60*1000, risk=bool(s['streak'] and not done and any(x['status']!='concluida' for x in rows)))
@bp.get('/planning')
@login_required
def planning():
    view=request.args.get('view','week'); start=today()-timedelta(days=today().weekday()) if view=='week' else today().replace(day=1); end=start+timedelta(days=6 if view=='week' else 30)
    rows=goals_for(current_user,start,end); return render_template('planning.html',rows=rows,start=start,end=end,view=view)
@bp.get('/history')
@login_required
def history():
    days=[today()-timedelta(days=i) for i in range(6,-1,-1)]; ds=completed_dates(current_user); chart=[1 if d in ds else 0 for d in days]
    return render_template('history.html',stats=stats(current_user),labels=[d.strftime('%d/%m') for d in days],chart=chart)
@bp.route('/profile',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def profile():
    if request.method=='POST':
        current_user.name=request.form.get('name','').strip() or current_user.name
        current_user.theme_mode=request.form.get('theme_mode',current_user.theme_mode);current_user.locale=request.form.get('locale','pt-BR') if request.form.get('locale') in ('pt-BR','en-US') else 'pt-BR';current_user.motivational_phrases_enabled='phrases' in request.form;current_user.notifications_enabled='notifications' in request.form;db.session.commit();flash('Perfil atualizado.','success');return redirect(url_for('main.profile'))
    return render_template('profile.html',stats=stats(current_user),unlocked=UserAchievement.query.filter_by(user_id=current_user.id).count())
@bp.route('/phrases',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def phrases():
    if not current_user.is_premium:
        flash('Personalização de frases é um recurso Premium.','error')
        return redirect(url_for('main.premium'))
    if request.method=='POST':
        interval=request.form.get('interval')
        if interval:
            try: interval=int(interval)
            except ValueError: interval=0
            if interval not in (1,5,15,30,60): flash('Escolha um intervalo válido.','error')
            else: current_user.phrase_interval_minutes=interval;db.session.commit();flash('Intervalo atualizado.','success')
        text=request.form.get('text','').strip()
        if text:
            if len(text)>255: flash('A frase pode ter no máximo 255 caracteres.','error')
            else: db.session.add(MotivationalPhrase(user=current_user,text=text));db.session.commit();flash('Frase personalizada adicionada.','success')
        return redirect(url_for('main.phrases'))
    return render_template('phrases.html',default_phrases=DEFAULT_MOTIVATIONAL_PHRASES,custom_phrases=current_user.custom_phrases,interval=current_user.phrase_interval_minutes)
@bp.post('/phrases/<int:id>/delete')
@login_required
@limiter.limit('30 per minute')
def delete_phrase(id):
    if not current_user.is_premium: abort(403)
    phrase=db.session.get(MotivationalPhrase,id)
    if not phrase or phrase.user_id!=current_user.id: abort(404)
    db.session.delete(phrase);db.session.commit();flash('Frase removida.','success')
    return redirect(url_for('main.phrases'))
@bp.post('/profile/avatar')
@login_required
@limiter.limit('10 per minute')
def upload_avatar():
    try:
        current_user.avatar_path=_save_avatar(request.files.get('avatar'),current_user);db.session.commit()
        flash('Foto de perfil atualizada.','success')
    except ValueError as e:
        flash(str(e),'error')
    return redirect(url_for('main.profile'))
@bp.post('/profile/avatar/remove')
@login_required
@limiter.limit('30 per minute')
def remove_avatar():
    if current_user.avatar_path:
        _delete_avatar_file(current_user.avatar_path);current_user.avatar_path=None;db.session.commit()
        flash('Foto de perfil removida.','success')
    return redirect(url_for('main.profile'))
@bp.post('/profile/clear')
@login_required
@limiter.limit('10 per minute')
def clear_data():
    # ORM deletion preserves recurring-goal dependent records on all databases.
    for goal in Goal.query.filter_by(user_id=current_user.id): db.session.delete(goal)
    for template in GoalTemplate.query.filter_by(user_id=current_user.id): db.session.delete(template)
    UserAchievement.query.filter_by(user_id=current_user.id).delete()
    db.session.commit();flash('Dados removidos. Sua conta foi preservada.','success');return redirect(url_for('main.profile'))
@bp.get('/achievements')
@login_required
def achievements():
    from ..models import Achievement
    unlock_achievements(current_user)
    unlocked={x.achievement_id for x in UserAchievement.query.filter_by(user_id=current_user.id)}
    order={d['key']:i for i,d in enumerate(ACHIEVEMENT_DEFINITIONS)}
    items=sorted(Achievement.query.all(),key=lambda a:order.get(a.key,len(order)))
    by_group={}
    for a in items: by_group.setdefault(a.group,[]).append(a)
    groups=[{'name':name,'cards':cards} for name,cards in by_group.items()]
    return render_template('achievements.html',groups=groups,unlocked=unlocked,total=len(items))
@bp.get('/reports')
@login_required
def reports(): return render_template('reports.html', stats=stats(current_user))
@bp.route('/premium',methods=['GET','POST'])
@login_required
@limiter.limit('30 per minute', methods=['POST'])
def premium():
    if request.method=='POST':
        if not current_app.config.get('DEMO_MODE',False): abort(404)
        current_user.is_premium=not current_user.is_premium;db.session.commit();flash('Modo demonstração atualizado — nenhuma cobrança foi feita.','success');return redirect(url_for('main.premium'))
    return render_template('premium.html', demo_mode=current_app.config.get('DEMO_MODE',False))
