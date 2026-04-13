import csv
import os

def update_tracker(company, role, match, recommended_projects, status, cv, cover_letter, jira, date):
    file_exists = os.path.exists("master_tracker.csv")
    
    with open("master_tracker.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Company", "Role", "Match %", "Recommended Projects", "Status", "CV File", "Cover Letter", "Jira Epic", "Date"])
        writer.writerow([company, role, match, recommended_projects, status, cv, cover_letter, jira, date])