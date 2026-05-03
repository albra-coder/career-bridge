# create_test_data.py
from app import create_app
from models import db, User, Graduate, Employer, Job
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        print("Creating test data...")
        
        # Create test graduates
        graduate_users = [
            ('john.doe@email.com', 'John Doe', 'JavaScript, Python, React, Node.js, MongoDB'),
            ('sarah.smith@email.com', 'Sarah Smith', 'Python, Machine Learning, SQL, Data Analysis'),
            ('mike.chen@email.com', 'Mike Chen', 'Java, Spring Boot, MySQL, AWS, Docker'),
            ('emily.wilson@email.com', 'Emily Wilson', 'Python, Django, React, PostgreSQL, Docker')
        ]
        
        for email, name, skills in graduate_users:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, user_type='graduate', is_active=True)
                user.set_password('password123')
                db.session.add(user)
                db.session.flush()
                
                graduate = Graduate(
                    user_id=user.id,
                    full_name=name,
                    skills=skills,
                    education=f"Bachelor of Science in Computer Science - {name.split()[0]} University",
                    resume_text=f"Experienced developer with skills in {skills}. Strong problem-solving abilities and team collaboration skills."
                )
                db.session.add(graduate)
                print(f"Created graduate: {name}")
        
        # Create test employer and jobs
        employer_user = User.query.filter_by(email='tech@company.com').first()
        if not employer_user:
            employer_user = User(email='tech@company.com', user_type='employer', is_active=True)
            employer_user.set_password('password123')
            db.session.add(employer_user)
            db.session.flush()
            
            employer = Employer(
                user_id=employer_user.id,
                company_name='Tech Solutions Inc',
                company_description='Leading technology company',
                industry='Technology'
            )
            db.session.add(employer)
            db.session.flush()
            
            # Create test jobs with various requirements
            test_jobs = [
                ('Frontend Developer', 'JavaScript, React, HTML, CSS, TypeScript', 'We need a frontend developer with React experience.'),
                ('Backend Developer', 'Python, Django, SQL, REST APIs, Docker', 'Looking for backend developer with Python and Django skills.'),
                ('Data Scientist', 'Python, Machine Learning, SQL, Statistics, TensorFlow', 'Join our data science team to build ML models.'),
                ('Full Stack Developer', 'JavaScript, React, Node.js, Python, MongoDB', 'Full stack developer needed for web applications.')
            ]
            
            for title, requirements, description in test_jobs:
                job = Job(
                    employer_id=employer.id,
                    title=title,
                    description=description,
                    requirements=requirements,
                    location='Remote',
                    salary_range='$80,000 - $120,000',
                    job_type='full-time',
                    is_approved=True
                )
                db.session.add(job)
                print(f"Created job: {title}")
        
        db.session.commit()
        print("Test data created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating test data: {e}")