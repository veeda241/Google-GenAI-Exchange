import re

# This mapping helps find skills that have common alternative names or acronyms
# not already covered by being separate entries in skills.json.
# The key is the canonical skill name from skills.json.
# The value is a list of additional regex-safe strings to match.
SKILL_VARIATIONS = {
    "Node.js": ["NodeJS"],
    # Example for future use:
    # "UI/UX Design": ["UI/UX"],
}

def extract_skills(text, skills_list):
    """
    Extracts known skills from a given text using regular expressions.
    This version is case-insensitive, handles word boundaries, and can be
    extended with variations (e.g., "Node.js" vs "NodeJS").
    """
    found_skills = set()

    for skill in skills_list:
        # The primary pattern is the skill name itself, escaped for regex safety.
        patterns_to_check = [re.escape(skill)]

        # Check if there are known variations for this skill.
        if skill in SKILL_VARIATIONS:
            patterns_to_check.extend(SKILL_VARIATIONS[skill])

        # Build a single regex pattern for the skill and its variations, using word boundaries.
        combined_pattern = r'\b(' + '|'.join(patterns_to_check) + r')\b'

        # Search for the pattern in the text, ignoring case.
        if re.search(combined_pattern, text, re.IGNORECASE):
            found_skills.add(skill)
    return sorted(list(found_skills))