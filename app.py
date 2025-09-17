from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime
import os

from data_loader import load_json_data
from skill_mapper import extract_skills
from recommender import recommend_careers, analyze_skill_gap, recommend_courses
from youtube_service import get_video_details, extract_video_id_from_url, search_videos

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print(f"Info: Loading environment variables from {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path)
else:
    # This is not a critical error, as the key might be set in the system's environment
    print("Info: .env file not found. Assuming environment variables are set globally.")

app = Flask(__name__)

# --- New Configurations for Database and Session Management ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_dev_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to /login if user is not authenticated
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = 'info'

# --- User Model for Database ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# --- New Analysis Model for Database ---
class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_input = db.Column(db.Text, nullable=False)
    analysis_results = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    author = db.relationship('User', backref=db.backref('analyses', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Load all data at startup
SKILLS_LIST = load_json_data('skills.json')
CAREERS_DATA = load_json_data('careers.json')
COURSES_DATA = load_json_data('courses.json')

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html', title="Home")

# --- New Authentication Routes ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title="Sign Up")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check username and password.', 'error')
    return render_template('login.html', title="Login")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """Displays the user's profile page with past analyses."""
    # Query analyses for the current user, ordered by most recent first
    past_analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.timestamp.desc()).all()
    return render_template('profile.html', analyses=past_analyses, title="My Profile")

@app.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """Displays the results of a specific past analysis."""
    analysis = Analysis.query.get_or_404(analysis_id)

    # Security check: Ensure the current user owns this analysis
    if analysis.author != current_user:
        flash("You are not authorized to view this analysis.", "error")
        return redirect(url_for('profile'))

    return render_template('results.html', analysis=analysis.analysis_results, title="Past Analysis Results", from_history=True)

@app.route('/analyze', methods=['POST'])
@login_required # This route is now protected
def analyze():
    """Processes user input and displays recommendations."""
    user_input = request.form.get('user_input', '')

    if not user_input or not SKILLS_LIST or not CAREERS_DATA or not COURSES_DATA:
        # Handle case where data failed to load or input is empty
        flash("Could not process request due to missing data or input.", "error")
        return redirect(url_for('index'))

    # 1. Extract skills from user input
    user_skills = extract_skills(user_input, SKILLS_LIST)

    # 2. Get career recommendations
    career_recommendations = recommend_careers(user_skills, CAREERS_DATA)

    # 3. For EACH recommendation, perform skill gap analysis and get project details
    for rec in career_recommendations:
        career = rec['career']
        required_skills = career['required_skills']
        
        # Analyze skill gap and add to the recommendation object
        skill_gap = analyze_skill_gap(user_skills, required_skills)
        rec['skill_gap'] = skill_gap
        
        # Recommend courses and add to the recommendation object
        course_recs = recommend_courses(skill_gap, COURSES_DATA)
        rec['course_recommendations'] = course_recs
        
        # Fetch YouTube video details for project ideas
        project_ideas = career.get('project_ideas', [])

        video_ids = []
        if project_ideas:
            for p in project_ideas:
                video_id = extract_video_id_from_url(p.get('youtube_url', ''))
                if video_id:
                    video_ids.append(video_id)
        if video_ids:
            rec['career']['project_ideas_detailed'] = get_video_details(video_ids)

    analysis_results = {
        'user_skills': user_skills,
        'recommendations': career_recommendations
    }

    # --- New: Save the analysis to the database ---
    new_analysis = Analysis(
        user_input=user_input,
        analysis_results=analysis_results,
        author=current_user
    )
    db.session.add(new_analysis)
    db.session.commit()

    return render_template('results.html', analysis=analysis_results, title="Analysis Results")

@app.route('/search_videos', methods=['POST'])
def search_youtube_videos():
    """Searches for YouTube videos based on a query from the client."""
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    videos = search_videos(query)
    return jsonify(videos)

if __name__ == '__main__':
    with app.app_context():
        # This will create the database file and tables if they don't exist
        db.create_all()
    app.run(debug=True)