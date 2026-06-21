import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ..extensions import db, limiter
from ..models import User
bp=Blueprint('auth',__name__,url_prefix='/auth')
EMAIL_RE=re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
@bp.route('/login',methods=['GET','POST'])
@limiter.limit('5 per minute', methods=['POST'])
def login():
    if current_user.is_authenticated:return redirect(url_for('main.dashboard'))
    if request.method=='POST':
        u=User.query.filter_by(email=request.form.get('email','').lower().strip()).first()
        if u and u.check_password(request.form.get('password','')): login_user(u); return redirect(url_for('main.dashboard'))
        flash('E-mail ou senha inválidos.','error')
    return render_template('auth/login.html')
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
