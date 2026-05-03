# routes/graduate.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Employer, db, Graduate, Job, Application, Notification, MatchAnalytics
from utils.algorithms import MatchingAlgorithms
import json

graduate_bp = Blueprint('graduate', __name__)

@graduate_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'graduate':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    graduate = Graduate.query.filter_by(user_id=current_user.id).first()
    if not graduate:
        flash('Graduate profile not found. Please complete your profile.', 'error')
        return redirect(url_for('graduate.profile'))
    
    # Get applications with job details
    applications = Application.query.filter_by(graduate_id=graduate.id).join(Job).join(Employer).all()
    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('graduate_dashboard.html', 
                         graduate=graduate, 
                         applications=applications,
                         notifications=notifications)

@graduate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    graduate = Graduate.query.filter_by(user_id=current_user.id).first()
    if not graduate:
        # Create graduate profile if it doesn't exist
        graduate = Graduate(user_id=current_user.id, full_name="")
        db.session.add(graduate)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            graduate.full_name = request.form.get('full_name', '')
            graduate.phone = request.form.get('phone', '')
            graduate.education = request.form.get('education', '')
            
            # Process skills - store as comma-separated string
            skills_text = request.form.get('skills', '')
            graduate.skills = skills_text
            
            graduate.resume_text = request.form.get('resume_text', '')
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('graduate.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            print(f"Profile update error: {e}")
    
    return render_template('graduate_profile.html', graduate=graduate)

@graduate_bp.route('/jobs')
@login_required
def jobs():
    graduate = Graduate.query.filter_by(user_id=current_user.id).first()
    if not graduate:
        flash('Please complete your profile first', 'error')
        return redirect(url_for('graduate.profile'))
    
    # Get all approved and active jobs
    jobs = Job.query.filter_by(is_active=True, is_approved=True).all()
    
    # Calculate matches
    matches = []
    for job in jobs:
        match_result = MatchingAlgorithms.calculate_overall_match(
            graduate.skills,
            graduate.resume_text,
            job.requirements,
            job.description
        )
        
        # Store match analytics in database
        match_analytics = MatchAnalytics(
            graduate_id=graduate.id,
            job_id=job.id,
            skill_match_score=match_result['skill_match'],
            text_similarity_score=match_result['text_similarity'],
            overall_match_score=match_result['overall_score'],
            algorithm_version='v1.2'
        )
        
        # Update or insert match analytics
        existing_analytics = MatchAnalytics.query.filter_by(
            graduate_id=graduate.id, 
            job_id=job.id
        ).first()
        
        if existing_analytics:
            existing_analytics.skill_match_score = match_result['skill_match']
            existing_analytics.text_similarity_score = match_result['text_similarity']
            existing_analytics.overall_match_score = match_result['overall_score']
        else:
            db.session.add(match_analytics)
        
        if match_result['overall_score'] >= 60:
            matches.append({
                'job': job,
                'match_score': match_result['overall_score'],
                'skill_match': match_result['skill_match'],
                'text_similarity': match_result['text_similarity']
            })
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving match analytics: {e}")
    
    # Sort matches by score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    return render_template('graduate_jobs.html', graduate=graduate, matches=matches)

@graduate_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    graduate = Graduate.query.filter_by(user_id=current_user.id).first()
    if not graduate:
        flash('Please complete your profile first', 'error')
        return redirect(url_for('graduate.profile'))
    
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        graduate_id=graduate.id, 
        job_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job', 'warning')
        return redirect(url_for('graduate.jobs'))
    
    try:
        # Calculate match score
        match_result = MatchingAlgorithms.calculate_overall_match(
            graduate.skills,
            graduate.resume_text,
            job.requirements,
            job.description
        )
        
        # Create application
        application = Application(
            graduate_id=graduate.id,
            job_id=job_id,
            cover_letter=request.form.get('cover_letter', ''),
            match_score=match_result['overall_score'],
            status='pending'
        )
        
        db.session.add(application)
        
        # Create notification for employer
        notification = Notification(
            user_id=job.employer.user_id,
            title='New Application',
            message=f'{graduate.full_name} applied for your job: {job.title}'
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Application submitted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error submitting application. Please try again.', 'error')
        print(f"Application error: {e}")
    
    return redirect(url_for('graduate.jobs'))

@graduate_bp.route('/applications')
@login_required
def applications():
    graduate = Graduate.query.filter_by(user_id=current_user.id).first()
    if not graduate:
        flash('Please complete your profile first', 'error')
        return redirect(url_for('graduate.profile'))
    
    applications = Application.query.filter_by(graduate_id=graduate.id)\
        .join(Job)\
        .join(Employer)\
        .order_by(Application.applied_at.desc())\
        .all()
    
    return render_template('graduate_applications.html', graduate=graduate, applications=applications)