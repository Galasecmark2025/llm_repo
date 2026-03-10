# create_exchange_folder.py

from pathlib import Path
import frappe

def create_exchange_folder(exchange=None, logger=None):
    """Create output directory for the exchange."""
    if not logger:
        return None
    
    if not exchange:
        logger.warning(f'⚠️ Exchange name not provided')
        return None
    try:
        exchange_parent_path = Path(frappe.get_site_path("private", "files", "exchange_circulars"))
        exchnage_path = exchange_parent_path / exchange.upper()
        exchnage_path.mkdir(parents=True, exist_ok=True)
        return exchnage_path
    except Exception as err:
        err_msg = f'❌ Error occurred while creating exchange folder'
        logger.error(f'{err_msg}: {err}')
        frappe.log_error(title=err_msg, message=frappe.get_traceback())
        return None