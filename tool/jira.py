from jira import JIRA
from dotenv import load_dotenv
import os

load_dotenv()

def get_jira_client():
    return JIRA(server=os.getenv("JIRA_URL"),basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API")))

def create_epic(jira, company, job_title):
    eppic =jira.create_issue( fields={"project": {"key": os.getenv("JIRA_PROJECT")},"summary": f"{company} — { job_title}","issuetype": {"name": "Epic"}})
    return eppic
def create_task(jira, summary, epic_key):
    task =jira.create_issue(fields={"project":{"key": os.getenv("JIRA_PROJECT")},"summary": summary,"issuetype": {"name": "Task"}, "parent": {"key": epic_key}})
    return task
def create_jira_plan(company, job_title):
    jira = get_jira_client()
    epic = create_epic(jira, company, job_title)
    tasks = [
    "Research company culture and news",
    "Tailor CV",

    "Write and review cover letter",
    "Interview prep",
    "Apply by deadline",
    "Follow up if no response"
]

    for task_summary in tasks:
        create_task(jira, task_summary, epic.key)
    return epic.key