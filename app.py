from flask import Flask, render_template, request

from data_loader import load_json_data
from skill_mapper import extract_skills
from recommender import recommend_careers, analyze_skill_gap, recommend_courses

app = Flask(__name__)

# Load all data at startup
SKILLS_LIST = load_json_data('skills.json')
CAREERS_DATA = load_json_data('careers.json')
COURSES_DATA = load_json_data('courses.json')

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Processes user input and displays recommendations."""
    user_input = request.form.get('user_input', '')

    if not user_input or not SKILLS_LIST or not CAREERS_DATA or not COURSES_DATA:
        # Handle case where data failed to load or input is empty
        return render_template('index.html', error="Could not process request. Please try again.")

    # 1. Extract skills from user input
    user_skills = extract_skills(user_input, SKILLS_LIST)

    # 2. Get career recommendations
    career_recommendations = recommend_careers(user_skills, CAREERS_DATA)

    # 3. For the top recommendation, perform skill gap analysis
    skill_gap = []
    course_recommendations = []
    if career_recommendations:
        top_career = career_recommendations[0]['career']
        required_skills = top_career['required_skills']
        skill_gap = analyze_skill_gap(user_skills, required_skills)
        course_recommendations = recommend_courses(skill_gap, COURSES_DATA)

    analysis_results = {
        'user_skills': user_skills,
        'recommendations': career_recommendations,
        'skill_gap': skill_gap,
        'course_recommendations': course_recommendations
    }

    return render_template('results.html', analysis=analysis_results)

if __name__ == '__main__':
    app.run(debug=True)