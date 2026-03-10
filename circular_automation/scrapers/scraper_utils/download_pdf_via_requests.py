# download_pdf_via_requests.py

import frappe, requests, time

def download_pdf_via_requests(pdf_url=None, circular_no=None, preferred_file_name=None, save_dir=None, headers=None, logger=None):
    if not logger:
        frappe.log_error(f'logger is missing for download_pdf_via_requests()', 'Missing logger error')
        return False
    if not pdf_url:
        logger.error(f'PDF url not provided in download_pdf_via_requests()')
        frappe.log_error('PDF url not provided in download_pdf_via_requests()', 'Missing parameters error')
        return False
    if not save_dir:
        logger.error(f'Output directory not provided in download_pdf_via_requests()')
        frappe.log_error('Output directory not provided in download_pdf_via_requests()', 'Missing parameters error')
        return False
    
    file_path = save_dir / f'{circular_no}.pdf'
    
    if preferred_file_name:
        file_path = save_dir / f'{preferred_file_name}.pdf'
    if not headers:
        headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/pdf"
            }
    for attempt in range(1, 4):
        try:
            response = requests.get(
                    pdf_url,
                    headers=headers,
                    stream=True,
                    timeout=(10, 120),
                    verify=True
                )
            if response.status_code != 200:
                logger and logger.error(f"Failed to download PDF | Status: {response.status_code} | URL: {pdf_url}")
                return None
            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type:
                logger and logger.error(f"Invalid content type ({content_type}) | URL: {pdf_url}")
                return None

            # ---- Write file ----
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger and logger.info(f"PDF downloaded successfully: {file_path}")
            return file_path
        except requests.exceptions.ReadTimeout as e:
            logger.warning(f"Read timeout (attempt {attempt}) | Retrying...")
        except Exception as e:
            logger.exception(f"Download failed (attempt {attempt}) | {e}")
    
    time.sleep(2)

    logger.error(f"PDF download failed after 3 attempts | URL: {pdf_url}")
    frappe.log_error(f"PDF download failed after 3 attempts | URL: {pdf_url}")
    return None