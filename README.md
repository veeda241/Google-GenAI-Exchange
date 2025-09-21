# AI Career Advisor

A personalized AI-powered career advisor that maps your skills, recommends career paths, and prepares you for the job market by identifying skill gaps and suggesting learning resources. This application now includes user accounts to save and review past analyses.

## Features

- **Skill Extraction**: Identifies skills from user-provided text or an uploaded resume (PDF, DOCX, TXT).
- **Career Recommendation**: Matches user skills against a database of careers to suggest suitable paths.
- **Skill Gap Analysis**: Shows the user which skills they are missing for their top recommended career path.
- **Personalized Learning Plan**: Recommends online courses and YouTube project ideas to bridge skill gaps.
- **User Accounts & History**: Sign up, log in, and view a history of your past analysis results.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy, SQLite
- **Authentication**: Flask-Login, Flask-Bcrypt
- **AI/ML**: Custom recommendation logic (Jaccard Similarity)
- **Frontend**: HTML, CSS
- **Data**: JSON
- **APIs**: YouTube Data API v3

## Project Structure

```
/ai-career-advisor
|-- app.py              # Main Flask web application
|-- requirements.txt    # Python dependencies
|-- README.md           # This file
|-- core/               # Core application logic
|-- data/               # JSON data files
|-- templates/          # HTML templates
`-- static/             # CSS and other static assets
```

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone <https://github.com/veeda241/Google-GenAI-Exchange/edit/main>
    cd Google-GenAI-Exchange
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run the Flask application:**
    ```bash
    python app.py
    ```

4.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Future Improvements

- **Resume Parsing**: Integrate a library like `PyMuPDF` to directly upload and parse PDF resumes.
- **Advanced Skill Extraction**: Use a more advanced NLP model (e.g., spaCy's EntityRuler) for more accurate skill extraction.
- **Dynamic Data**: Scrape job boards like LinkedIn or Indeed to keep the career data up-to-date with market trends.
- **User Accounts**: Add user authentication to save career goals and track skill development over time.
- **Expand Database**: Add more careers, skills, and courses to the JSON data files.
