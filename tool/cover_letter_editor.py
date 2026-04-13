from docx import Document
import os

def edit_cover_letter(cv_text, job_title, company, job_description, github_projects, cover_letter_template, client, portfolio_link="", kaggle_link="", extra_context="", project_description=""):
    
    if cv_text:
        cv_section = f"Here is the candidate's existing CV:\n{cv_text}"
    else:

        cv_section = "No CV provided — generate from scratch."
    
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
    

    if cover_letter_template:
        

        template_section = f"Here is their existing cover letter to use as a base:\n{cover_letter_template}"
    else:

        template_section = "No existing cover letter — generate from scratch."

    prompt = f"""
    You are a professional cover letter writer.
    
    {cv_section}
    {projects_section}
    {portfolio_section}
    {kaggle_section}
    {extra_section}
    {description_section}
    {template_section}
    
    Here is the job they are applying for:
    Job title: {job_title}
    Company: {company}
    Job description: {job_description}
    
    Write or improve the cover letter for this specific role.
    - Keep it to 3 paragraphs
    - First paragraph: why this company and role specifically
    - Second paragraph: most relevant experience and projects
    - Third paragraph: closing and call to action
    - Sound human and enthusiastic, not generic
    - Do not invent experience that is not in the CV
    - Leave [YOUR NAME] as a placeholder at the end
    """
    
    #response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
    #return response.text
    response = client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content



def save_cover_letter(cover_letter_text, company, job_title, session_folder):
    doc = Document()
    doc.add_paragraph(cover_letter_text)
    filename = f"cover_letter_{company}_{job_title}.docx".replace(" ", "_").replace("/", "_")
    filepath = os.path.join(session_folder, "cover_letters", filename)
    doc.save(filepath)
    print(f"Cover letter saved as {filepath}")
    return filepath