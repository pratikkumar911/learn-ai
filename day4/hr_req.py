import os
import json

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document


# ==========================================
# 1. Load API key
# ==========================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=api_key)


# ==========================================
# 2. Pydantic schemas
# ==========================================

class ResumeData(BaseModel):
    skills: list[str]
    experience: list[str]
    projects: list[str]


class MatchResult(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]

    matched_experience: list[str]
    missing_experience: list[str]

    matched_projects: list[str]
    missing_projects: list[str]

    match_percentage: float


# ==========================================
# 3. Extract text from PDF
# ==========================================

def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# 4. Extract text from Word
# ==========================================

def extract_docx_text(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# ==========================================
# 5. Extract resume text
# ==========================================

def extract_resume_text(file_path):

    if file_path.endswith(".pdf"):
        return extract_pdf_text(file_path)

    elif file_path.endswith(".docx"):
        return extract_docx_text(file_path)

    else:
        raise ValueError("Only PDF and DOCX files are supported")


# ==========================================
# 6. Extract structured information from resume
# ==========================================

def extract_resume_data(resume_text):

    schema = ResumeData.model_json_schema()

    system_prompt = f"""
You are an HR resume parser.

Extract information from the resume.

Return ONLY valid JSON.

The output must follow this schema:

{json.dumps(schema, indent=2)}

Extract:

1. skills
2. experience
3. projects

Do not invent information.
Only extract information actually present in the resume.
"""

    response = client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": resume_text
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    answer = response.choices[0].message.content

    data = json.loads(answer)

    return ResumeData(**data)


# ==========================================
# 7. Match resume against HR requirements
# ==========================================

def match_resume(resume_data, hr_requirements):

    schema = MatchResult.model_json_schema()

    system_prompt = f"""
You are an HR resume matching system.

Compare the candidate's resume information against the HR requirements.

Return ONLY valid JSON.

Output schema:

{json.dumps(schema, indent=2)}

Rules:

1. Match based on semantic meaning, not just exact words.
2. "React" and "React.js" should be considered the same skill.
3. "Node" and "Node.js" should be considered the same.
4. Do not consider unrelated skills as matches.
5. Clearly identify matched and missing requirements.
6. Calculate match_percentage.

Calculate the percentage as:

(number of matched requirements / total HR requirements) * 100

Do not invent experience or projects.
"""

    user_prompt = f"""
CANDIDATE RESUME:

Skills:
{resume_data.skills}

Experience:
{resume_data.experience}

Projects:
{resume_data.projects}


HR REQUIREMENTS:

{json.dumps(hr_requirements, indent=2)}
"""

    response = client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    answer = response.choices[0].message.content

    data = json.loads(answer)

    return MatchResult(**data)


# ==========================================
# 8. Main program
# ==========================================

resume_file = "resume.pdf"


# HR's requirements
hr_requirements = {
    "skills": [
        "C++",
        "JavaScript",
        "React.js",
        "Node.js",
        "SQL",
        "AWS",
        "Docker"
    ],

    "experience": [
        "3+ years software development experience",
        "Backend development experience",
        "REST API development",
        "Microservices experience"
    ],

    "projects": [
        "Full stack web application",
        "Cloud based project"
    ]
}


# Extract resume
resume_text = extract_resume_text(resume_file)

print("\n========== RESUME TEXT ==========\n")
print(resume_text[:3000])


# Extract structured data
resume_data = extract_resume_data(resume_text)

print("\n========== EXTRACTED RESUME ==========\n")

print("Skills:")
for skill in resume_data.skills:
    print("-", skill)

print("\nExperience:")
for exp in resume_data.experience:
    print("-", exp)

print("\nProjects:")
for project in resume_data.projects:
    print("-", project)


# Match with HR requirements
result = match_resume(
    resume_data,
    hr_requirements
)


# ==========================================
# 9. Print result
# ==========================================

print("\n===================================")
print("         RESUME MATCH RESULT")
print("===================================\n")

print(f"Match Percentage: {result.match_percentage}%")

print("\nMatched Skills:")
for item in result.matched_skills:
    print("✓", item)

print("\nMissing Skills:")
for item in result.missing_skills:
    print("✗", item)

print("\nMatched Experience:")
for item in result.matched_experience:
    print("✓", item)

print("\nMissing Experience:")
for item in result.missing_experience:
    print("✗", item)

print("\nMatched Projects:")
for item in result.matched_projects:
    print("✓", item)

print("\nMissing Projects:")
for item in result.missing_projects:
    print("✗", item)