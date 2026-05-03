# routes/employer.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, db, Employer, Job, Application, Graduate, Notification, MatchAnalytics
from utils.algorithms import MatchingAlgorithms

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'employer':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found. Please complete your profile.', 'error')
        return redirect(url_for('employer.profile'))
    
    jobs = Job.query.filter_by(employer_id=employer.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    
    # Calculate statistics
    total_applications = db.session.query(Application).join(Job).filter(Job.employer_id == employer.id).count()
    pending_applications = db.session.query(Application).join(Job).filter(
        Job.employer_id == employer.id, 
        Application.status == 'pending'
    ).count()
    
    return render_template('employer_dashboard.html', 
                         employer=employer, 
                         jobs=jobs,
                         notifications=notifications,
                         total_applications=total_applications,
                         pending_applications=pending_applications)

@employer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        # Create employer profile if it doesn't exist
        employer = Employer(user_id=current_user.id, company_name="")
        db.session.add(employer)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            employer.company_name = request.form.get('company_name', '')
            employer.company_description = request.form.get('company_description', '')
            employer.industry = request.form.get('industry', '')
            employer.website = request.form.get('website', '')
            employer.phone = request.form.get('phone', '')
            
            db.session.commit()
            flash('Company profile updated successfully', 'success')
            return redirect(url_for('employer.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            print(f"Profile update error: {e}")
    
    jobs = Job.query.filter_by(employer_id=employer.id).all()
    return render_template('employer_profile.html', employer=employer, jobs=jobs)

@employer_bp.route('/jobs')
@login_required
def jobs():
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found', 'error')
        return redirect(url_for('auth.logout'))
    
    jobs = Job.query.filter_by(employer_id=employer.id).order_by(Job.created_at.desc()).all()
    return render_template('employer_jobs.html', employer=employer, jobs=jobs)

@employer_bp.route('/job/new', methods=['GET', 'POST'])
@login_required
def new_job():
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found', 'error')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        try:
            # Process requirements - store as comma-separated string
            requirements_text = request.form.get('requirements', '')
            
            job = Job(
                employer_id=employer.id,
                title=request.form.get('title', ''),
                description=request.form.get('description', ''),
                requirements=requirements_text,
                location=request.form.get('location', ''),
                salary_range=request.form.get('salary_range', ''),
                job_type=request.form.get('job_type', 'full-time'),
                is_approved=False  # Needs admin approval
            )
            
            db.session.add(job)
            db.session.commit()
            
            flash('Job posted successfully! Waiting for admin approval.', 'success')
            return redirect(url_for('employer.jobs'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error posting job. Please try again.', 'error')
            print(f"Job posting error: {e}")
    
    return render_template('employer_new_job.html', employer=employer)

# routes/employer.py - Update the candidates route
@employer_bp.route('/candidates/<int:job_id>')
@login_required
def candidates(job_id):
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found', 'error')
        return redirect(url_for('auth.logout'))
    
    job = Job.query.filter_by(id=job_id, employer_id=employer.id).first_or_404()
    
    # Get all graduates with profiles
    graduates = Graduate.query.filter(
        Graduate.skills.isnot(None),
        Graduate.skills != ''
    ).all()
    
    print(f"Found {len(graduates)} graduates with skills for job {job_id}")
    
    # Find matches
    matches = []
    for graduate in graduates:
        try:
            match_result = MatchingAlgorithms.calculate_overall_match(
                graduate.skills,
                graduate.resume_text or "",
                job.requirements,
                job.description
            )
            
            print(f"Graduate {graduate.full_name}: {match_result['overall_score']}% match")
            
            if match_result['overall_score'] >= 60:  # 60% threshold
                matches.append({
                    'graduate': graduate,
                    'match_score': match_result['overall_score'],
                    'skill_match': match_result['skill_match'],
                    'text_similarity': match_result['text_similarity']
                })
                
                # Store match analytics in database
                match_analytics = MatchAnalytics.query.filter_by(
                    graduate_id=graduate.id,
                    job_id=job.id
                ).first()
                
                if match_analytics:
                    match_analytics.skill_match_score = match_result['skill_match']
                    match_analytics.text_similarity_score = match_result['text_similarity']
                    match_analytics.overall_match_score = match_result['overall_score']
                else:
                    match_analytics = MatchAnalytics(
                        graduate_id=graduate.id,
                        job_id=job.id,
                        skill_match_score=match_result['skill_match'],
                        text_similarity_score=match_result['text_similarity'],
                        overall_match_score=match_result['overall_score'],
                        algorithm_version='v1.2'
                    )
                    db.session.add(match_analytics)
                    
        except Exception as e:
            print(f"Error calculating match for graduate {graduate.id}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"Found {len(matches)} matches for job {job_id}")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving match analytics: {e}")
    
    # Sort matches by score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    return render_template('employer_candidates.html', 
                         employer=employer, 
                         job=job, 
                         matches=matches)

@employer_bp.route('/applications/<int:job_id>')
@login_required
def applications(job_id):
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found', 'error')
        return redirect(url_for('auth.logout'))
    
    job = Job.query.filter_by(id=job_id, employer_id=employer.id).first_or_404()
    
    applications = Application.query.filter_by(job_id=job_id)\
        .join(Graduate)\
        .join(User)\
        .order_by(Application.applied_at.desc())\
        .all()
    
    return render_template('employer_applications.html', employer=employer, job=job, applications=applications)

@employer_bp.route('/application/<int:application_id>/update-status', methods=['POST'])
@login_required
def update_application_status(application_id):
    employer = Employer.query.filter_by(user_id=current_user.id).first()
    if not employer:
        flash('Employer profile not found', 'error')
        return redirect(url_for('auth.logout'))
    
    application = Application.query.get_or_404(application_id)
    
    # Verify the employer owns this job
    if application.job.employer_id != employer.id:
        flash('Access denied', 'error')
        return redirect(url_for('employer.dashboard'))
    
    try:
        new_status = request.form.get('status')
        application.status = new_status
        
        # Create notification for graduate
        notification = Notification(
            user_id=application.graduate.user_id,
            title='Application Status Updated',
            message=f'Your application for {application.job.title} has been {new_status}'
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Application status updated', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating application status', 'error')
        print(f"Status update error: {e}")
    
    return redirect(url_for('employer.applications', job_id=application.job_id))