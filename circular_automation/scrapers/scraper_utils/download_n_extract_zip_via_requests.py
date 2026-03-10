# download_n_extract_zip_via_requests.py

import frappe, requests, zipfile

def download_n_extract_zip_via_requests(zip_url=None, circular_no=None, output_dir=None, headers=None, logger=None):
    if not logger:
        frappe.log_error(f'logger is missing for download_n_extract_zip_via_requests()', 'Missing logger error')
        return False
    if not zip_url:
        logger.error(f'ZIP url not provided in download_n_extract_zip_via_requests()')
        frappe.log_error('ZIP url not provided in download_n_extract_zip_via_requests()', 'Missing parameters error')
        return False
    if not output_dir:
        logger.error(f'Output directory not provided in download_n_extract_zip_via_requests()')
        frappe.log_error('Output directory not provided in download_n_extract_zip_via_requests()', 'Missing parameters error')
        return False
    
    save_dir = output_dir / str(circular_no)
    save_dir.mkdir(parents=True, exist_ok=True)
    zip_filename = f'{circular_no}.zip'
    zip_path = save_dir / zip_filename    

    try:
        if not zip_path.exists():
            response = requests.get(zip_url, headers=headers, stream=True, timeout=60, verify=True)
            if response.status_code != 200:
                logger.error(f"Failed to download ZIP | Status: {response.status_code} | URL: {zip_url}")
                return None
            
            content_type = response.headers.get("Content-Type", "").lower()
            if "zip" not in content_type and "octet-stream" not in content_type:
                logger.error(f"Invalid ZIP content type ({content_type}) | URL: {zip_url}")
                return None
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                logger.info(f"ZIP downloaded successfully: {zip_path}")
        else:
            logger.info(f"ZIP already exists, skipping download: {zip_path}")
        # ---- Extract ZIP ----
        extract_dir = save_dir
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        logger.info(f"ZIP extracted successfully | Files: {len(zipfile.ZipFile(zip_path).namelist())}")
        return extract_dir
    except zipfile.BadZipFile:
        logger.error(f"Corrupt ZIP file: {zip_path}")
        return None
    except Exception as err:
        logger.error(f"Exception while downloading/extracting ZIP | URL: {zip_url} | Error: {err}")
        return None