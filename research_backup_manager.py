#!/usr/bin/env python3
"""
Research Backup Management Module
Handles backup and restore operations for research data
"""

import os
import logging
import shutil
from datetime import datetime
from research_csv_manager import LOG_CSV_FILE

# Setup logging
log = logging.getLogger(__name__)

def backup_log_csv():
    """Create a backup of log.csv"""
    try:
        if os.path.exists(LOG_CSV_FILE):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'{LOG_CSV_FILE}.backup_{timestamp}'
            
            shutil.copy2(LOG_CSV_FILE, backup_filename)
            log.info(f"Created backup: {backup_filename}")
            return backup_filename
        else:
            log.warning(f"{LOG_CSV_FILE} does not exist, cannot create backup")
            return None
    except Exception as e:
        log.error(f"Error creating backup: {e}")
        return None

def restore_log_csv_from_backup(backup_filename):
    """Restore log.csv from a backup file"""
    try:
        if os.path.exists(backup_filename):
            shutil.copy2(backup_filename, LOG_CSV_FILE)
            log.info(f"Restored {LOG_CSV_FILE} from {backup_filename}")
            return True
        else:
            log.error(f"Backup file {backup_filename} does not exist")
            return False
    except Exception as e:
        log.error(f"Error restoring from backup: {e}")
        return False
