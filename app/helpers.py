# Helper routines
"""
Helper Functions:
    file_time: extract date from string
    
"""

from datetime import date
import re
import csv
import json


#def get_date(line: str, index=0: int) -> str:
def get_date(line: str, index=0, year=None, cutoff=0) -> str:
    """
    Find date (format: M/D, M/D/Y) within a string, return formatted date string mm/dd/yy

    Args:
        line (str): String to search for date(s)
        index (int): The ith (index) date in 
        year (int): provide active year (default None: will use current year)
        cutoff (int): month on and after will use prior year (default: 0 no cut off)
    """
    # is m/d/y?
    year = str(year) if year else str(date.today().year)[2:]
    prior_year = str(int(year) - 1)
    cutoff = cutoff if cutoff else 100
    dates = re.findall(r"(\d{1,2}/\d{1,2}/\d{2,4})", line)

    if not dates:
        # is m/d?
        dates = re.findall(r"(\d{1,2}/\d{1,2})", line)

    if dates and len(dates) + index > 0:
        _date = dates[index].split("/")

        # add leading zero to month and day if needed 
        _date[0] = _date[0].zfill(2)
        _date[1] = _date[1].zfill(2)

        # date is month/day, append year (prior year if cutoff month)
        if len(_date) < 3:
            _date.append(year if int(_date[0]) < cutoff else prior_year)
        _date = "/".join(_date)
        return _date

    else:
        return "unknown"

def iso_date(line: str, index=0, year=None, cutoff=0) -> str:
    """
    Find date (format: M/D, M/D/Y) within a string, return formatted date string mm/dd/yy

    Args:
        line (str): String to search for date(s)
        index (int): The ith (index) date in 
        year (int): provide active year (default None: will use current year)
        cutoff (int): month on and after will use prior year (default: 0 no cut off)
    """

def write_to_csv(data, filename, mode="w"):
    """
    Writes a dictionary or a list of dictionaries to a CSV file.

    Args:
        data (dict or list of dict): The dictionary or list of dictionaries to write.
        filename (str): The name of the CSV file to create.
        mode (str): file access mode (currently only "w")
    """
    if not data:
        return
    data_type = "list"
    if isinstance(data, dict):
        data = [data]
    if isinstance(data[0], dict):
        data_type = "dict"
        
    if data_type == "list":
        with open(filename, mode, newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data)
    else:
        fields = list(data[0].keys())
        with open(filename, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)


def write_to_json(data, filename, mode="w"):
    """
    Writes a dictionary or a list of dictionaries to a JSON file.

    Args:
        data (dict/list dict): Dictionary or list of dictionaries to write.
        filename (str): The name of the CSV file to create.
        mode (str): file access mode (currently only "w")
    """
    with open(filename, mode) as json_file:
        json.dump(data, json_file, indent=4)

def read_json(filename, mode="r"):
    """
    read a JSON file.

    Args:
        filename (str): The name of the CSV file to create.
        mode (str): file access mode (currently only "r")
    Return:
        json results
    """
    try:
        with open(filename, mode) as file:
            data = json.load(file)
        print(filename)

    except FileNotFoundError:
        print (f"Error: JSON file ({filename}) not found.")
        raise FileNotFoundError 
    except Exception as e:
        print(f"An unexpected error occurred (file: {filename}): {e}")
        raise Exception 
    
    return data

def iso_date(date):
    """Convert data string format m/d/y or m/d to YYYY-MM-DD

    Args:
        date (str): string date mm/dd/yy or mm/dd/yyyy
    Return:
        date (str): yyyy-mm-dd else original 'date'
    """
    if type(date) != str:
        return date
    date_split = date.split("/")
    if len(date_split) == 2:
        # is of form m/d, append year
        date_split.append(str(date.today().year))
    elif len(date_split) != 3:
        # if not m/d/y return original 'date'
        return date
    date_split[0] = date_split[0].zfill(2)
    date_split[1] = date_split[1].zfill(2)
    if len(date_split[2]) == 2:
        # year is YY:
        date_split[2] = "20" + date_split[2]
    return f"{date_split[2]}-{date_split[0]}-{date_split[1]}"
    
