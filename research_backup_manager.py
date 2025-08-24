#!/usr/bin/env python3
"""
Research Backup Management Module
Handles backup and restore operations for research data

This module provides functionality to:
- Create timestamped backups of log files
- Restore data from backup files
- Manage backup retention policies
- Verify backup integrity
- Handle various error conditions gracefully
- Provide performance optimizations and logging

Author: ASK Research Tool
Last Updated: 2025-08-24
"""

import os
import logging
import shutil
import hashlib
import glob
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from research_csv_manager import LOG_CSV_FILE

# Setup logging with enhanced configuration
log = logging.getLogger(__name__)

# Configuration constants
BACKUP_RETENTION_DAYS = 30
MAX_BACKUPS = 100
BACKUP_DIR = "backups"
BACKUP_PREFIX = "log.csv.backup_"

def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists and is accessible
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file exists and is accessible, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            log.warning(f"File does not exist: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            log.warning(f"Path is not a file: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            log.warning(f"File is not readable: {file_path}")
            return False
        
        return True
    except Exception as e:
        log.error(f"Error validating file {file_path}: {e}")
        return False

def calculate_file_hash(file_path: str) -> Optional[str]:
    """
    Calculate MD5 hash of a file for integrity verification
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string or None if error
    """
    try:
        if not validate_file_exists(file_path):
            return None
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    except Exception as e:
        log.error(f"Error calculating hash for {file_path}: {e}")
        return None

def create_backup_directory() -> bool:
    """
    Create backup directory if it doesn't exist
    
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            log.info(f"Created backup directory: {BACKUP_DIR}")
        return True
    except Exception as e:
        log.error(f"Error creating backup directory: {e}")
        return False

def backup_log_csv() -> Optional[str]:
    """
    Create a timestamped backup of log.csv with integrity verification
    
    Returns:
        Path to the created backup file or None if failed
    """
    try:
        # Validate source file
        if not validate_file_exists(LOG_CSV_FILE):
            log.warning(f"{LOG_CSV_FILE} does not exist, cannot create backup")
            return None
        
        # Create backup directory
        if not create_backup_directory():
            return None
        
        # Generate timestamp and backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(BACKUP_DIR, f'{BACKUP_PREFIX}{timestamp}')
        
        # Create backup
        shutil.copy2(LOG_CSV_FILE, backup_filename)
        
        # Verify backup integrity
        original_hash = calculate_file_hash(LOG_CSV_FILE)
        backup_hash = calculate_file_hash(backup_filename)
        
        if original_hash and backup_hash and original_hash == backup_hash:
            log.info(f"Created verified backup: {backup_filename}")
            
            # Clean up old backups
            cleanup_old_backups()
            
            return backup_filename
        else:
            log.error(f"Backup integrity check failed for {backup_filename}")
            # Remove failed backup
            try:
                os.remove(backup_filename)
            except:
                pass
            return None
        
    except Exception as e:
        log.error(f"Error creating backup: {e}")
        return None

def restore_log_csv_from_backup(backup_filename: str) -> bool:
    """
    Restore log.csv from a backup file with integrity verification
    
    Args:
        backup_filename: Path to the backup file
        
    Returns:
        True if restore was successful, False otherwise
    """
    try:
        # Validate backup file
        if not validate_file_exists(backup_filename):
            log.error(f"Backup file {backup_filename} does not exist")
            return False
        
        # Calculate backup file hash before restore
        backup_hash = calculate_file_hash(backup_filename)
        if not backup_hash:
            log.error(f"Cannot verify backup file integrity: {backup_filename}")
            return False
        
        # Create backup of current file if it exists
        if os.path.exists(LOG_CSV_FILE):
            current_backup = backup_log_csv()
            if not current_backup:
                log.warning("Could not create backup of current file before restore")
        
        # Perform restore
        shutil.copy2(backup_filename, LOG_CSV_FILE)
        
        # Verify restore integrity
        restored_hash = calculate_file_hash(LOG_CSV_FILE)
        if restored_hash and restored_hash == backup_hash:
            log.info(f"Successfully restored {LOG_CSV_FILE} from {backup_filename}")
            return True
        else:
            log.error(f"Restore integrity check failed for {LOG_CSV_FILE}")
            return False
        
    except Exception as e:
        log.error(f"Error restoring from backup: {e}")
        return False

def list_available_backups() -> List[Dict[str, Any]]:
    """
    List all available backup files with metadata
    
    Returns:
        List of backup information dictionaries
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            return []
        
        backups = []
        backup_pattern = os.path.join(BACKUP_DIR, f"{BACKUP_PREFIX}*")
        
        for backup_file in glob.glob(backup_pattern):
            try:
                stat = os.stat(backup_file)
                backup_info = {
                    'filename': backup_file,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'hash': calculate_file_hash(backup_file)
                }
                backups.append(backup_info)
            except Exception as e:
                log.warning(f"Error getting info for backup {backup_file}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        log.info(f"Found {len(backups)} backup files")
        return backups
        
    except Exception as e:
        log.error(f"Error listing backups: {e}")
        return []

def cleanup_old_backups() -> int:
    """
    Clean up old backup files based on retention policy
    
    Returns:
        Number of files removed
    """
    try:
        backups = list_available_backups()
        if not backups:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        removed_count = 0
        
        for backup_info in backups:
            # Remove backups older than retention period
            if backup_info['created'] < cutoff_date:
                try:
                    os.remove(backup_info['filename'])
                    log.info(f"Removed old backup: {backup_info['filename']}")
                    removed_count += 1
                except Exception as e:
                    log.error(f"Error removing old backup {backup_info['filename']}: {e}")
            
            # Limit total number of backups
            if len(backups) - removed_count > MAX_BACKUPS:
                try:
                    os.remove(backup_info['filename'])
                    log.info(f"Removed excess backup: {backup_info['filename']}")
                    removed_count += 1
                except Exception as e:
                    log.error(f"Error removing excess backup {backup_info['filename']}: {e}")
        
        if removed_count > 0:
            log.info(f"Cleaned up {removed_count} old backup files")
        
        return removed_count
        
    except Exception as e:
        log.error(f"Error cleaning up old backups: {e}")
        return 0

def get_backup_statistics() -> Dict[str, Any]:
    """
    Get statistics about backup files
    
    Returns:
        Dictionary with backup statistics
    """
    try:
        backups = list_available_backups()
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size': 0,
                'oldest_backup': None,
                'newest_backup': None,
                'average_size': 0
            }
        
        total_size = sum(backup['size'] for backup in backups)
        oldest_backup = min(backup['created'] for backup in backups)
        newest_backup = max(backup['created'] for backup in backups)
        average_size = total_size / len(backups) if backups else 0
        
        stats = {
            'total_backups': len(backups),
            'total_size': total_size,
            'oldest_backup': oldest_backup.isoformat(),
            'newest_backup': newest_backup.isoformat(),
            'average_size': average_size,
            'retention_days': BACKUP_RETENTION_DAYS,
            'max_backups': MAX_BACKUPS
        }
        
        log.info(f"Backup statistics: {stats['total_backups']} backups, {stats['total_size']} bytes")
        return stats
        
    except Exception as e:
        log.error(f"Error getting backup statistics: {e}")
        return {
            'total_backups': 0,
            'total_size': 0,
            'error': str(e)
        }

def verify_backup_integrity(backup_filename: str) -> bool:
    """
    Verify the integrity of a backup file
    
    Args:
        backup_filename: Path to the backup file
        
    Returns:
        True if backup is valid, False otherwise
    """
    try:
        if not validate_file_exists(backup_filename):
            return False
        
        # Check if file has valid content (not empty)
        if os.path.getsize(backup_filename) == 0:
            log.warning(f"Backup file is empty: {backup_filename}")
            return False
        
        # Calculate hash to ensure file is not corrupted
        file_hash = calculate_file_hash(backup_filename)
        if not file_hash:
            return False
        
        log.info(f"Backup integrity verified: {backup_filename}")
        return True
        
    except Exception as e:
        log.error(f"Error verifying backup integrity: {e}")
        return False

# Export main functions for easy access
__all__ = [
    'backup_log_csv',
    'restore_log_csv_from_backup',
    'list_available_backups',
    'cleanup_old_backups',
    'get_backup_statistics',
    'verify_backup_integrity',
    'validate_file_exists',
    'calculate_file_hash'
]
