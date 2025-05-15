from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from src.models.survey import Survey

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all surveys created by the current user
    user_surveys = Survey.query.filter_by(user_id=current_user.user_id).all()
    return render_template('dashboard.html', surveys=user_surveys)
