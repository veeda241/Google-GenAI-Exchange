import math

def calculate_jaccard_similarity(set1, set2):
    """Calculates the Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union != 0 else 0.0

def recommend_careers(user_skills, careers_data):
    """
    Recommends careers based on skill similarity and returns all matches above a threshold.
    Recommends careers based on skill similarity and returns all available careers, ranked by score.
    """
    user_skills_set = set(skill.lower() for skill in user_skills)
    recommendations = []

    for career in careers_data:
        required_skills_set = set(skill.lower() for skill in career.get('required_skills', []))
        

        score = calculate_jaccard_similarity(user_skills_set, required_skills_set)
        
        # Filter to show any career with a match score greater than 0.1% (0.001)
        if score > 0.001:
            recommendations.append({
                'career': career,
                'match_score': score
            })

        recommendations.append({
            'career': career,
            'match_score': score
        })

    # Sort recommendations by match score in descending order
    return sorted(recommendations, key=lambda x: x['match_score'], reverse=True)

def analyze_skill_gap(user_skills, required_skills):
    """Identifies skills the user is missing for a specific career."""
    user_skills_set = set(skill.lower() for skill in user_skills)
    required_skills_set = set(skill.lower() for skill in required_skills)
    return list(required_skills_set - user_skills_set)

def recommend_courses(skill_gap, courses_data):
    """Recommends courses for the skills in the skill gap."""
    recommendations = []
    skill_gap_set = set(s.lower() for s in skill_gap)

    for course in courses_data:
        course_skills_set = set(s.lower() for s in course.get('relevant_skills', []))
        if not skill_gap_set.isdisjoint(course_skills_set):
            recommendations.append(course)
            
    return recommendations