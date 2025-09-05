"""
Parse Job List

The format outline of each job in the jobs list document is:
    N. comany_name
    \tN.1 position_name (optional: 'remote'/'local')
    \t\tN.1.m Source: text_source_name (optional)
    \t\tN.1.m Remote (flag optional: is a remote job)
    \t\tN.1.m Cover Letter (flag optional: application included cover letter)
    \t\tN.1.m Local (flag optional: is a local job)
    \t\tN.1.m Applied date_applied (optional)
    \t\tN.1.m Interview
    \t\t\tN.1.m.n text_additional_interview (optional: multiple lines)
    \t\t\tN.1.m.n text_additional_interview (optional: multiple lines)
    \t\tN.1.m Decline date_decline_notice (optional)
    \t\tN.1.m Notes text_notes (optional)
    \t\t\tN.1.m.n text_additional_notes (optional: multiple lines)
    \t\t\tN.1.m.n text_additional_notes (optional: multiple lines)
    \t\tN.1.m text_other (optional: appended to notes)

Will parse the job list document (docx) file. The format of this fils is:
    1. comany_name
    \t1.1 position (require)
    \t1.1.1 details (require) 
    \t\t\t1.1.1.1 sub-details

Details
Should include the application date: \t1.1.1 Applied: m/d
Can include if recieved declined/rejected: pythont1.1.1 Decline: m/d  
Can include interview information: \t1.1.1 Interview
    with optional sub-interview details: 
        \t1.1.1.1 an interview detail (who, date, email...)
        
This file is read in and then converted to json and csv files
"""

from docx2python import docx2python
from app.helpers import get_date, iso_date
from app.helpers import write_to_csv
from app.helpers import write_to_json

DEFAULT_FILE = "data/outline/Jobs_Applied_outline.docx"
DEFAULT_OUTPUT = "data/jobs_outline"


def get_file_lines(doc_file=DEFAULT_FILE):
    """Reads the outlined jobs document file (docx)
    Will convert 
    (If From):
      N
      \tN.N
      \t\tN.N.N
      \t\t\tN.N.N.N
    ...
    To:
      N)
      \tN)
      \t\tN)
      \t\t\tN)
    ...
    """
    try:
        with docx2python(doc_file) as docx_content:
            text = docx_content.text
            lines = text.split("\n\n")
            return lines

    except FileNotFoundError:
        print (f"Error: JSON file ({doc_file}) not found.")
        raise FileNotFoundError
    except Exception as e:
        print(f"An unexpected error occurred (file: {doc_file}): {e}")
        raise Exception 
    return None


class parse_line():
    def __init__(self, line):
        self.leading_tabs = count_leading_tabs(line)
        _line = line[self.leading_tabs:].split("\t") # split between tab (number and text)
        self.outline_number = 0
        self.text = ""
        if len(_line) > 1:
            self.outline_number = int(_line[0].replace(")", ""))
            self.text = _line[1]


def count_leading_tabs(text):
    count = 0
    for char in text:
        if char == '\t':
            count += 1
        else:
            break
    return count


def reset_job(company):
    job = {
        "company": "",
        "position": "",
        "source": "",
        "remote": None,
        "applied": None,
        "cover": None,
        "interview": [], # array
        "decline": None,
        "notes": [], # array
        }
    job["company"] = company.strip()
    return job

def get_detail_text(detail='', line=''):
    # get the text for the job detail: 
    text = line[len(detail):] # remove detail label
    text = text[1:] if text.find(':') == 0 else text # remove if ':'
    return text.strip()

def get_job_details(job, text):
    text = text.strip()
    detail_is = "notes"
    
    # if "Source: " in text:
    if text.lower().find('source') == 0:
        # detail_is = "source"
        # job["source"] = text.replace("Source: ", "")
        job["source"] = get_detail_text(detail='source', line=text)

    #elif "applied" in text.lower():
    elif text.lower().find('applied') == 0:
        # detail_is = "applied"
        job["applied"] = iso_date(get_date(text, cutoff=12))

        if "remote" in text.lower():
            job["remote"] = True
        if "cover" in text.lower():
            job["cover"] = True

    #elif "cover letter" in text.lower():
    elif text.lower().find('cover') == 0:
            job["cover"] = True

    #elif "interview" in text.lower():
    elif text.lower().find('interview') == 0:
        detail_is = "interview"
        # job['interview'].append(iso_date(get_date(text, cutoff=12)))
        interview_text = get_detail_text(detail='interview', line=text)
        if interview_text:
            job["interview"].append(interview_text)

    #elif "decline" in text.lower():
    elif text.lower().find('decline') == 0:
        job["decline"] = iso_date(get_date(text, cutoff=12))

    #elif "remote" == text[:6].lower():
    elif text.lower().find('remote') == 0:
        job["remote"] = True

    #elif "local" == text[:5].lower():
    elif text.lower().find('local') == 0:
        job["remote"] = False

    elif text.lower().find('notes') == 0:
        txt = get_detail_text(detail='notes', line=text)
        if txt:
            job["notes"].append(txt)
    elif text.lower().find('note') == 0:
        txt = get_detail_text(detail='note', line=text)
        if txt:
            job["notes"].append(txt)
    else:
        job['notes'].append(text)
    
    return job, detail_is


def get_job_list(file=DEFAULT_FILE):
    lines = get_file_lines(file)
    job = {}
    jobs = []
    detail = 'notes'
    
    for _line in lines:
        line = parse_line(_line)
        leading_tabs = line.leading_tabs
        outline_number = line.outline_number
        text = line.text
        
        if not line.outline_number or not line.text:
            continue

        if leading_tabs == 0:  # is company
            if job:  # if a current job collected, save previous
                if job["company"] and job["position"]:
                    jobs.append(job)
                else:
                    print(f"Error fields: {job["company"]}, {job["position"]}")
            job = reset_job(text)

        elif leading_tabs == 1:  # is position
            if outline_number == 1: # only one item (position) at this level
                job["position"] = text.replace("(remote)", "").strip()
                # if position states remote:
                if "remote" in text.lower():
                    job["remote"] = True
            else:
                print(f"Error in table: ({outline_number}) {text}")

        elif leading_tabs == 2:  # is detail
            job, detail = get_job_details(job, text)

        elif line.leading_tabs == 3:  # is sub-detail
            # append the text to the previous detail level
            job[detail].append(text)

        elif line.leading_tabs > 3:  # is sub-detail
            # append the text to the previous detail level
            job[detail].append(f"{outline_number}. {text}")

    if job and job["company"] and job["position"]:
        # Append last job if any
        jobs.append(job)

    return jobs


def write_jobs_list(source=DEFAULT_FILE, target=DEFAULT_OUTPUT):
    jobs = get_job_list(file=source)
    if target:
        write_to_csv(jobs, target + ".csv")
        write_to_json(jobs, target + ".json")
    print(f"JOb written: {len(jobs)}")
    return jobs
    

if __name__ == '__main__':
    print("from command line...")
    jobs = write_jobs_list()

    for job in jobs:
        print(job)

