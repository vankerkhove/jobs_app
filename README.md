# Jobs App project

Markdown examples (for my own understanding):

## Examples (sub-header)

1. Text attributes (Outline)
   * _italic_
   * **bold**
   * `monospace`

## Setup (using PowerShell in Windows)

Workspace: /_workspace directory
Git repo

Layout
TBD

Initiate Git repo (done once):
project jobs_app
/_workspace/git> init jobs_app

Create virtual environment (done once):
> cd jobs_app
/_workspace/jobs_app> python -m venv .venv
Once created, then activate (each time):
> .venv\Scripts\activate

Install Flask (done once)
> pip install Flask

Run Flask app:
flask --app <app_name> run
If app name (the folder) is 'app' then  (the case for this project):
> flask run

From browser: http://127.0.0.1:5000

NOTE:
- When installing docx module, needed to install python-docx due to 
ModuleNotFoundError: No module named 'exceptions' message
So:
    pip install docx
and then:
    pip install python-docx
