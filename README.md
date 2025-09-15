# AI Career Advisor

A personalized AI career advisor that maps skills, recommends career paths, and prepares users for the evolving job market by identifying skill gaps and suggesting learning resources.

## Features

- **Skill Extraction**: Identifies technical and soft skills from user-provided text (like a resume summary).
- **Career Recommendation**: Uses a TF-IDF and Cosine Similarity model to match user skills against a database of careers.
- **Skill Gap Analysis**: Shows the user which skills they are missing for their top recommended career path.
- **Personalized Learning Plan**: Recommends online courses to help bridge the identified skill gaps.

## Tech Stack

- **Backend**: Python, Flask
- **AI/ML**: Scikit-learn
- **Frontend**: HTML, CSS
- **Data**: JSON

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
    git clone <repository-url>
    cd ai-career-advisor
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