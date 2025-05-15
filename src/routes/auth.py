from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.extensions import db
from src.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Form validation
        if not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
            
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
            
        # Create new user
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Form validation
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')
            
        # Check user credentials
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
            
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log in user
        login_user(user, remember=remember)
        
        # Redirect to the page the user was trying to access
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
