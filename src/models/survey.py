from datetime import datetime
from src.extensions import db

class Survey(db.Model):
    __tablename__ = 'Surveys'
    
    survey_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('SurveyOption', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, title, description=None):
        self.user_id = user_id
        self.title = title
        self.description = description
        
    def get_share_link(self, request_host):
        return f"{request_host}/survey/{self.survey_id}/respond"
        
    def get_response_count(self):
        return len(self.responses)


class SurveyOption(db.Model):
    __tablename__ = 'Survey_Options'
    
    option_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('Surveys.survey_id', ondelete='CASCADE'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    option_order = db.Column(db.Integer, nullable=False)
    
    # Relationships
    responses = db.relationship('SurveyResponse', backref='option', lazy=True)
    
    __table_args__ = (
        db.CheckConstraint('option_order BETWEEN 1 AND 5', name='check_option_order'),
    )
    
    def __init__(self, survey_id, option_text, option_order):
        self.survey_id = survey_id
        self.option_text = option_text
        self.option_order = option_order


class SurveyResponse(db.Model):
    __tablename__ = 'Survey_Responses'
    
    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('Surveys.survey_id', ondelete='CASCADE'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('Survey_Options.option_id', ondelete='CASCADE'), nullable=False)
    respondent_email = db.Column(db.Text)
    response_date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    def __init__(self, survey_id, option_id, respondent_email=None):
        self.survey_id = survey_id
        self.option_id = option_id
        self.respondent_email = respondent_email
