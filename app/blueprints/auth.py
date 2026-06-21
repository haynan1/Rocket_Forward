import re
import smtplib
from email.message import EmailMessage
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from ..extensions import db, limiter
from ..models import User
bp=Blueprint('auth',__name__,url_prefix='/auth')
EMAIL_RE=re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _reset_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='rocket-forward-password-reset')


def password_reset_token(user):
    return _reset_serializer().dumps({'user_id': user.id, 'password_hash': user.password_hash})


def user_from_reset_token(token):
    try:
        data = _reset_serializer().loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return None
    user = db.session.get(User, data.get('user_id'))
    return user if user and user.password_hash == data.get('password_hash') else None


def _send_reset_email(user, reset_url):
    server = current_app.config.get('SMTP_SERVER')
    if not server:
        current_app.logger.warning('Configure SMTP_SERVER para enviar recuperação de senha. Link temporário: %s', reset_url)
        return False
    message = EmailMessage()
    message['Subject'] = 'Recupere sua senha — Rocket Forward'
    message['From'] = current_app.config['SMTP_SENDER']
    message['To'] = user.email
    message.set_content(f'Abra este link para criar uma nova senha (ele expira em 1 hora):\n\n{reset_url}')
    with smtplib.SMTP(server, current_app.config['SMTP_PORT']) as smtp:
        if current_app.config.get('SMTP_USE_TLS'):
            smtp.starttls()
        if current_app.config.get('SMTP_USERNAME'):
            smtp.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
        smtp.send_message(message)
    return True
@bp.route('/login',methods=['GET','POST'])
@limiter.limit('5 per minute', methods=['POST'])
def login():
    if current_user.is_authenticated:return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        u=User.query.filter_by(email=request.form.get('email','').lower().strip()).first()
        if u and u.check_password(request.form.get('password','')): login_user(u); return redirect(url_for('main.dashboard'))
        flash('E-mail ou senha inválidos.','error')
    return render_template('auth/login.html')
@bp.route('/forgot-password',methods=['GET','POST'])
@limiter.limit('5 per minute', methods=['POST'])
def forgot_password():
    if request.method=='POST':
        user=User.query.filter_by(email=request.form.get('email','').lower().strip()).first()
        if user:
            reset_url=url_for('auth.reset_password',token=password_reset_token(user),_external=True)
            try: _send_reset_email(user,reset_url)
            except (OSError, smtplib.SMTPException): current_app.logger.exception('Não foi possível enviar o e-mail de recuperação.')
        flash('Se esse e-mail tiver uma conta, enviaremos um link para criar uma nova senha.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
@bp.route('/reset-password/<token>',methods=['GET','POST'])
@limiter.limit('10 per minute', methods=['POST'])
def reset_password(token):
    user=user_from_reset_token(token)
    if not user:
        flash('Este link de recuperação expirou ou já foi usado. Peça outro.','error')
        return redirect(url_for('auth.forgot_password'))
    if request.method=='POST':
        password=request.form.get('password','')
        if len(password)<8:
            flash('A senha deve ter pelo menos 8 caracteres.','error')
        elif password!=request.form.get('password_confirmation',''):
            flash('As senhas não são iguais.','error')
        else:
            user.set_password(password);db.session.commit();login_user(user)
            flash('Senha alterada. Você está de volta à missão!','success')
            return redirect(url_for('main.dashboard'))
    return render_template('auth/reset_password.html',token=token)
@bp.route('/register',methods=['GET','POST'])
@limiter.limit('5 per minute', methods=['POST'])
def register():
    if request.method=='POST':
        email=request.form.get('email','').lower().strip(); password=request.form.get('password','')
        if not email or not EMAIL_RE.match(email): flash('Informe um e-mail válido.','error')
        elif len(password)<8: flash('A senha deve ter pelo menos 8 caracteres.','error')
        elif User.query.filter_by(email=email).first(): flash('Este e-mail já está em uso.','error')
        else:
            u=User(name=request.form.get('name','').strip() or 'Astronauta',email=email);u.set_password(password);db.session.add(u);db.session.commit();login_user(u);flash('Conta criada. Sua missão começa agora!','success');return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html')
@bp.get('/logout')
def logout(): logout_user(); return redirect(url_for('auth.login'))
