from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
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
        if project_ideas:
            video_ids = [extract_video_id_from_url(p['youtube_url']) for p in project_ideas if extract_video_id_from_url(p['youtube_url'])]
            if video_ids:
                # Add detailed project info to the recommendation's career object
                rec['career']['project_ideas_detailed'] = get_video_details(video_ids)

    analysis_results = {
        'user_skills': user_skills,
        'recommendations': career_recommendations
    }

    return render_template('results.html', analysis=analysis_results)

@app.route('/search_videos', methods=['POST'])
def search_youtube_videos():
    """Searches for YouTube videos based on a query from the client."""
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    videos = search_videos(query)
    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)