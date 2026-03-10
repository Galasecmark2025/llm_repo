# goto_with_retry.py

import frappe, time

def goto_with_retry(page, url, retries: int = 5, timeout: int = 60000, logger=None):
    """Navigate to URL with retries and ensure full JS initialization (esp. for MCX)."""
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to navigate to {url} (attempt {attempt+1}/{retries})...")
            page.goto(url, timeout=timeout, wait_until="networkidle")

            logger.info(f"Successfully navigated to {url}")
            return True

        except Exception as err:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {err}")
            time.sleep(5)

    err_msg = f"Failed to load {url} after {retries} attempts."
    logger.error(f"{err_msg}")
    frappe.log_error(title=err_msg, message=frappe.get_traceback())
    return False
