# excel_save_n_check.py

from pathlib import Path
import pandas as pd
import frappe

def excel_save_n_check(based_on='circular_no', date=None, circular_no=None, subject=None, base_dir=None, exchange=None, operation='save', logger=None):
    if not logger:
        frappe.log_error('logger is mising in excel_save_n_check()', 'Missing logger issue')
        return False
    logger.info(f"➡️ Entered excel_save_n_check | operation={operation}")
    
    if not exchange:
        logger.error(f'Exchange name is missing in excel_save_n_check()')
        return False
    
    if not base_dir:
        logger.error('Base directory is missing')
        return False
    
    if not date:
        logger.error('Date is missing')
        date = 'None'
    
    if not operation:
        logger.warning(f'Operation method not provided... will continue with save operation')
        
    if based_on == 'circular_no' and not circular_no:
        logger.error('circular_no is missing')
        return False
    if based_on == 'subject' and not subject:
        logger.error('subject is missing')
        return False
    
    save_dir = Path(base_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / f"{exchange}_circulars.xlsx"
    # corrupt_file_remover(filepath=file_path, logger=logger)
    logger.info(f"📄 Excel path resolved: {file_path}")

    if operation == 'save':
        logger.info("🟦 SAVE operation triggered")
        try:
            if based_on == 'circular_no':
                record = {
                    'date': date,
                    'circular_no': circular_no
                }
                subset = ['circular_no', 'date']
            elif based_on == 'subject':
                record = {
                    'date': date,
                    'subject': subject
                }
                subset = ['subject', 'date']
            else:
                logger.warning(f'Undefined record type')
                return False
            df_new = pd.DataFrame([record])

            logger.info(f"🆕 New Record to insert:\n{df_new.to_dict(orient='records')}")

            if file_path.exists():
                logger.info("📘 Existing Excel found — reading file")
                df_existing = pd.read_excel(file_path)
                logger.info(f"📗 Existing rows count: {len(df_existing)}")
                df_result = pd.concat([df_existing, df_new], ignore_index=True)
                logger.info(f"📘 Total rows after append: {len(df_result)}")

            else:
                logger.info("📕 Excel does NOT exist — creating new file")
                df_result = df_new

            for col in subset:
                df_result[col] = (
                    df_result[col]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )
            df_result.drop_duplicates(subset=subset, keep='first', inplace=True)
            
            df_result.to_excel(file_path, index=False)
            logger.info(f"💾 Saved Excel successfully → {file_path}")
            return True
        except Exception as err:
            logger.warning(f'Error occurred for "{operation}" operation: {err}')
            return False
    elif operation == 'check':
        logger.info("🟨 CHECK operation triggered")
        if not file_path.exists():
            logger.info("📕 Excel file does not exist — record cannot exist")
            return False
        try:
            df_existing = pd.read_excel(file_path)
            logger.info(f"📗 Existing rows count: {len(df_existing)}")
            
            if based_on == 'circular_no':
                subset = ['circular_no', 'date']
                check_values = {
                    'circular_no': str(circular_no).strip().upper(),
                    'date': str(date).strip().upper()
                }
            elif based_on == 'subject':
                subset = ['subject', 'date']
                check_values = {
                    'subject': str(subject).strip().upper(),
                    'date': str(date).strip().upper()
                }
            else:
                logger.error("Invalid based_on value")
                return False
            
            # Normalize existing data
            for col in subset:
                if col in df_existing.columns:
                    df_existing[col] = (
                        df_existing[col]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )
            # Build condition
            if based_on == 'circular_no':
                check_df = df_existing[(df_existing['circular_no'] == check_values['circular_no']) & (df_existing['date'] == check_values['date'])]
            else:
                check_df = df_existing[(df_existing['subject'] == check_values['subject']) & (df_existing['date'] == check_values['date'])]
            
            if check_df.shape[0] > 0:
                logger.info('✅ Record already exists in Excel')
                return True
            else:
                logger.info('Record does not exist in Excel')
                return False
        except Exception as err:
            logger.warning(f'Error occurred for "{operation}" operation: {err}')
            return False