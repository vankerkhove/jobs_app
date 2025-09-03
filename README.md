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

Initiate Git repo:
project jobs_app
/_workspace/git> init jobs_app

Create virtual environment:
> cd jobs_app
/_workspace/jobs_app> python -m venv .venv
Once created, then activate:
> .venv\Scripts\activate

Install Flask
> pip install Flask

Run Flask app:
flask --app <app_name> run
If app name is 'app' then:
flask run

From browser: http://127.0.0.1:5000