"""Tests for SQLite storage functionality."""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

from ejoinctl.store import SQLiteStorage
from ejoinctl.models import (
    SMSTask,
    SMSReport,
    InboxMessage,
    DeviceStatus,
    PortStatus,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def storage(temp_db):
    """Create a storage instance with temporary database."""
    return SQLiteStorage(temp_db)


@pytest.fixture
def sample_sms_task():
    """Create a sample SMS task for testing."""
    return SMSTask(
        ports=["1A", "2B"],
        message="Test message",
        phone_numbers=["1234567890", "0987654321"]
    )


@pytest.fixture
def sample_sms_report():
    """Create a sample SMS report for testing."""
    return SMSReport(
        task_id="task-123",
        port="1A",
        phone_number="1234567890",
        message="Test message",
        status=0,
        response_message="OK",
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_inbox_message():
    """Create a sample inbox message for testing."""
    return InboxMessage(
        port="1A",
        sender="1234567890",
        message="Reply message",
        timestamp=datetime.now(timezone.utc),
        is_read=False
    )


def test_storage_initialization(temp_db):
    """Test storage initialization and table creation."""
    storage = SQLiteStorage(temp_db)
    
    # Check that database file was created
    assert os.path.exists(temp_db)
    
    # Check that tables exist by trying to query them
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check sms_tasks table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sms_tasks'")
        assert cursor.fetchone() is not None
        
        # Check sms_reports table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sms_reports'")
        assert cursor.fetchone() is not None
        
        # Check inbox_messages table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inbox_messages'")
        assert cursor.fetchone() is not None
        
        # Check device_status table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='device_status'")
        assert cursor.fetchone() is not None
        
        # Check port_status table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='port_status'")
        assert cursor.fetchone() is not None


def test_store_sms_task(storage, sample_sms_task):
    """Test storing SMS task."""
    task_id = storage.store_sms_task(sample_sms_task)
    
    assert task_id is not None
    assert len(task_id) > 0
    
    # Verify task was stored
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sms_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == "1A,2B"  # ports
        assert row[2] == "Test message"  # message
        assert row[3] == "1234567890,0987654321"  # phone_numbers


def test_store_sms_report(storage, sample_sms_report):
    """Test storing SMS report."""
    report_id = storage.store_sms_report(sample_sms_report)
    
    assert report_id is not None
    assert report_id > 0
    
    # Verify report was stored
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sms_reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == "task-123"  # task_id
        assert row[2] == "1A"  # port
        assert row[3] == "1234567890"  # phone_number
        assert row[4] == "Test message"  # message
        assert row[5] == 0  # status


def test_store_inbox_message(storage, sample_inbox_message):
    """Test storing inbox message."""
    message_id = storage.store_inbox_message(sample_inbox_message)
    
    assert message_id is not None
    assert message_id > 0
    
    # Verify message was stored
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inbox_messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == "1A"  # port
        assert row[2] == "1234567890"  # sender
        assert row[3] == "Reply message"  # message
        assert row[5] == 0  # is_read (False -> 0)


def test_get_sms_reports(storage):
    """Test retrieving SMS reports."""
    # Store some test reports
    report1 = SMSReport(
        task_id="task-1",
        port="1A",
        phone_number="1111111111",
        message="Message 1",
        status=0,
        response_message="OK"
    )
    
    report2 = SMSReport(
        task_id="task-1",
        port="2B",
        phone_number="2222222222",
        message="Message 2",
        status=1,
        response_message="Failed"
    )
    
    storage.store_sms_report(report1)
    storage.store_sms_report(report2)
    
    # Get all reports for task-1
    reports = storage.get_sms_reports(task_id="task-1")
    assert len(reports) == 2
    
    # Get reports by port
    reports_1a = storage.get_sms_reports(port="1A")
    assert len(reports_1a) == 1
    assert reports_1a[0].port == "1A"
    
    # Get failed reports
    failed_reports = storage.get_sms_reports(status=1)
    assert len(failed_reports) == 1
    assert failed_reports[0].status == 1


def test_get_inbox_messages(storage):
    """Test retrieving inbox messages."""
    # Store some test messages
    msg1 = InboxMessage(
        port="1A",
        sender="1111111111",
        message="Message 1",
        is_read=False
    )
    
    msg2 = InboxMessage(
        port="2B",
        sender="2222222222",
        message="Message 2",
        is_read=True
    )
    
    storage.store_inbox_message(msg1)
    storage.store_inbox_message(msg2)
    
    # Get all messages
    messages = storage.get_inbox_messages()
    assert len(messages) == 2
    
    # Get unread messages
    unread = storage.get_inbox_messages(is_read=False)
    assert len(unread) == 1
    assert unread[0].message == "Message 1"
    
    # Get messages by port
    port_1a_messages = storage.get_inbox_messages(port="1A")
    assert len(port_1a_messages) == 1
    assert port_1a_messages[0].port == "1A"


def test_mark_message_read(storage):
    """Test marking inbox message as read."""
    # Store a test message
    msg = InboxMessage(
        port="1A",
        sender="1111111111",
        message="Test message",
        is_read=False
    )
    
    msg_id = storage.store_inbox_message(msg)
    
    # Mark as read
    storage.mark_message_read(msg_id)
    
    # Verify it's marked as read
    messages = storage.get_inbox_messages(message_id=msg_id)
    assert len(messages) == 1
    assert messages[0].is_read is True


def test_update_device_status(storage):
    """Test updating device status."""
    device_status = DeviceStatus(
        gateway_host="192.168.1.1",
        device_id="TEST001",
        signal_strength=20,
        network_status="connected",
        ports=[
            PortStatus(port="1A", status="ready", imei="123456789012345"),
            PortStatus(port="1B", status="locked", imei="123456789012346")
        ]
    )
    
    storage.update_device_status(device_status)
    
    # Verify device status was stored
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM device_status WHERE gateway_host = ?", ("192.168.1.1",))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == "TEST001"  # device_id
        assert row[2] == 20  # signal_strength
        assert row[3] == "connected"  # network_status


def test_get_device_status(storage):
    """Test retrieving device status."""
    # Store test status
    device_status = DeviceStatus(
        gateway_host="192.168.1.1",
        device_id="TEST001",
        signal_strength=25,
        network_status="connected",
        ports=[]
    )
    
    storage.update_device_status(device_status)
    
    # Retrieve status
    retrieved = storage.get_device_status("192.168.1.1")
    
    assert retrieved is not None
    assert retrieved.gateway_host == "192.168.1.1"
    assert retrieved.device_id == "TEST001"
    assert retrieved.signal_strength == 25
    assert retrieved.network_status == "connected"


def test_port_status_integration(storage):
    """Test port status storage and retrieval."""
    device_status = DeviceStatus(
        gateway_host="192.168.1.1",
        device_id="TEST001",
        signal_strength=20,
        network_status="connected",
        ports=[
            PortStatus(port="1A", status="ready", imei="123456789012345"),
            PortStatus(port="1B", status="locked", imei="123456789012346")
        ]
    )
    
    storage.update_device_status(device_status)
    
    # Verify port statuses were stored
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM port_status WHERE gateway_host = ? ORDER BY port",
            ("192.168.1.1",)
        )
        rows = cursor.fetchall()
        
        assert len(rows) == 2
        assert rows[0][1] == "1A"  # port
        assert rows[0][2] == "ready"  # status
        assert rows[0][3] == "123456789012345"  # imei
        assert rows[1][1] == "1B"
        assert rows[1][2] == "locked"


def test_get_port_statuses(storage):
    """Test retrieving port statuses."""
    # Store test data
    device_status = DeviceStatus(
        gateway_host="192.168.1.1",
        device_id="TEST001",
        signal_strength=20,
        network_status="connected",
        ports=[
            PortStatus(port="1A", status="ready", imei="123456789012345"),
            PortStatus(port="2B", status="offline", imei="123456789012346")
        ]
    )
    
    storage.update_device_status(device_status)
    
    # Get all port statuses
    port_statuses = storage.get_port_statuses("192.168.1.1")
    assert len(port_statuses) == 2
    
    # Get specific port status
    port_1a = storage.get_port_statuses("192.168.1.1", port="1A")
    assert len(port_1a) == 1
    assert port_1a[0].port == "1A"
    assert port_1a[0].status == "ready"


def test_database_concurrency(storage):
    """Test database operations with multiple connections."""
    import threading
    import time
    
    results = []
    
    def worker(worker_id):
        # Each worker stores some data
        for i in range(5):
            task = SMSTask(
                ports=[f"{worker_id}A"],
                message=f"Message {i} from worker {worker_id}",
                phone_numbers=[f"123456789{worker_id}"]
            )
            task_id = storage.store_sms_task(task)
            results.append((worker_id, task_id))
            time.sleep(0.01)  # Small delay to interleave operations
    
    # Start multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify all operations completed successfully
    assert len(results) == 15  # 3 workers × 5 operations each
    
    # Verify all task IDs are unique
    task_ids = [result[1] for result in results]
    assert len(set(task_ids)) == 15


def test_cleanup_old_data(storage):
    """Test cleanup of old data."""
    from datetime import timedelta
    
    # Store old and new messages
    old_time = datetime.now(timezone.utc) - timedelta(days=8)
    new_time = datetime.now(timezone.utc)
    
    # Create reports with different timestamps
    old_report = SMSReport(
        task_id="old-task",
        port="1A",
        phone_number="1111111111",
        message="Old message",
        status=0,
        response_message="OK",
        timestamp=old_time
    )
    
    new_report = SMSReport(
        task_id="new-task",
        port="1A",
        phone_number="2222222222",
        message="New message",
        status=0,
        response_message="OK",
        timestamp=new_time
    )
    
    storage.store_sms_report(old_report)
    storage.store_sms_report(new_report)
    
    # Get all reports before cleanup
    all_reports = storage.get_sms_reports()
    assert len(all_reports) == 2
    
    # Cleanup old reports (older than 7 days)
    storage.cleanup_old_reports(days=7)
    
    # Should only have the new report
    remaining_reports = storage.get_sms_reports()
    assert len(remaining_reports) == 1
    assert remaining_reports[0].task_id == "new-task"


def test_storage_context_manager(temp_db):
    """Test storage as context manager."""
    with SQLiteStorage(temp_db) as storage:
        # Store some data
        task = SMSTask(
            ports=["1A"],
            message="Test message",
            phone_numbers=["1234567890"]
        )
        task_id = storage.store_sms_task(task)
        assert task_id is not None
    
    # Verify data persists after context exit
    with SQLiteStorage(temp_db) as storage2:
        with storage2._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sms_tasks")
            count = cursor.fetchone()[0]
            assert count == 1