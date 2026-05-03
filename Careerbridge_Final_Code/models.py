# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('graduate', 'employer', 'admin'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    graduate_profile = db.relationship('Graduate', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    employer_profile = db.relationship('Employer', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    admin_logs = db.relationship('AdminLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Graduate(db.Model):
    __tablename__ = 'graduates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    resume_text = db.Column(db.Text)
    resume_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = db.relationship('Application', backref='graduate', lazy=True, cascade='all, delete-orphan')
    match_analytics = db.relationship('MatchAnalytics', backref='graduate', lazy=True)
    
    def get_skills_list(self):
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []
    
    def __repr__(self):
        return f'<Graduate {self.full_name}>'

class Employer(db.Model):
    __tablename__ = 'employers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    company_description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    jobs = db.relationship('Job', backref='employer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employer {self.company_name}>'

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employers.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    job_type = db.Column(db.Enum('full-time', 'part-time', 'internship', 'contract'))
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    match_analytics = db.relationship('MatchAnalytics', backref='job', lazy=True)
    
    def get_requirements_list(self):
        if self.requirements:
            return [req.strip() for req in self.requirements.split(',') if req.strip()]
        return []
    
    def __repr__(self):
        return f'<Job {self.title}>'

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'reviewed', 'shortlisted', 'rejected', 'hired'), default='pending')
    match_score = db.Column(db.Float)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('graduate_id', 'job_id', name='unique_application'),
    )
    
    def __repr__(self):
        return f'<Application {self.id}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.title}>'

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminLog {self.action}>'

class MatchAnalytics(db.Model):
    __tablename__ = 'match_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey('graduates.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    skill_match_score = db.Column(db.Float)
    text_similarity_score = db.Column(db.Float)
    overall_match_score = db.Column(db.Float)
    algorithm_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('graduate_id', 'job_id', name='unique_match_analytics'),
    )
    
    def __repr__(self):
        return f'<MatchAnalytics {self.graduate_id}-{self.job_id}>'