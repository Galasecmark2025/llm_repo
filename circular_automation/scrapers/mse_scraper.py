# mse_scraper.py

from playwright.sync_api import sync_playwright
import frappe, time
from urllib.parse import urljoin

from circular_automation.circular_automation.scrapers.scraper_utils.download_n_extract_zip_via_requests import download_n_extract_zip_via_requests
from circular_automation.circular_automation.scrapers.scraper_utils.download_pdf_via_requests import download_pdf_via_requests
from circular_automation.circular_automation.scrapers.scraper_utils.clean_string import convert_date, clean_string
from circular_automation.circular_automation.scrapers.scraper_utils.excel_save_n_check import excel_save_n_check
from circular_automation.circular_automation.scrapers.scraper_utils.InsertRecord import InsertRecord

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.msei.in/downloads/Circulars/Default",
        "Connection": "keep-alive"
    }   

def mse_scraper(exchange=None, url=None, from_date=None, to_date=None, output_dir=None, logger=None):
    if not logger:
        frappe.log_error('logger is mising in mse_scraper()', 'Missing logger issue')
        return False
    if not exchange:
        logger.error(f'Exchange name is missing in mse_scraper()')
    exchange = str(exchange).upper()
    
    logger.info(f'Recieved parameters: Exchange: {exchange}, From: {from_date}, To: {to_date}, Ouptut Dir: {output_dir}')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        context = browser.new_context()
        page = context.new_page()

        # ---- Navigate to site ----
        MSE_URL = url
        try:
            page.goto(MSE_URL, timeout=60000, wait_until="load")
            
            page.locator('//div[@class="m-filter-c clearfix"]//button[text()="Advance Search "]').click()
            page.wait_for_load_state('networkidle')
            page.wait_for_load_state('load')
            time.sleep(2)
            
            page.evaluate(
                """
                ({ selector, value }) => {
                    const el = document.querySelector(selector);
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
                """,
                {
                    "selector": "#ExchangeCirculars_circularswithadvancesearch_dtFrom",
                    "value": f"{from_date.replace('/', '-')}"
                }
            )
            page.evaluate(
                """
                ({ selector, value }) => {
                    const el = document.querySelector(selector);
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
                """,
                {
                    "selector": "#ExchangeCirculars_circularswithadvancesearch_dtTo",
                    "value": f"{to_date.replace('/', '-')}"
                }
            )

            page.locator('//input[@type="submit" and @value="Search"]').click()
            page.wait_for_load_state('load')
            page.wait_for_load_state('networkidle')
            
            circular_table_el = page.locator('//table[@class="table table-striped t-listview"]')
            if circular_table_el.count() == 0:
                logger.info(f"No circular found for date range: {from_date} - {to_date}")
                return True
            logger.info('Circular table found')
            # "//span[text()='Currently no data available.']"
            page.wait_for_selector('//table[@class="table table-striped t-listview"]//tr//th', timeout=30000)
            headings = []
            table_heads = page.locator('//table[@class="table table-striped t-listview"]//tr//th')
            for th in table_heads.all():
                headings.append(th.inner_text().strip())
            headings.append('CIRCULAR LINK')
            logger.info(f'Fetched headings: {headings}')
            
            cir_rows = page.locator('//table[@class="table table-striped t-listview"]//tr[@class]')
            rows_count = cir_rows.count()
            logger.info(f'Circulars count: {rows_count}')
            for i in range(rows_count):
                row = cir_rows.nth(i)
                tds = row.locator("td")
                date_raw = tds.nth(0).inner_text().strip()
                date = convert_date(date_input=date_raw, date_format="%d-%b-%Y", logger=logger)
                circular_no  = tds.nth(1).inner_text().strip()
                segment  = tds.nth(2).inner_text().strip()
                department  = tds.nth(3).inner_text().strip()
                
                anchor = tds.nth(4).locator('a')
                subject = anchor.inner_text().strip()
                presence_status = excel_save_n_check(date=date, circular_no=circular_no, exchange=exchange, base_dir=output_dir, operation='check', logger=logger)
                if presence_status:
                    logger.info(f'Circular already present. Skipping...')
                    continue
                circular_link = anchor.get_attribute('href')
                if circular_link:
                    circular_link = urljoin(MSE_URL, circular_link)
                logger.info(circular_link)
                circular_no_cleaned = clean_string(string=circular_no, logger=logger)
                save_dir = output_dir / str(circular_no_cleaned)
                save_dir.mkdir(parents=True, exist_ok=True)
                download_status = False
                if circular_link.endswith('.pdf'):
                    # continue
                    pdf_download_status = download_pdf_via_requests(pdf_url=circular_link, circular_no=circular_no, save_dir=save_dir, headers=HEADERS, logger=logger)
                    if pdf_download_status:
                        logger.info(f'PDF downloaded for: {circular_no}')
                        download_status = True
                    else:
                        logger.warning(f'Failed to download PDF for: {circular_no}')
                elif circular_link.endswith('.zip'):
                    zip_download_status = download_n_extract_zip_via_requests(zip_url=circular_link, circular_no=circular_no, output_dir=output_dir, headers=HEADERS, logger=logger)
                    if zip_download_status:
                        logger.info(f'ZIP downloaded for: {circular_no}')
                        download_status = True
                    else:
                        logger.warning(f'Failed to download ZIP for: {circular_no}')
                
                if download_status:
                    inserter = InsertRecord()
                    insert_record_status = inserter.insert_new_record(
                        subject=subject, 
                        circular_url=circular_link, 
                        date=date,
                        circular_no=f'{exchange}/{circular_no}', 
                        regulator=exchange, 
                        department=department, 
                        segment_name=segment, 
                        parent_path=save_dir, 
                        logger=logger)
                    if insert_record_status:
                        logger.info(f'Circular record inserted: {circular_no}')
                        save_history_status = excel_save_n_check(date=date, circular_no=circular_no, exchange=exchange, base_dir=output_dir, logger=logger)
                        if save_history_status:
                            logger.info(f'Successfully saved record for: {date}: {circular_no}')
                        else:
                            logger.warning(f'Failed to save record for: {date}: {circular_no}')
                    else:
                        logger.warning(f'Unable to insert circular for: {circular_no}')       
            return True
        
        except Exception as err:
            err_msg = f'Error occurred while scraping {exchange}'
            logger.error(f'{err_msg}: {err}')
            return False