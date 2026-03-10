# InsertRecord.py

from frappe.utils.file_manager import save_file
from frappe.model.rename_doc import rename_doc
from pathlib import Path
import frappe

class InsertRecord:
    def __init__(self):
        if not frappe.db.exists("DocType", "Circular Record"):
            err_msg = "'Circular Record' DocType does not exist"
            frappe.log_error(title="DocType Issue", message=err_msg)
            
    def insert_new_record(
            self, 
            subject=None, 
            circular_url=None, 
            date=None, 
            circular_no=None, 
            regulator=None, 
            department=None, 
            segment_name=None, 
            category_name=None, 
            communication_number=None, 
            parent_path=None, 
            logger=None
        ):

        logger = logger or frappe.logger("frappe_insertion_log")

        try:
            if not circular_no:
                logger.warning(f'⚠️ Missing required field: Circular No... Will continue with series ')
            files = []
            if parent_path is None:
                logger.warning(f'Circular folder path not provided... will fail to attach any circular/attachments')
                return None
            
            parent_path = Path(parent_path)
            if not parent_path.exists():
                logger.warning(f"❌ Path does not exist → {parent_path}")
                return None
            
            if not parent_path.is_dir():
                logger.warning(f"❌ Path is not a folder → {parent_path}")
                return None
            
            # if parent_path.exists() and parent_path.is_dir():
            files = [f for f in parent_path.iterdir()
                        if f.is_file() and not f.name.endswith(('summary.txt','task_list.txt','circular_no.txt'))
                    ]
            
            if len(files) == 0:
                logger.error("❌ No files found to attach")
                frappe.log_error(title='Missing file(s) error', message=f'No Circular/Attachments found for circular: {circular_no}')
                return None
            
            if circular_no:
                is_exists = frappe.db.exists("Circular Record", {"circular_no": circular_no})
                if is_exists:
                    logger.info(f"ℹ️ Circular already exists → {circular_no}, skipping...")
                    return True
  
            # else:
            circular_rec = frappe.new_doc("Circular Record")
            
            if circular_no: circular_rec.circular_no = circular_no
            if subject: circular_rec.subject = subject
            if circular_url: circular_rec.circular_url = circular_url
            if date: circular_rec.date = date
            if regulator: circular_rec.regulator = str(regulator).upper()
            if department: circular_rec.department = department
            if segment_name: circular_rec.segment_name = segment_name
            if category_name: circular_rec.category_name = category_name
            if communication_number: circular_rec.communication_number = communication_number
            if parent_path: circular_rec.parent_path = str(parent_path)
            
            circular_rec.insert(ignore_permissions=True)
            logger.info(f"✅ Inserted Circular → {circular_no}")

            try:
                for file in files:
                    with open(file, "rb") as f:
                        path = Path(file.name)
                        filename = (path.stem[:50] if len(path.stem) > 50 else path.stem) + path.suffix
                        save_file(filename, f.read(), "Circular Record", circular_rec.name, is_private=1)
                    logger.info(f"📎 Attached PDF → {file.name}")
                
            except Exception as err:
                err_msg = f"❌ Failed to attach PDF"
                logger.error(f"{err_msg}: {err}", exc_info=True)
                frappe.log_error(title=err_msg, message=frappe.get_traceback())
                return None
            
            circular_rec.save(ignore_permissions=True)
            frappe.db.commit()
            try:
                circular_no_txt_file = parent_path / "circular_no.txt"
                with open(circular_no_txt_file, "w", encoding='utf-8') as f:
                    f.write(' ' if not circular_no else circular_no)
                logger.info(f"📝 Created circular_no.txt → {circular_no_txt_file}")
            except Exception as err:
                err_msg = f"❌ Failed to create circular_no.txt"
                logger.error(f"{err_msg}: {err}", exc_info=True)
                frappe.log_error(title=err_msg, message=frappe.get_traceback())
                return None
            
            if circular_no: 
                rename_doc("Circular Record", circular_rec.name, circular_no, ignore_permissions=True)
                logger.info(f'Doc renamed successfully.')
                frappe.db.commit()
                return True
            else:
                fetched_circular_no = circular_rec.name
                logger.info(f'\nCirculr record name: {fetched_circular_no}')
                try:
                    circular_no_txt_file = parent_path / "circular_no.txt"
                    with open(circular_no_txt_file, "w", encoding='utf-8') as f:
                        f.write(' ' if not fetched_circular_no else fetched_circular_no)
                    logger.info(f"📝 Created circular_no.txt → {circular_no_txt_file}")
                    return True
                except Exception as err:
                    err_msg = f"❌ Failed to create circular_no.txt"
                    logger.error(f"{err_msg}: {err}", exc_info=True)
                    frappe.log_error(title=err_msg, message=frappe.get_traceback())
                    return None
            
        except Exception as err:
            err_msg = f"❌ Error inserting circular: {circular_no}"
            logger.error(f"{err_msg}: {err}", exc_info=True)
            frappe.log_error(title=err_msg, message=frappe.get_traceback())
            frappe.db.rollback()
            return None
