import sqlite3
import os
from docx2python import docx2python

from helpers import get_date, iso_date
from tools.db_tools import DB

description_file = './data/description/Jobs_Applied_description_test.docx'
description_file = './data/description/Jobs_Applied_description_4_8-8.docx'

def read_docx_file(docx_file):
    try:
        with docx2python(docx_file) as docx_content:
            text = docx_content.text
            lines = text.split("\n\n")
            return lines

    except Exception as e:
        print(f"An unexpected error occurred (file: {docx_file}): {e}")
        raise Exception 
    return None

def parse_file_content(lines):
    _start = "jobstart>>>"
    _description = "jobd>>>"
    _end = "jobend>>>"
    status = "done"
    
    this_job = []
    this_description = []
    all_jobs = []
    
    for line in lines:
        if line == _start:
            status = "details"
            this_job = []
            this_description = []
        elif line == _description:
            status = "description"
        elif line == _end:
            status = "done"
            all_jobs.append(_format_job(this_job, this_description))
        elif status == "details":
            this_job.append(line)
        elif status == "description":
            print(line)
            this_description.append(line)

    return all_jobs

def _format_job(job, description):
    """Add job to the jobs dictionary. 

    Args:
        job (list): company, position, and applied (date)
        description (text): each line of the description
    """
    if len(job) < 2:
        print(f"Error in job {job}")
        return None
    company = job[0].strip()
    position = job[1].replace("(remote)", "").strip() # remove '(remote) from position
    apply_date = iso_date(get_date(job[2], cutoff=12)) if len(job) > 2 else None
    description_text = "\n".join(description)
    return {
        "company": company,
        "position": position,
        "applied": apply_date,
        "description": description_text}

def sql_insert_dict(data, table='description'):
    columns = ', '.join(data.keys())
    placeholders = ':' + ', :'.join(data.keys())
    command = (f"INSERT OR IGNORE INTO {table} ({columns}) " +
               f"VALUES ({placeholders})")
    return command

def write_to_db(jobs_db, job):
    try:
        jobs_db.execute(sql_insert_dict(job), job)
    except sqlite3.Error as e:
        print(f"Exception - Error: {e}")


if __name__ == '__main__':
    print("from command line...")

    lines = read_docx_file(description_file)
    jobs = parse_file_content(lines)
    db_file = "./instance/jobs.sqlite"
    table = 'description'
    description_db = DB(db_file)
    for job in jobs:
        if job:
            write_to_db(description_db, job)
    description_db.commit()
    print("count: ", description_db.count(table))
    description_db.close()
