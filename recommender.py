from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_careers(user_skills, careers_data):
    """
    Recommends careers based on skill similarity using TF-IDF and Cosine Similarity.
    """
    if not user_skills:
        return []

    # Create a corpus of documents: one for the user's skills, and one for each career's required skills.
    user_skills_str = ' '.join(user_skills)
    career_skills_list = [' '.join(career['required_skills']) for career in careers_data]

    corpus = [user_skills_str] + career_skills_list

    # Vectorize the corpus using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity between the user's skills vector and all career vectors
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Create a list of (career, score) tuples
    recommendations = []
    for i, career in enumerate(careers_data):
        recommendations.append({
            'career': career,
            'score': cosine_similarities[i]
        })

    # Sort recommendations by score in descending order
    recommendations.sort(key=lambda x: x['score'], reverse=True)

    return recommendations

def analyze_skill_gap(user_skills, required_skills):
    """
    Identifies skills the user is missing for a specific career.
    """
    user_skills_set = set(s.lower() for s in user_skills)
    required_skills_set = set(s.lower() for s in required_skills)
    
    skill_gap = list(required_skills_set - user_skills_set)
    return skill_gap

def recommend_courses(skill_gap, courses_data):
    """Recommends courses for the skills in the skill gap."""
    return [course for course in courses_data if course['skill'] in skill_gap]