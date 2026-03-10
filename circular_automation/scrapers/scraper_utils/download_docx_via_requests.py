# download_docx_via_requests.py

from urllib.parse import urlparse
from pathlib import Path
import requests, frappe

def download_docx_via_requests(doc_url=None, circular_no=None, preferred_file_name=None, save_dir=None, logger=None):
    if not logger:
        frappe.log_error('logger is missing for download_docx_via_requests()', 'Missing logger error')
        return False

    if not doc_url:
        logger.error('DOCX url not provided in download_docx_via_requests()')
        return False

    if not save_dir:
        logger.error('Output directory not provided in download_docx_via_requests()')
        return False

    # ---- Determine extension ----
    url_path = urlparse(doc_url).path
    ext = Path(url_path).suffix.lower() or ".docx"

    if ext not in (".docx", ".doc"):
        logger.error(f"Unsupported document extension ({ext}) | URL: {doc_url}")
        return False

    # ---- File path ----
    filename = preferred_file_name or circular_no
    file_path = save_dir / f"{filename}{ext}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword"
    }

    try:
        response = requests.get(
            doc_url,
            headers=headers,
            stream=True,
            timeout=60,
            verify=True
        )

        if response.status_code != 200:
            logger.error(f"Failed to download document | Status: {response.status_code} | URL: {doc_url}")
            return False

        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()

        if content_type not in {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        }:
            logger.error(f"Invalid DOCX content type ({content_type}) | URL: {doc_url}")
            return False

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"DOCX downloaded successfully: {file_path}")
        return file_path

    except Exception as e:
        logger.exception(f"Exception while downloading DOCX | URL: {doc_url} | Error: {e}")
        return False