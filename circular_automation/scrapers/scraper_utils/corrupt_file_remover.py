# corrupt_file_remover.py

from pathlib import Path
import pandas as pd
import frappe, zipfile

def corrupt_file_remover(filepath=None):
    """
    Checks whether a file is corrupted (currently supports .xlsx ZIP-based files).
    If corrupted, deletes the file safely.

    Args:
        file_path (str | Path): Path to the file
        logger (logging.Logger, optional): Logger instance

    Returns:
        bool:
            True  -> file was corrupt and removed
            False -> file is valid or does not exist
    """
    try:
        if not filepath:
            return False
        
        filepath = Path(filepath)

        if not filepath.exists():
            return False
        
        if filepath.suffix.lower() != ".xlsx":
            return False
        
        if filepath.stat().st_size == 0:
            filepath.unlink(missing_ok=True)
            frappe.logger().warning(f"🗑 Removed empty Excel file: {filepath}")
            return True

        # Force engine to catch zip corruption
        pd.read_excel(filepath, engine="openpyxl")

        return False  # valid Excel
        
    except (zipfile.BadZipFile, ValueError, OSError, Exception) as err:
        try:
            filepath.unlink(missing_ok=True)
            frappe.logger().warning(f"🗑 Corrupt Excel removed: {filepath} | Reason: {err}")
        except Exception:
            pass
        return True