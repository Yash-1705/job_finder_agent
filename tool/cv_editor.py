from docx import Document
import os

def tailor_cv(cv_text, job_title, company, job_description, github_projects, client, portfolio_link="", kaggle_link="", extra_context="", project_description=""):
    
    if cv_text:
        cv_section = f"Here is the candidate's existing CV:\n{cv_text}"
    else:

        cv_section = "The candidate has no existing CV. Generate one from scratch."
    
    if github_projects:
        projects_section = f"Here are their GitHub projects:\n{github_projects}"
    else:
        projects_section = "No GitHub projects provided."
    
    if portfolio_link:
        portfolio_section = f"Portfolio/other link: {portfolio_link}"
    else:

        portfolio_section = ""
    

    if kaggle_link:
        kaggle_section = f"Kaggle profile: {kaggle_link}"
    else:
        kaggle_section = ""
    
    if extra_context:
        extra_section = f"Additional project files/work:\n{extra_context}"
    else:
        extra_section = ""
    
    if project_description:
        
        description_section = f"Other projects described by candidate:\n{project_description}"
    else:
        description_section = ""

    prompt = f"""
    You are a CV writing expert.
    
    {cv_section}
    {projects_section}
    {portfolio_section}
    {kaggle_section}
    {extra_section}
    {description_section}
    
    Here is the job they are applying for:
    Job title: {job_title}
    Company: {company}
    Job description: {job_description}
    
    Rewrite or generate the CV tailored for this specific role.
    Keep all facts truthful — do not invent experience.
    Emphasise relevant skills and reorder bullet points to match the job requirements.
    Output the full CV text ready to save.
    Based on the files provided update the necessary projects or skills.
    """
    
    #response = client.models.generate_content(model="gemini-2.0-flash-lite",contents=prompt)
    #return response.text
    response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content


def save_cv(cv_text, company, job_title, session_folder):
    doc = Document()
    doc.add_paragraph(cv_text)
    filename = f"cv_{company}_{job_title}.docx".replace(" ", "_").replace("/", "_")
    filepath = os.path.join(session_folder, "cvs", filename)
    doc.save(filepath)
    print(f"CV saved as {filepath}")
    return filepath