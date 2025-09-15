def extract_skills(text, skills_list):
    """
    Extracts known skills from a given text.
    A simple implementation that checks for skill mentions.
    """
    found_skills = set()
    text_lower = text.lower()
    for skill in skills_list:
        # Use word boundaries to avoid matching substrings (e.g., 'go' in 'google')
        # A simple way is to check for the skill with spaces or at the end of the text
        if f' {skill.lower()} ' in f' {text_lower} ':
            found_skills.add(skill)
    return list(found_skills)