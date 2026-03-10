# clean_string.py

from datetime import datetime
from pathlib import Path
import frappe, re

def clean_string(string=None, separator='_', max_len=None, logger=None):
    try:
        string = str(string).strip()
        string = re.sub(r'[^A-Za-z0-9]', '_', string)
        string = re.sub(r'_+', separator, string)
        string_cleaned = string.strip(separator)
        if max_len:
            string_cleaned = string_cleaned[:max_len] if len(string_cleaned) > max_len else string_cleaned
        return string_cleaned
    
    except Exception as err:
        err_msg = f'Error occurred while cleaning subject'
        logger.error(f'{err_msg}: {err}')
        frappe.log_error(title=err_msg, message=frappe.get_traceback())
        return None
    
def clean_string_other_than_english(string=None, logger=None):
    try:
        string = str(string).strip()
        string = re.sub(r"[^\x00-\x7F]+", "", string)
        string = re.sub(r"\s+", " ", string)
        string_cleaned = re.sub(r"^[^A-Za-z0-9]+", "", string)
        return string_cleaned
    
    except Exception as err:
        err_msg = f'Error occurred while cleaning subject'
        logger.error(f'{err_msg}: {err}')
        frappe.log_error(title=err_msg, message=frappe.get_traceback())
        return None

def clean_filename(filename=None, separator='_', max_len=50, logger=None):
    try:
        if not filename:
            return None
        basename = Path(filename).stem
        ext = Path(filename).suffix
        filename = str(basename).strip()
        filename = re.sub(r'[^A-Za-z0-9]', separator, filename)
        filename = re.sub(rf'{re.escape(separator)}+', separator, filename)
        filename_cleaned = filename.strip(separator)
        filename_cleaned = filename_cleaned[:max_len] if len(filename_cleaned) > max_len else filename_cleaned
        filename_cleaned = f'{filename_cleaned}{ext}'
        return filename_cleaned
    
    except Exception as err:
        err_msg = f'Error occurred while cleaning filename: {filename}'
        logger.error(f'{err_msg}: {err}')
        frappe.log_error(title=err_msg, message=frappe.get_traceback()) 
        return None

def convert_date(date_input=None, date_format="%d/%m/%Y", conversion_format='%Y-%m-%d', logger=None):
    try:
        date = datetime.strptime(date_input, date_format)
        return date.strftime(conversion_format)
    except Exception as err:
        logger.warning(f'Date conversion failed | value={date_input} | error={err}')
        return None  
