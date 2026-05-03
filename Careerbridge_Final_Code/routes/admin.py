from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Job, Employer, Graduate, Application, MatchAnalytics, AdminLog
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Statistics
    total_users = User.query.count()
    total_graduates = Graduate.query.count()
    total_employers = Employer.query.count()
    total_jobs = Job.query.count()
    pending_jobs = Job.query.filter_by(is_approved=False).count()
    
    # Recent activity
    recent_logs = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_graduates=total_graduates,
                         total_employers=total_employers,
                         total_jobs=total_jobs,
                         pending_jobs=pending_jobs,
                         recent_logs=recent_logs)

@admin_bp.route('/users')
@login_required
def users():
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/jobs')
@login_required
def jobs():
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    jobs = Job.query.all()
    return render_template('admin_jobs.html', jobs=jobs)

@admin_bp.route('/job/<int:job_id>/approve', methods=['POST'])
@login_required
def approve_job(job_id):
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    job = Job.query.get_or_404(job_id)
    job.is_approved = True
    
    # Log the action
    log = AdminLog(
        action=f'Approved job: {job.title}',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Job approved successfully', 'success')
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/reports')
@login_required
def reports():
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)  # Last 6 months
    
    # Platform Statistics
    total_users = User.query.count()
    total_graduates = Graduate.query.count()
    total_employers = Employer.query.count()
    total_jobs = Job.query.count()
    pending_jobs = Job.query.filter_by(is_approved=False).count()
    total_applications = Application.query.count()
    
    # Average match score (only from applications with match scores)
    avg_match_score_result = db.session.query(
        func.avg(Application.match_score)
    ).filter(Application.match_score.isnot(None)).scalar()
    avg_match_score = round(avg_match_score_result or 0, 2)
    
    # Successful hires
    successful_hires = Application.query.filter_by(status='hired').count()
    
    # Employment Trends - Last 6 months by month
    trends_data = get_monthly_trends(start_date, end_date)
    
    # Top Skills Analysis
    top_skills = get_top_skills()
    
    # Platform Performance Metrics
    performance_metrics = get_performance_metrics()
    
    # Industry Distribution
    industry_distribution = get_industry_distribution()
    
    # Algorithm Performance
    algorithm_performance = get_algorithm_performance()
    
    # User Growth Metrics
    user_growth = get_user_growth_metrics(start_date)
    
    # Job Market Insights
    job_market_insights = get_job_market_insights()
    
    return render_template('admin_reports.html', 
                         total_users=total_users,
                         total_graduates=total_graduates,
                         total_employers=total_employers,
                         total_jobs=total_jobs,
                         pending_jobs=pending_jobs,
                         total_applications=total_applications,
                         avg_match_score=avg_match_score,
                         successful_hires=successful_hires,
                         trends_data=trends_data,
                         top_skills=top_skills,
                         performance_metrics=performance_metrics,
                         industry_distribution=industry_distribution,
                         algorithm_performance=algorithm_performance,
                         user_growth=user_growth,
                         job_market_insights=job_market_insights)

@admin_bp.route('/api/reports/export')
@login_required
def export_reports():
    """Export reports data as JSON"""
    if current_user.user_type != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all report data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    report_data = {
        'platform_statistics': {
            'total_users': User.query.count(),
            'total_graduates': Graduate.query.count(),
            'total_employers': Employer.query.count(),
            'total_jobs': Job.query.count(),
            'pending_jobs': Job.query.filter_by(is_approved=False).count(),
            'total_applications': Application.query.count(),
            'successful_hires': Application.query.filter_by(status='hired').count()
        },
        'generated_at': datetime.utcnow().isoformat(),
        'date_range': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    }
    
    return jsonify(report_data)

@admin_bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    if current_user.user_type != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    
    # Log the action
    action = 'Activated' if user.is_active else 'Deactivated'
    log = AdminLog(
        action=f'{action} user: {user.email}',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'User {action.lower()} successfully', 'success')
    return redirect(url_for('admin.users'))

# Helper functions for reports (keep the same implementation as before)
def get_monthly_trends(start_date, end_date):
    """Get monthly application and hiring trends"""
    # Monthly applications
    monthly_applications = db.session.query(
        extract('year', Application.applied_at).label('year'),
        extract('month', Application.applied_at).label('month'),
        func.count(Application.id).label('count')
    ).filter(
        Application.applied_at >= start_date,
        Application.applied_at <= end_date
    ).group_by(
        extract('year', Application.applied_at),
        extract('month', Application.applied_at)
    ).order_by('year', 'month').all()
    
    # Monthly hires
    monthly_hires = db.session.query(
        extract('year', Application.applied_at).label('year'),
        extract('month', Application.applied_at).label('month'),
        func.count(Application.id).label('count')
    ).filter(
        Application.applied_at >= start_date,
        Application.applied_at <= end_date,
        Application.status == 'hired'
    ).group_by(
        extract('year', Application.applied_at),
        extract('month', Application.applied_at)
    ).order_by('year', 'month').all()
    
    # Create labels and data arrays
    labels = []
    applications_data = []
    hires_data = []
    
    current_date = start_date
    while current_date <= end_date:
        month_key = f"{current_date.strftime('%b')} {current_date.year}"
        labels.append(month_key)
        
        # Find applications for this month
        app_count = next((app.count for app in monthly_applications 
                         if app.month == current_date.month and app.year == current_date.year), 0)
        applications_data.append(app_count)
        
        # Find hires for this month
        hire_count = next((hire.count for hire in monthly_hires 
                          if hire.month == current_date.month and hire.year == current_date.year), 0)
        hires_data.append(hire_count)
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return {
        'labels': labels[-6:],  # Last 6 months
        'applications': applications_data[-6:],
        'hires': hires_data[-6:]
    }

def get_top_skills():
    """Extract and analyze top skills from graduates and jobs"""
    # Get all skills from graduates
    graduate_skills = []
    graduates = Graduate.query.filter(Graduate.skills.isnot(None)).all()
    for grad in graduates:
        if grad.skills:
            skills = [skill.strip().lower() for skill in grad.skills.split(',')]
            graduate_skills.extend(skills)
    
    # Get all skills from job requirements
    job_skills = []
    jobs = Job.query.filter(Job.requirements.isnot(None)).all()
    for job in jobs:
        if job.requirements:
            skills = [skill.strip().lower() for skill in job.requirements.split(',')]
            job_skills.extend(skills)
    
    # Combine and count frequencies
    all_skills = graduate_skills + job_skills
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Get top 10 skills
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate percentages for display
    total_skill_occurrences = sum(skill_counts.values())
    top_skills_with_percent = []
    for skill, count in top_skills:
        percentage = round((count / total_skill_occurrences) * 100, 1) if total_skill_occurrences > 0 else 0
        top_skills_with_percent.append({
            'skill': skill.title(),
            'count': count,
            'percentage': percentage
        })
    
    return top_skills_with_percent

def get_performance_metrics():
    """Calculate platform performance metrics"""
    # System Uptime (simulated - in production this would come from monitoring)
    # For demo, we'll calculate based on successful operations
    
    # Average Response Time (simulated)
    total_applications = Application.query.count()
    successful_matches = MatchAnalytics.query.filter(MatchAnalytics.overall_match_score >= 60).count()
    
    # Calculate success rate for matching
    match_success_rate = 0
    if total_applications > 0:
        match_success_rate = round((successful_matches / total_applications) * 100, 1)
    
    # User satisfaction (simulated based on application to hire ratio)
    total_hires = Application.query.filter_by(status='hired').count()
    hire_success_rate = 0
    if total_applications > 0:
        hire_success_rate = round((total_hires / total_applications) * 100, 1)
    
    return {
        'system_uptime': 99.8,  # Simulated
        'avg_response_time': 1.2,  # Simulated
        'matching_accuracy': match_success_rate,
        'user_satisfaction': min(100, hire_success_rate * 2)  # Scale for demo
    }

def get_industry_distribution():
    """Get industry distribution from employers"""
    industry_counts = db.session.query(
        Employer.industry,
        func.count(Employer.id).label('count')
    ).filter(
        Employer.industry.isnot(None),
        Employer.industry != ''
    ).group_by(Employer.industry).all()
    
    total_employers_with_industry = sum(count for _, count in industry_counts)
    
    distribution = []
    for industry, count in industry_counts:
        percentage = round((count / total_employers_with_industry) * 100, 1) if total_employers_with_industry > 0 else 0
        distribution.append({
            'industry': industry,
            'count': count,
            'percentage': percentage
        })
    
    # Sort by count descending
    distribution.sort(key=lambda x: x['count'], reverse=True)
    
    return distribution

def get_algorithm_performance():
    """Calculate algorithm performance metrics"""
    # Skill matching accuracy (based on applications with high match scores)
    high_match_applications = Application.query.filter(Application.match_score >= 70).count()
    total_applications_with_score = Application.query.filter(Application.match_score.isnot(None)).count()
    
    skill_accuracy = 0
    if total_applications_with_score > 0:
        skill_accuracy = round((high_match_applications / total_applications_with_score) * 100, 1)
    
    # Text similarity performance (using match analytics)
    text_similarity_avg = db.session.query(
        func.avg(MatchAnalytics.text_similarity_score)
    ).filter(MatchAnalytics.text_similarity_score.isnot(None)).scalar() or 0
    
    text_accuracy = round(text_similarity_avg, 1)
    
    # Overall matching success (applications with match score > 60%)
    successful_matches = Application.query.filter(Application.match_score >= 60).count()
    overall_success = 0
    if total_applications_with_score > 0:
        overall_success = round((successful_matches / total_applications_with_score) * 100, 1)
    
    return {
        'skill_matching_accuracy': skill_accuracy,
        'text_similarity_accuracy': text_accuracy,
        'overall_matching_success': overall_success
    }

def get_user_growth_metrics(start_date):
    """Calculate user growth metrics"""
    # Monthly user growth
    monthly_users = db.session.query(
        extract('year', User.created_at).label('year'),
        extract('month', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= start_date).group_by(
        extract('year', User.created_at),
        extract('month', User.created_at)
    ).order_by('year', 'month').all()
    
    # Calculate growth rates
    total_users = User.query.count()
    users_last_month = sum(month.count for month in monthly_users[-1:])
    users_previous_month = sum(month.count for month in monthly_users[-2:-1]) if len(monthly_users) >= 2 else 0
    
    monthly_growth = 0
    if users_previous_month > 0:
        monthly_growth = round(((users_last_month - users_previous_month) / users_previous_month) * 100, 1)
    
    # Graduate vs Employer growth
    recent_graduates = Graduate.query.join(User).filter(User.created_at >= start_date).count()
    recent_employers = Employer.query.join(User).filter(User.created_at >= start_date).count()
    
    total_recent_users = recent_graduates + recent_employers
    graduate_growth = round((recent_graduates / total_recent_users) * 100, 1) if total_recent_users > 0 else 0
    employer_growth = round((recent_employers / total_recent_users) * 100, 1) if total_recent_users > 0 else 0
    
    # Active user rate (users with recent activity)
    active_cutoff = datetime.utcnow() - timedelta(days=30)
    active_users = User.query.filter(
        or_(
            User.updated_at >= active_cutoff,
            User.created_at >= active_cutoff
        )
    ).count()
    
    active_rate = round((active_users / total_users) * 100, 1) if total_users > 0 else 0
    
    return {
        'monthly_growth': monthly_growth,
        'graduate_growth': graduate_growth,
        'employer_growth': employer_growth,
        'active_user_rate': active_rate
    }

def get_job_market_insights():
    """Calculate job market insights"""
    # Average applications per job
    job_applications = db.session.query(
        Job.id,
        func.count(Application.id).label('app_count')
    ).outerjoin(Application).group_by(Job.id).all()
    
    avg_applications_per_job = 0
    if job_applications:
        avg_applications_per_job = round(sum(job.app_count for job in job_applications) / len(job_applications), 1)
    
    # Job approval rate
    total_jobs = Job.query.count()
    approved_jobs = Job.query.filter_by(is_approved=True).count()
    approval_rate = round((approved_jobs / total_jobs) * 100, 1) if total_jobs > 0 else 0
    
    # Average time to fill (simplified - using application to hire time)
    hire_times = db.session.query(
        Application.applied_at,
        Application.updated_at
    ).filter(
        Application.status == 'hired',
        Application.updated_at.isnot(None)
    ).all()
    
    avg_days_to_fill = 28  # Default fallback
    if hire_times:
        total_days = sum((hire.updated_at - hire.applied_at).days for hire in hire_times)
        avg_days_to_fill = round(total_days / len(hire_times))
    
    # Employer satisfaction (based on job posting and hiring activity)
    active_employers = Employer.query.join(Job).filter(Job.is_active == True).distinct().count()
    total_employers = Employer.query.count()
    employer_satisfaction = round((active_employers / total_employers) * 100, 1) if total_employers > 0 else 0
    
    return {
        'avg_applications_per_job': avg_applications_per_job,
        'job_approval_rate': approval_rate,
        'avg_time_to_fill': avg_days_to_fill,
        'employer_satisfaction': employer_satisfaction
    }