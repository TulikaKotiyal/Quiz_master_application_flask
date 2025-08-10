from flask import jsonify,Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Subject, Chapter, Quiz, Question, Score
from forms import LoginForm, RegistrationForm, SubjectForm, ChapterForm, QuizForm, QuestionForm
from datetime import datetime

# Create blueprints for different sections of the app
main_bp = Blueprint('main', __name__)  # Main routes
auth_bp = Blueprint('auth', __name__)  # Authentication routes
admin_bp = Blueprint('admin', __name__)  # Admin routes
user_bp = Blueprint('user', __name__)  # User routes

# Main route: Redirects to the login page
@main_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

# Login route: Handles user login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        # Redirect to appropriate dashboard based on role
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', form=form)

        login_user(user)
        
        # Check if user is admin or regular user
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html', form=form)
    
# Registration route: Handles user registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If the user is already logged in, redirect them to the home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user
        new_user = User(
            username=form.username.data,  # Add username
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            full_name=form.full_name.data,
            qualification=form.qualification.data,
            dob=form.dob.data,
            is_admin=False  # Regular users are not admins
        )
        db.session.add(new_user)  # Add the new user to the database
        db.session.commit()  # Save changes to the database
        flash('Account created successfully! Please log in.', 'success')  # Show a success message
        return redirect(url_for('auth.login'))  # Redirect to the login page
    
    return render_template('auth/register.html', form=form)

# Logout route: Handles user logout
@auth_bp.route('/logout')
@login_required  # Only logged-in users can access this route
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('auth.login'))  # Redirect to the login page

# Admin dashboard route: Displays the admin dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin Dashboard - Only accessible to admins"""
    if not current_user.is_admin:
        abort(403)  # Forbidden access
    
    # Fetch statistics
    stats = {
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_subjects': Subject.query.count(),
        'total_chapters': Chapter.query.count(),
        'total_quizzes': Quiz.query.count(),
        'quizzes_attempted': Score.query.count(),
    }
    
    # Fetch recent quiz attempts
    recent_scores = Score.query.order_by(Score.time_stamp_of_attempt.desc()).limit(10).all()
    
    # Fetch a quiz (if needed)
    quiz = Quiz.query.first()  # Fetch the first quiz for demonstration
    
    # If no quiz exists, set quiz to None
    if not quiz:
        flash('No quizzes found. Please create a quiz first.', 'warning')
        quiz = None  # Set quiz to None to avoid errors in the template
    
    return render_template('admin/dashboard.html', 
                           stats=stats,
                           recent_scores=recent_scores,
                           quiz=quiz)  # Pass the quiz variable
# Subject management route: Allows admins to manage subjects
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = SubjectForm()
    if form.validate_on_submit():
        # Create a new subject
        new_subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))
    
    # Display all subjects
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects, form=form)
@admin_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        form.populate_obj(subject)
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))

    return render_template('admin/edit_subject.html', form=form, subject=subject)

@admin_bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    subject = Subject.query.get_or_404(subject_id)  # Get the subject
    db.session.delete(subject)  # Delete the subject
    db.session.commit()  # Save changes to the database
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.manage_subjects'))

# Chapter management route: Allows admins to manage chapters
@admin_bp.route('/chapters', methods=['GET', 'POST'])
@login_required
def manage_chapters():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = ChapterForm()
    
    # Fetch all subjects for the dropdown
    subjects = Subject.query.all()
    form.subject_id.choices = [(subject.id, subject.name) for subject in subjects]
    
    if form.validate_on_submit():
        # Create a new chapter
        new_chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('admin.manage_chapters'))
    
    # Fetch all chapters for display
    chapters = Chapter.query.all()
    
    # Debug: Print all subjects to the console
    print(f"Subjects: {subjects}")
    
    return render_template('admin/chapters.html', chapters=chapters, form=form, subjects=subjects)
@admin_bp.route('/add_chapter', methods=['POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]  # Populate subject dropdown
    
    if form.validate_on_submit():
        # Create a new chapter
        new_chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
    else:
        flash('Invalid form submission.', 'danger')
    
    return redirect(url_for('admin.manage_chapters'))

@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    chapter = Chapter.query.get_or_404(chapter_id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]  # Populate subject dropdown

    if form.validate_on_submit():
        form.populate_obj(chapter)
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.manage_chapters'))

    return render_template('admin/edit_chapter.html', form=form, chapter=chapter)

@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    chapter = Chapter.query.get_or_404(chapter_id)  # Get the chapter
    db.session.delete(chapter)  # Delete the chapter
    db.session.commit()  # Save changes to the database
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.manage_chapters'))

# Quiz management route: Allows admins to manage quizzes
@admin_bp.route('/quizzes', methods=['GET', 'POST'])
@login_required
def manage_quizzes():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = QuizForm()
    
    # Fetch all subjects for the dropdown
    subjects = Subject.query.all()
    form.subject_id.choices = [(subject.id, subject.name) for subject in subjects]  # Populate subject_id choices
    
    if form.validate_on_submit():
        # Create a new quiz
        new_quiz = Quiz(
            title=form.title.data,
            chapter_id=form.chapter_id.data,
            date_of_quiz=form.date_of_quiz.data,
            time_duration=form.duration.data,
            remarks=form.remarks.data
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('admin.manage_quizzes'))
    
    # Fetch all quizzes for display
    quizzes = Quiz.query.all()
    
    subjects = Subject.query.all()
    
    return render_template('admin/quizzes.html', quizzes=quizzes, form=form, subjects=subjects)

@admin_bp.route('/get_chapters', methods=['GET'])
@login_required
def get_chapters():
    subject_id = request.args.get('subject_id')
    if not subject_id:
        return jsonify({"error": "Subject ID is required"}), 400

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{'id': chapter.id, 'name': chapter.name} for chapter in chapters])

@admin_bp.route('/add_quiz', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    form = QuizForm()
    
    # Populate subject and chapter dropdowns
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Create a new quiz
            new_quiz = Quiz(
                title=form.title.data,
                chapter_id=form.chapter_id.data,
                date_of_quiz=form.date_of_quiz.data,
                time_duration=form.duration.data,
                remarks=form.remarks.data
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('admin.manage_quizzes'))
        else:
            # If validation fails, flash errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", 'danger')
            return redirect(url_for('admin.manage_quizzes'))  # Redirect back
    
    # For GET requests, redirect to the page with the modal
    return redirect(url_for('admin.manage_quizzes'))

@admin_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]  # Populate chapter dropdown

    if form.validate_on_submit():
        form.populate_obj(quiz)
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.manage_quizzes'))

    return render_template('admin/edit_quiz.html', form=form, quiz=quiz)

@admin_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)  # Get the quiz
    db.session.delete(quiz)  # Delete the quiz
    db.session.commit()  # Save changes to the database
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.manage_quizzes'))

@admin_bp.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def manage_questions(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    form = QuestionForm()  
    return render_template('admin/questions.html', quiz=quiz, questions=questions, form=form)
# Route to add a new question to a quiz
@admin_bp.route('/add_question/<int:quiz_id>', methods=['POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    form = QuestionForm()
    if form.validate_on_submit():
        try:
            # Create a new question
            new_question = Question(
                quiz_id=quiz_id,
                question_text=form.question_text.data,
                option1=form.option1.data,
                option2=form.option2.data,
                option3=form.option3.data,
                option4=form.option4.data,
                correct_option=int(form.correct_option.data)
            )
            db.session.add(new_question)
            db.session.commit()
            flash('Question added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        # Flash form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))
# Route to edit an existing question
@admin_bp.route('/edit_question/<int:quiz_id>', methods=['POST'])
@login_required
def edit_question(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    form = QuestionForm()
    if form.validate_on_submit():
        question_id = request.form.get('question_id')
        question = Question.query.get_or_404(question_id)
        
        # Update the question
        question.question_statement = form.question_text.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = int(form.correct_option.data)
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
    else:
        flash('Invalid form submission.', 'danger')
    
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

# Route to delete a question
@admin_bp.route('/delete_question/<int:quiz_id>', methods=['POST'])
@login_required
def delete_question(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('user.dashboard'))

    question_id = request.form.get('question_id')
    question = Question.query.get_or_404(question_id)
    
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))


# User dashboard route: Displays the user dashboard
@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get search parameters
    subject_search = request.args.get('subject_search', '').strip()
    quiz_search = request.args.get('quiz_search', '').strip()

    # Base queries
    quiz_query = Quiz.query.join(Chapter).join(Subject)
    subject_query = Subject.query

    # Apply filters if search terms exist
    if subject_search:
        subject_query = subject_query.filter(
            Subject.name.ilike(f'%{subject_search}%')
        )
        quiz_query = quiz_query.filter(
            Subject.name.ilike(f'%{subject_search}%')
        )

    if quiz_search:
        quiz_query = quiz_query.filter(
            Quiz.title.ilike(f'%{quiz_search}%')
        )

    # Get filtered results
    subjects = subject_query.all()
    quizzes = quiz_query.all()

    # Get user scores and stats
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempts = len(user_scores)
    average_score = sum(s.score / s.total_questions * 100 for s in user_scores) / total_attempts if total_attempts else 0

    return render_template('user/dashboard.html',
                         quizzes=quizzes,
                         subjects=subjects,
                         scores=user_scores,
                         total_attempts=total_attempts,
                         average_score=average_score)
# Quiz attempt route: Allows users to attempt a quiz
@user_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])  # Changed from '/quiz/<int:quiz_id>/attempt'
@login_required
def attempt_quiz(quiz_id):
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
        
        new_score = Score(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            total_questions=len(questions),
            percentage=(score/len(questions))*100 if questions else 0
        )
        db.session.add(new_score)
        db.session.commit()
        
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('user.quiz_results', quiz_id=quiz_id))
    
    return render_template('user/quiz.html', quiz=quiz, questions=questions)
@user_bp.route('/quiz/<int:quiz_id>/results')
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).order_by(Score.time_stamp_of_attempt.desc()).first()
    
    return render_template('user/quiz_results.html', 
                         quiz=quiz, 
                         score=score)

@admin_bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access restricted to administrators only.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Users per page

    
    users_query = User.query.filter_by(is_admin=False)
    
    # Apply search filter if query exists 
    if search_query:
        users_query = users_query.filter(
            User.full_name.ilike(f'%{search_query}%') |
            User.email.ilike(f'%{search_query}%') |
            User.username.ilike(f'%{search_query}%')
        )
    
    # Paginate the results
    users = users_query.order_by(User.id.asc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/users.html', 
                         users=users,
                         search_query=search_query)
@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access restricted to administrators only.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.is_admin:
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Delete all related scores first
        Score.query.filter_by(user_id=user_id).delete()
        
        # Now delete the user
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))    