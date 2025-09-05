from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from app.jobs_db import get_db
from app.helpers import read_json
from app.parse_job_list import write_jobs_list

bp = Blueprint('jobs', __name__)

DEFAULT_JSON_FILE =    "c:/_workspace/jobs_app/data/jobs_outline.json"
DEFAULT_DETAILS_FILE = "c:/_workspace/jobs_app/data/outline/Jobs_Applied_outline.docx"
TEST_DETAILS_TARGET =  "c:/_workspace/jobs_app/data/jobs_outline"

def table_columns(table='jobs'):
    column_info = get_db().execute(f"PRAGMA table_info({table});").fetchall()
    column_names = [info[1] for info in column_info]
    return column_names

def db_execute(command, parameters=None, commit=False):
    try:
        db = get_db()
        if parameters:
           db.execute(command, parameters)
        else:
           db.execute(command)
        if commit:
            db.commit()
        return True, db

    except db.IntegrityError:
        error = f"Job (company, position, applied) exists in database."
        return False, error
    except Exception as e:
        print(f"Exception - DB command({command}) parameters({parameters}) {e}")
        raise Exception 

def get_details_file(source=DEFAULT_DETAILS_FILE ,target=TEST_DETAILS_TARGET):
    try:
        write_jobs_list(source, target)
        return 1

    except FileNotFoundError:
        return -1 
    except Exception as e:
        raise Exception 

def insert_jobs_from_json(jobs_db, source_json=DEFAULT_JSON_FILE):
    try:
        jobs = read_json(source_json)

    except FileNotFoundError:
        return -1 
    except Exception as e:
        raise Exception 

    for record in jobs:
        job = format_job_dict(record)
        try:
            jobs_db.execute(sql_insert_dict(job), job)
        except jobs_db.Error as e:
            print(f"Exception - Error: {e}")
    jobs_db.commit()
    return 1

def format_job_dict(job):
    """Set all null fields to either "" or False, 
       set arrays to strings with new line separators
    """
    for key in job.keys():
        value = job[key]
        if key in ["source", "applied", "decline"]:
            job[key] = "" if value == None else value
        if key in ["remote", "cover"]:
            job[key] = False if value == None else value
        if key in ["interview", "notes"]:
            if value == None:
                job[key] = ""
            elif type(value) == list:
                job[key] = "\n".join(value)
    return job

def sql_insert_dict(data, table='jobs'):
    columns = ', '.join(data.keys())
    placeholders = ':' + ', :'.join(data.keys())
    command = (f"INSERT OR IGNORE INTO {table} ({columns}) " +
               f"VALUES ({placeholders})")
    return command


def get_job(job_id):
    job = get_db().execute(
        'SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if job is None:
        abort(404, f"Post id {id} doesn't exist.")
    return job

def get_jobs(columns='*', condition=None):
    where_condition = ""
    if condition:
        where_condition = f"WHERE {condition}"
    try:
        jobs = get_db().execute(
            f'SELECT {columns} FROM jobs {where_condition}').fetchall()
        return jobs
    except Exception as e:
        print(f"Exception - Get Job error: {e}")

def interview_jobs():
    # SELECT * FROM jobs WHERE interview IS NOT NULL AND interview != '';
    where =  "interview IS NOT NULL AND interview != ''"
    return get_jobs(condition=where)

def id_list():
    jobs_ids = get_jobs(columns='id')
    try:
        _jobs = [x[0] for x in jobs_ids]
        _jobs.sort()
        return _jobs
    except Exception as e:
        print(f"Exception - Get Job error: {e}")

def next_job(id):
    _id_list = id_list()
    index = _id_list.index(id)
    next = index + 1 if index < len(_id_list) - 1 else 0
    return _id_list[next]

def previous_job(id):
    _id_list = id_list()
    index = _id_list.index(id)
    previous = index - 1 if index > 0 else len(_id_list) - 1
    return _id_list[previous]
        

def key_condition(company, position, applied, interview=None):
    """format keys fields: company, position, appplied into db search condition
    """
    conditions = []
    if company:
        conditions.append(f"company LIKE '%{company}%'")
    if position:
        conditions.append(f"position LIKE '%{position}%'")
    if applied:
        conditions.append(f"applied LIKE '%{applied}%'")
    if interview:
        conditions.append(f"interview LIKE '%{interview}%'")
    if conditions:
        all = " AND ".join(conditions)
        conditions = f"{all} COLLATE NOCASE"
    else:
        conditions = None
    return conditions


@bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    message = None

    row = None
    update = None
    if request.method == 'POST':
        forms = request.form.keys()

        if "update_jobs_json" in forms:

            result = get_details_file()
            if result == 1:
                flash("Updated jobs JSON file...")
            elif result == -1:
                flash("Jobs details file not found...")

        if "update_jobs_db" in forms:
            result = insert_jobs_from_json(db)
            if result == 1:
                flash("Updated jobs details list...")
            elif result == -1:
                flash("Jobs JSON file not found...")

        if "update_desc_db" in forms:
            flash("Update Desciption - Not Implemenet")

    jobs = db.execute("SELECT id, company, position, applied " + 
                      "FROM jobs ORDER BY id ASC").fetchall()

    return render_template(
       'index.html',
       jobs=jobs,
       number=str(len(jobs)),
       message=message)


@bp.route('/listing', methods=['GET', 'POST'])
def listing():
    job = None
    columns = table_columns()

    if request.method == 'POST':
        forms = request.form.keys()
        print(forms)

    flash("under construction...")
    return render_template('listing.html', column_list=columns)



@bp.route('/<int:id>/details', methods=['GET', 'POST'])
def details(id):
    job = get_job(id)
    job = [html_multiline(str(i)) for i in job]
        
    if request.method == 'POST':
        forms = request.form.keys()
        if 'select_edit' in forms:
            return redirect( url_for('jobs.edits', id=int(id) ))
        if 'select_delete' in forms:
            return redirect( url_for('jobs.deletes', id=int(id) ))
        if 'select_previous' in forms:
            return redirect( url_for('jobs.details', id=previous_job(id)) )
        if 'select_next' in forms:
            return redirect( url_for('jobs.details', id=next_job(id)) )

    return render_template('details.html', job=job)


def get_jobs_edits(html_data):
    edit_data = [
        html_data['company'],
        html_data['position'],
        html_data['applied'],
        html_data['source'],
        1 if "remote" in html_data.keys() else 0,
        1 if "cover" in html_data.keys() else 0,
        html_data['interview'].replace('\r\n', '\n'),
        html_data['decline'],
        html_data['notes'].replace('\r\n', '\n'),
    ]
    return edit_data

def html_multiline(text):
    new_text = text.replace('\r\n', '<br>')
    new_text = text.replace('\n', '<br>')
    return new_text

def db_multiline(text):
    new_text = text.replace('<br>', '\n\r')
    return new_text

def update_job(id, new, original):
    columns = table_columns()[1:]

    # get all changed columns
    updates = {columns[i]: new[i] 
               for i in range(len(new)) if new[i] != original[i]}

    # format set columns, e.g.: "company = ?, position = ?,..."
    set_columns = ", ".join([f"{key}=?" for key in updates.keys()])

    command = f"UPDATE jobs SET {set_columns} WHERE id = {id}"
    print(f"DEBUG Updates to id {id}: {updates}")
    return db_execute(command, parameters=list(updates.values()), commit=True)

@bp.route('/<int:id>/edits', methods=['GET', 'POST'])
def edits(id):
    
    job = get_job(id)
    if request.method == 'POST':
        forms = request.form.keys()
        if 'select_update' in forms:
            edit_data = get_jobs_edits(request.form)
            current_data = list(get_job(id))[1:]
            if edit_data != current_data:
                result, msg = update_job(id, edit_data, current_data)
                if result:
                    flash("Job updated...")
                    return redirect( url_for('jobs.details', id=id))
                else:
                    flash(msg)
                    job = [id] + edit_data
            else:
                flash("No changes to job...")
        elif 'select_cancel' in forms:
            return redirect( url_for('jobs.details', id=id))
        elif 'select_reset' in forms:
            flash("Reset to original...")

    return render_template('edits.html', job=job, edit=True)


def insert_job(data, table='jobs'):
    columns = ', '.join(table_columns()[1:])
    placeholders = ':' + ', :'.join(table_columns()[1:])
    command = (f"INSERT INTO {table} ({columns}) " +
               f"VALUES ({placeholders})")
    print(f"DEBUG Insert: {data[0]}, {data[1]}")
    return db_execute(command, parameters=data, commit=True)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    job = ['new', '', '', '', '', 0, 0, '', '', ''] 
    confirm = False
    if request.method == 'POST':
        forms = request.form.keys()
        add_data = get_jobs_edits(request.form)
        if 'select_add' in forms:
            add_data = get_jobs_edits(request.form)
            result, msg = insert_job(add_data)
            if result:
                flash("Add job not implemented yet...")
                return redirect( url_for('index'))
            else:
                flash(msg)
                job = ['new'] + add_data
        elif 'select_cancel' in forms:
            job = ['new'] + add_data
            confirm = True
            flash("Press 'Confirm' to cancel add...")
        elif 'select_confirm' in forms:
            flash("Cancelled add...")
            return redirect( url_for('index'))

    return render_template('edits.html', job=job, add=True, confirm=confirm)


@bp.route('/<int:id>/deletes', methods=['GET', 'POST'])
def deletes(id):
    job = get_job(id)
    job = [html_multiline(str(i)) for i in job]

    if request.method == 'POST':
        forms = request.form.keys()
        if 'select_confirm_delete' in forms:
            flash(f"Deleted job id: {id}")
            delete_query = f"DELETE FROM jobs WHERE id = {id}"
            db_execute(delete_query, commit=True)
            return redirect( url_for('index'))
        elif 'select_cancel_delete' in forms:
            flash("Delete cancelled")
            return redirect( url_for('jobs.details', id=id))

    flash(f"Deleting job: {id}...")
    return render_template('details.html', job=job, delete=True)


@bp.route('/find', methods=['GET', 'POST'])
def find(id=None):
    jobs_list = None
    one_job = None
    interview_jobs = None

    if request.method == 'POST':
        company = request.form['company']
        position = request.form['position']
        applied = request.form['applied']
        interview = request.form['interview']
        
        forms = request.form.keys()
        if 'find_job' in forms:
            condition = key_condition(company, position, applied, interview)
            jobs = get_jobs(condition=condition)
            if type(jobs) == list and len(jobs) > 0:
                if len(jobs) > 1:
                    jobs_list = jobs
                else:
                    one_job = jobs[0]
                    one_job = [html_multiline(str(i)) for i in one_job]

        elif "get_interview_jobs" in request.form.keys():
            where =  "interview IS NOT NULL AND interview != ''"
            jobs_list = get_jobs(condition=where)
            interview_jobs = True

        elif "selected_job" in request.form.keys():
            one_job = get_job(request.form['selected_job'])
            one_job = [html_multiline(str(i)) for i in one_job]

        if "select_edit" in request.form.keys():
            return redirect(
                url_for('jobs.edits', id=request.form['job_id']))

        if "select_delete" in request.form.keys():
            return redirect(url_for('jobs.deletes', id=request.form['job_id']))
            
    return render_template(
        'find.html',
        one_job=one_job,
        jobs_list=jobs_list,
        interview_jobs=interview_jobs)


@bp.route('/description', methods=['GET', 'POST'])
def description():
    flash(f"Description operation not implemented...")
    return redirect(url_for('index'))
