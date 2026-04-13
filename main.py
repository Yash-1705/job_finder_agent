from playwright.sync_api import sync_playwright
#from google import genai
from groq import Groq
from dotenv import load_dotenv
import os
import datetime
from tool.cv_reader import read_cv
from tool.github_reader import get_github_projects
from tool.cv_editor import tailor_cv, save_cv
from tool.cover_letter_editor import edit_cover_letter, save_cover_letter
from tool.cover_letter_reader import read_cover_letter
from langchain_core.tools import Tool
from agent.core import agent
from tool.jira import create_jira_plan
from tool.spreadsheet import update_tracker

load_dotenv()
#GEMINI_API_KEY = os.getenv("GEMINI_API")
#client = genai.Client(api_key=GEMINI_API_KEY)
GROQ_API_KEY = os.getenv("GEMINI_API")
client = Groq(api_key =GROQ_API_KEY)

from langchain_core.tools import tool

@tool
def search_jobs(query: str) -> str:
    """Search for jobs on Seek. Input should be role and location like 'software engineering intern sydney'"""
    return f"searching for {query}"
# --- Create session folder ---
def create_session_folder():
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")
    folder = f"job_search/session_{timestamp}"
    os.makedirs(f"{folder}/cvs", exist_ok=True)
    os.makedirs(f"{folder}/cover_letters", exist_ok=True)
    print(f"\nSession folder created: {folder}")
    return folder

# --- Strip quotes from dragged file paths ---
def clean_path(path):
    return path.strip().strip("'\"")

# --- Collect candidate info ---
cv_path = clean_path(input("Drag your CV here and press Enter (or press Enter to skip): "))
if cv_path:
    cv_text = read_cv(cv_path)
    print("CV loaded successfully")
else:
    cv_text = ""
    print("No CV provided - will generate one from scratch")

cover_letter_path = clean_path(input("Drag an existing cover letter here (or press Enter to skip): "))
if cover_letter_path:
    cover_letter_template = read_cover_letter(cover_letter_path)
    print("Cover letter template loaded")
else:
    cover_letter_template = ""
    print("No cover letter provided - will generate one from scratch")

print("\n--- Work samples and portfolio (press Enter to skip any) ---")

github_username = input("GitHub username: ")
if github_username:
    github_projects = get_github_projects(github_username)
    print(f"Found {len(github_projects)} GitHub projects")
else:
    github_projects = []

portfolio_link = input("Portfolio or other link (Behance, Dribbble, LinkedIn etc): ")
kaggle_link = input("Kaggle profile link: ")

extra_files_path = clean_path(input("Any project files, CAD drawings or reports as PDF/Word (drag here): "))
if extra_files_path:
    extra_context = read_cv(extra_files_path)
    print("Extra files loaded")
else:
    extra_context = ""

project_description = input("Describe any other projects or work not covered above: ")

# --- Create session folder ---
session_folder = create_session_folder()

with sync_playwright() as p:
    role = input("What role are you looking for? ")
    location = input("What city or state are you looking to work? ")

    split_role = role.split()
    edited_role = "-".join(split_role)

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.seek.com.au/" + edited_role + "-jobs/in-" + location)
    page.wait_for_timeout(5000)

    jobs = page.query_selector_all('[data-testid="job-card-title"]')
    employer = page.query_selector_all('[data-automation="jobCompany"]')

    results = []
    for job, company in zip(jobs, employer):
        results.append({
            "title": job.inner_text(),
            "company": company.inner_text(),
            "url": "https://www.seek.com.au" + job.get_attribute("href")
        })

    print(f"\nFound {len(results)} jobs — analysing all...\n")

    for result in results:
        print(f"Analysing: {result['title']} at {result['company']}")

        page.goto(result["url"])
        page.wait_for_timeout(3000)

        # --- Safe description scrape ---
        desc = page.query_selector('[data-automation="jobAdDetails"]')
        result["description"] = desc.inner_text() if desc else "No description found"

        # --- Gap analysis prompt ---
        prompt = f"""
        You are a job application assistant.

        Here is the candidate's CV:
        {cv_text}

        Additional work samples:
        GitHub: {github_projects}
        Portfolio: {portfolio_link}
        Kaggle: {kaggle_link}
        Extra context: {extra_context}
        Other projects: {project_description}

        Here is the job description for {result['title']} at {result['company']}:
        {result['description']}

        Please provide:
        1. Match percentage with reasoning
        2. Skills and experience the candidate HAS that match
        3. Skills and experience the candidate is MISSING
        4. 2 to 3 specific projects or work samples they should create to close the gaps
           (code projects for software, CAD models for mechanical, portfolio pieces for design etc)
        5. Specific things to study or practice based on the role
           (Leetcode for software, CAD tools for mechanical, tools/software for other fields)
        6. Match percentage after following the recommendations
        """

        #response = client.models.generate_content(model="gemini-2.0-flash-lite",contents=prompt)
        response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role": "user", "content": prompt}])
        #print(response.text)
        print(response.choices[0].message.content)

        # --- Tailor CV and save to session folder ---
        tailored = tailor_cv(
            cv_text, result["title"], result["company"],
            result["description"], github_projects, client,
            portfolio_link, kaggle_link, extra_context, project_description
        )
        save_cv(tailored, result["company"], result["title"], session_folder)

        # --- Write cover letter and save to session folder ---
        cover_letter = edit_cover_letter(
            cv_text, result["title"], result["company"],
            result["description"], github_projects,
            cover_letter_template, client,
            portfolio_link, kaggle_link, extra_context, project_description
        )
        save_cover_letter(cover_letter, result["company"], result["title"], session_folder)

        print(f"Done: {result['title']} at {result['company']}")
        print("--------------------------------\n")
        epic_key = create_jira_plan(result["company"], result["title"])
        print(f"Jira tasks created for {result['company']}")

        update_tracker(
        result["company"],
        result["title"],
        "",
        "",
        "To Apply",
        f"{session_folder}/cvs/cv_{result['company']}_{result['title']}.docx".replace(" ", "_").replace("/", "_"),
        f"{session_folder}/cover_letters/cover_letter_{result['company']}_{result['title']}.docx".replace(" ", "_").replace("/", "_"),
        epic_key,
        datetime.date.today()
        )
        print("Tracker updated")

    browser.close()
    print(f"\nAll done! Files saved to: {session_folder}")

    executor = agent([search_jobs])
    result = executor.invoke({"messages": [{"role": "user", "content": f"find {role} internships in {location}"}]})
    print(result["messages"][-1].content)