from flask import Flask, flash, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
from config import Config
from models import Graduate, Job, db, User
from routes.auth import auth_bp
from routes.graduate import graduate_bp
from routes.employer import employer_bp
from routes.admin import admin_bp
import os

from utils.algorithms import MatchingAlgorithms

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail = Mail(app)
    
    # Flask-Login configuration
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(graduate_bp, url_prefix='/graduate')
    app.register_blueprint(employer_bp, url_prefix='/employer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')
        # Custom Jinja2 filters
    @app.template_filter('split_string')
    def split_string_filter(s, delimiter=','):
        """Split a string by delimiter and return list"""
        if not s:
            return []
        return [item.strip() for item in s.split(delimiter) if item.strip()]
    
    @app.template_filter('contains_skill')
    def contains_skill_filter(skills_string, skill):
        """Check if skills string contains a specific skill"""
        if not skills_string or not skill:
            return False
        skill_list = [s.strip().lower() for s in skills_string.split(',')]
        return skill.strip().lower() in skill_list
    
    @graduate_bp.route('/jobs')

    @login_required
    def jobs():
        graduate = Graduate.query.filter_by(user_id=current_user.id).first()
        if not graduate:
            flash('Graduate profile not found', 'error')
            return redirect(url_for('auth.logout'))
        
        jobs = Job.query.filter_by(is_active=True, is_approved=True).all()
        
        # Get matches and pre-process skills
        matches = MatchingAlgorithms.find_job_matches(graduate, jobs)
        
        # Pre-process skills for templates
        for match in matches:
            if match['job'].requirements:
                match['job_skills_list'] = match['job'].requirements.split(',')
            else:
                match['job_skills_list'] = []
            
            if graduate.skills:
                match['grad_skills_list'] = graduate.skills.split(',')
            else:
                match['grad_skills_list'] = []
        
        return render_template('graduate_jobs.html', graduate=graduate, matches=matches)


    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.user_type == 'graduate':
            return redirect(url_for('graduate.dashboard'))
        elif current_user.user_type == 'employer':
            return redirect(url_for('employer.dashboard'))
        elif current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('index'))
    

    @app.template_filter('split')
    def split_filter(s, delimiter=','):
        """Split a string by delimiter"""
        if s is None:
            return []
        return s.split(delimiter)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # API routes for algorithms
    @app.route('/api/calculate-match', methods=['POST'])
    @login_required
    def calculate_match():
        data = request.json
        from utils.algorithms import MatchingAlgorithms
        
        result = MatchingAlgorithms.calculate_overall_match(
            data.get('candidate_skills', []),
            data.get('resume_text', ''),
            data.get('job_skills', []),
            data.get('job_description', '')
        )
        
        return jsonify(result)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
   
    with app.app_context():
            # Create all tables
            db.create_all()
        
            # Create admin user if not exists
            from models import User
            from werkzeug.security import generate_password_hash
            
            admin_user = User.query.filter_by(email='admin@gmail.com').first()
            if not admin_user:
                admin_user = User(
                    email='admin@gmail.com',
                    password_hash=generate_password_hash('admin'),
                    user_type='admin',
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created: admin@gmail.com / admin")
        
            app.run(debug=True, host='0.0.0.0', port=5000)