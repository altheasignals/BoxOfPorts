"""SQLite storage layer for local state management."""

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .api_models import SMSTaskReport, SMSTask


class EjoinStore:
    """SQLite-based storage for EJOIN CLI state management."""
    
    def __init__(self, db_path: Path):
        """
        Initialize the storage with the given database file.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._local = threading.local()
        self._initialize_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                isolation_level=None,  # Auto-commit mode
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager for database transactions."""
        conn = self._get_connection()
        conn.execute("BEGIN")
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    
    def _initialize_db(self) -> None:
        """Initialize database schema."""
        with self._transaction() as conn:
            # SMS tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sms_tasks (
                    tid INTEGER PRIMARY KEY,
                    ports TEXT NOT NULL,
                    to_number TEXT NOT NULL,
                    text_hash TEXT NOT NULL,
                    template_text TEXT,
                    template_vars TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Task reports table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tid INTEGER NOT NULL,
                    sending INTEGER DEFAULT 0,
                    sent INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    unsent INTEGER DEFAULT 0,
                    sdr_details TEXT,
                    fdr_details TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tid) REFERENCES sms_tasks (tid)
                )
            """)
            
            # Inbox messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS inbox_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ssrc TEXT NOT NULL,
                    sms_id INTEGER NOT NULL,
                    delivery_report INTEGER NOT NULL,
                    port TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_base64 TEXT,
                    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ssrc, sms_id)
                )
            """)
            
            # Device status table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_ip TEXT NOT NULL,
                    device_mac TEXT NOT NULL,
                    max_ports INTEGER NOT NULL,
                    max_slots INTEGER NOT NULL,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Port status table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS port_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_ip TEXT NOT NULL,
                    port TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    status_text TEXT NOT NULL,
                    balance TEXT,
                    operator TEXT,
                    sim_number TEXT,
                    imei TEXT,
                    imsi TEXT,
                    iccid TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(device_ip, port)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sms_tasks_submitted_at ON sms_tasks (submitted_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_reports_tid ON task_reports (tid)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_inbox_ssrc_sms_id ON inbox_messages (ssrc, sms_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_port_status_device_port ON port_status (device_ip, port)")
    
    # SMS Task Management
    def save_sms_task(self, tid: int, ports: List[str], to_number: str, 
                      text_hash: str, template_text: str = None, 
                      template_vars: Dict[str, Any] = None) -> None:
        """Save an SMS task to the database."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sms_tasks 
                (tid, ports, to_number, text_hash, template_text, template_vars)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tid,
                ','.join(ports),
                to_number,
                text_hash,
                template_text,
                json.dumps(template_vars) if template_vars else None
            ))
    
    def get_sms_task(self, tid: int) -> Optional[Dict[str, Any]]:
        """Get an SMS task by TID."""
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM sms_tasks WHERE tid = ?", (tid,)).fetchone()
        if row:
            return {
                'tid': row['tid'],
                'ports': row['ports'].split(','),
                'to_number': row['to_number'],
                'text_hash': row['text_hash'],
                'template_text': row['template_text'],
                'template_vars': json.loads(row['template_vars']) if row['template_vars'] else {},
                'submitted_at': row['submitted_at'],
                'status': row['status']
            }
        return None
    
    def get_recent_sms_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent SMS tasks."""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT * FROM sms_tasks 
            ORDER BY submitted_at DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                'tid': row['tid'],
                'ports': row['ports'].split(','),
                'to_number': row['to_number'],
                'text_hash': row['text_hash'],
                'template_text': row['template_text'],
                'template_vars': json.loads(row['template_vars']) if row['template_vars'] else {},
                'submitted_at': row['submitted_at'],
                'status': row['status']
            }
            for row in rows
        ]
    
    def update_task_status(self, tid: int, status: str) -> None:
        """Update task status."""
        with self._transaction() as conn:
            conn.execute("""
                UPDATE sms_tasks SET status = ? WHERE tid = ?
            """, (status, tid))
    
    # Task Report Management
    def save_task_report(self, report: SMSTaskReport) -> None:
        """Save a task report."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_reports 
                (tid, sending, sent, failed, unsent, sdr_details, fdr_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report.tid,
                report.sending,
                report.sent,
                report.failed,
                report.unsent,
                json.dumps(report.sdr),
                json.dumps(report.fdr)
            ))
    
    def get_task_report(self, tid: int) -> Optional[Dict[str, Any]]:
        """Get the latest report for a task."""
        conn = self._get_connection()
        row = conn.execute("""
            SELECT * FROM task_reports 
            WHERE tid = ? 
            ORDER BY updated_at DESC 
            LIMIT 1
        """, (tid,)).fetchone()
        
        if row:
            return {
                'tid': row['tid'],
                'sending': row['sending'],
                'sent': row['sent'],
                'failed': row['failed'],
                'unsent': row['unsent'],
                'sdr_details': json.loads(row['sdr_details']) if row['sdr_details'] else [],
                'fdr_details': json.loads(row['fdr_details']) if row['fdr_details'] else [],
                'updated_at': row['updated_at']
            }
        return None
    
    def get_task_reports(self, tids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Get reports for multiple tasks."""
        if not tids:
            return {}
        
        conn = self._get_connection()
        placeholders = ','.join('?' * len(tids))
        rows = conn.execute(f"""
            SELECT DISTINCT tid, sending, sent, failed, unsent, sdr_details, fdr_details, updated_at
            FROM task_reports 
            WHERE tid IN ({placeholders})
            AND updated_at = (
                SELECT MAX(updated_at) FROM task_reports tr2 
                WHERE tr2.tid = task_reports.tid
            )
        """, tids).fetchall()
        
        reports = {}
        for row in rows:
            reports[row['tid']] = {
                'tid': row['tid'],
                'sending': row['sending'],
                'sent': row['sent'],
                'failed': row['failed'],
                'unsent': row['unsent'],
                'sdr_details': json.loads(row['sdr_details']) if row['sdr_details'] else [],
                'fdr_details': json.loads(row['fdr_details']) if row['fdr_details'] else [],
                'updated_at': row['updated_at']
            }
        
        return reports
    
    # Inbox Management
    def save_inbox_message(self, ssrc: str, sms_id: int, delivery_report: int,
                          port: str, timestamp: int, sender: str, recipient: str,
                          content: str, content_base64: str = None) -> None:
        """Save an inbox message."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO inbox_messages 
                (ssrc, sms_id, delivery_report, port, timestamp, sender, recipient, content, content_base64)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ssrc, sms_id, delivery_report, port, timestamp, sender, recipient, content, content_base64))
    
    def get_inbox_messages(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get inbox messages."""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT * FROM inbox_messages 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        
        return [
            {
                'id': row['id'],
                'ssrc': row['ssrc'],
                'sms_id': row['sms_id'],
                'delivery_report': bool(row['delivery_report']),
                'port': row['port'],
                'timestamp': row['timestamp'],
                'sender': row['sender'],
                'recipient': row['recipient'],
                'content': row['content'],
                'content_base64': row['content_base64'],
                'received_at': row['received_at']
            }
            for row in rows
        ]
    
    def get_inbox_count(self) -> int:
        """Get total count of inbox messages."""
        conn = self._get_connection()
        return conn.execute("SELECT COUNT(*) FROM inbox_messages").fetchone()[0]
    
    # Device and Port Status Management
    def save_device_status(self, device_ip: str, device_mac: str, 
                          max_ports: int, max_slots: int) -> None:
        """Save device status."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO device_status 
                (device_ip, device_mac, max_ports, max_slots)
                VALUES (?, ?, ?, ?)
            """, (device_ip, device_mac, max_ports, max_slots))
    
    def save_port_status(self, device_ip: str, port: str, status_code: int,
                        status_text: str, balance: str = None, operator: str = None,
                        sim_number: str = None, imei: str = None, 
                        imsi: str = None, iccid: str = None) -> None:
        """Save port status."""
        with self._transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO port_status 
                (device_ip, port, status_code, status_text, balance, operator, 
                 sim_number, imei, imsi, iccid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (device_ip, port, status_code, status_text, balance, operator,
                  sim_number, imei, imsi, iccid))
    
    def get_port_status(self, device_ip: str, port: str = None) -> List[Dict[str, Any]]:
        """Get port status for device."""
        conn = self._get_connection()
        
        if port:
            rows = conn.execute("""
                SELECT * FROM port_status 
                WHERE device_ip = ? AND port = ?
                ORDER BY updated_at DESC
            """, (device_ip, port)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM port_status 
                WHERE device_ip = ?
                ORDER BY port, updated_at DESC
            """, (device_ip,)).fetchall()
        
        return [
            {
                'device_ip': row['device_ip'],
                'port': row['port'],
                'status_code': row['status_code'],
                'status_text': row['status_text'],
                'balance': row['balance'],
                'operator': row['operator'],
                'sim_number': row['sim_number'],
                'imei': row['imei'],
                'imsi': row['imsi'],
                'iccid': row['iccid'],
                'updated_at': row['updated_at']
            }
            for row in rows
        ]
    
    # Utility methods
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old data from the database."""
        cutoff_date = datetime.now().isoformat()[:-3]  # Remove microseconds
        
        with self._transaction() as conn:
            # Clean up old task reports
            result = conn.execute("""
                DELETE FROM task_reports 
                WHERE updated_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            reports_deleted = result.rowcount
            
            # Clean up old inbox messages
            result = conn.execute("""
                DELETE FROM inbox_messages 
                WHERE received_at < datetime('now', '-{} days')
            """.format(days_to_keep))
            inbox_deleted = result.rowcount
            
            # Clean up old SMS tasks (keep if they have recent reports)
            result = conn.execute("""
                DELETE FROM sms_tasks 
                WHERE submitted_at < datetime('now', '-{} days')
                AND tid NOT IN (
                    SELECT DISTINCT tid FROM task_reports 
                    WHERE updated_at >= datetime('now', '-{} days')
                )
            """.format(days_to_keep, days_to_keep))
            tasks_deleted = result.rowcount
        
        return {
            'tasks_deleted': tasks_deleted,
            'reports_deleted': reports_deleted,
            'inbox_deleted': inbox_deleted
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self._get_connection()
        
        stats = {}
        
        # Task stats
        row = conn.execute("SELECT COUNT(*) FROM sms_tasks").fetchone()
        stats['total_tasks'] = row[0]
        
        row = conn.execute("SELECT COUNT(*) FROM task_reports").fetchone()
        stats['total_reports'] = row[0]
        
        row = conn.execute("SELECT COUNT(*) FROM inbox_messages").fetchone()
        stats['total_inbox'] = row[0]
        
        row = conn.execute("SELECT COUNT(*) FROM port_status").fetchone()
        stats['total_ports'] = row[0]
        
        # Recent activity
        row = conn.execute("""
            SELECT COUNT(*) FROM sms_tasks 
            WHERE submitted_at >= datetime('now', '-1 day')
        """).fetchone()
        stats['tasks_last_24h'] = row[0]
        
        row = conn.execute("""
            SELECT COUNT(*) FROM inbox_messages 
            WHERE received_at >= datetime('now', '-1 day')
        """).fetchone()
        stats['inbox_last_24h'] = row[0]
        
        return stats
    
    def close(self) -> None:
        """Close database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()


# Global store instance (will be initialized by config)
_store: Optional[EjoinStore] = None


def get_store() -> EjoinStore:
    """Get the global store instance."""
    if _store is None:
        raise RuntimeError("Store not initialized. Call initialize_store() first.")
    return _store


def initialize_store(db_path: Path) -> EjoinStore:
    """Initialize the global store instance."""
    global _store
    _store = EjoinStore(db_path)
    return _store