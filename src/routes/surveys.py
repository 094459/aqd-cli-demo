from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from src.extensions import db
from src.models.survey import Survey, SurveyOption, SurveyResponse

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/survey/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Form validation
        if not title:
            flash('Survey title is required', 'danger')
            return render_template('surveys/create.html')
            
        # Create new survey
        new_survey = Survey(
            user_id=current_user.user_id,
            title=title,
            description=description
        )
        db.session.add(new_survey)
        db.session.commit()
        
        # Get options from form
        options = []
        for i in range(1, 6):  # Maximum 5 options
            option_text = request.form.get(f'option_{i}')
            if option_text:
                options.append(option_text)
        
        # Add options to the survey
        for i, option_text in enumerate(options, 1):
            option = SurveyOption(
                survey_id=new_survey.survey_id,
                option_text=option_text,
                option_order=i
            )
            db.session.add(option)
        
        db.session.commit()
        flash('Survey created successfully', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('surveys/create.html')

@survey_bp.route('/survey/<int:survey_id>')
@login_required
def view_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Check if the current user is the owner of the survey
    if survey.user_id != current_user.user_id:
        abort(403)
        
    options = SurveyOption.query.filter_by(survey_id=survey_id).order_by(SurveyOption.option_order).all()
    
    # Get the share link for the survey
    share_link = survey.get_share_link(request.host_url.rstrip('/'))
    
    return render_template('surveys/view.html', survey=survey, options=options, share_link=share_link)

@survey_bp.route('/survey/<int:survey_id>/results')
@login_required
def view_results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Check if the current user is the owner of the survey
    if survey.user_id != current_user.user_id:
        abort(403)
        
    options = SurveyOption.query.filter_by(survey_id=survey_id).order_by(SurveyOption.option_order).all()
    
    # Get response counts for each option
    results = []
    total_responses = survey.get_response_count()
    
    for option in options:
        response_count = SurveyResponse.query.filter_by(option_id=option.option_id).count()
        percentage = 0
        if total_responses > 0:
            percentage = (response_count / total_responses) * 100
            
        results.append({
            'option': option,
            'count': response_count,
            'percentage': round(percentage, 1)
        })
    
    return render_template('surveys/results.html', survey=survey, results=results, total_responses=total_responses)

@survey_bp.route('/survey/<int:survey_id>/respond', methods=['GET', 'POST'])
def respond_to_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Check if the survey is active
    if not survey.is_active:
        flash('This survey is no longer active', 'info')
        return redirect(url_for('main.index'))
        
    options = SurveyOption.query.filter_by(survey_id=survey_id).order_by(SurveyOption.option_order).all()
    
    if request.method == 'POST':
        option_id = request.form.get('option_id')
        email = request.form.get('email')
        
        # Form validation
        if not option_id:
            flash('Please select an option', 'danger')
            return render_template('surveys/respond.html', survey=survey, options=options)
            
        # Create new response
        response = SurveyResponse(
            survey_id=survey_id,
            option_id=option_id,
            respondent_email=email
        )
        db.session.add(response)
        db.session.commit()
        
        flash('Thank you for your response!', 'success')
        return render_template('surveys/thank_you.html')
        
    return render_template('surveys/respond.html', survey=survey, options=options)

@survey_bp.route('/survey/<int:survey_id>/toggle', methods=['POST'])
@login_required
def toggle_survey_status(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Check if the current user is the owner of the survey
    if survey.user_id != current_user.user_id:
        abort(403)
        
    # Toggle the active status
    survey.is_active = not survey.is_active
    db.session.commit()
    
    status = "activated" if survey.is_active else "deactivated"
    flash(f'Survey {status} successfully', 'success')
    
    return redirect(url_for('survey.view_survey', survey_id=survey_id))

@survey_bp.route('/survey/<int:survey_id>/delete', methods=['POST'])
@login_required
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Check if the current user is the owner of the survey
    if survey.user_id != current_user.user_id:
        abort(403)
        
    db.session.delete(survey)
    db.session.commit()
    
    flash('Survey deleted successfully', 'success')
    return redirect(url_for('main.dashboard'))
