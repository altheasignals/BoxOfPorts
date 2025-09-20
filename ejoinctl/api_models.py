"""Pydantic models for EJOIN Multi-WAN Router HTTP API v2.2."""

from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


# Status and Error Codes
class SMSStatusCode(IntEnum):
    """SMS task status codes."""
    OK = 0
    INVALID_USER = 1
    INVALID_PORT = 2
    USSD_EXPECTED = 3
    PENDING_USSD = 4
    SIM_UNREGISTERED = 5
    TIMEOUT = 6
    SERVER_ERROR = 7
    SMS_EXPECTED = 8
    TO_EXPECTED = 9
    PENDING_TRANSACTION = 10
    TID_EXPECTED = 11
    FROM_EXPECTED = 12
    DUPLICATED_TASK_ID = 13
    UNAUTHORIZED = 14
    INVALID_CMD = 15
    TOO_MANY_TASK = 16


class PortStatusCode(IntEnum):
    """Port status codes."""
    NO_SIM_CARD = 0
    IDLE_SIM_CARD = 1
    REGISTERING = 2
    REGISTERED = 3
    NO_BALANCE = 5
    REGISTER_FAILED = 6
    SIM_LOCKED_DEVICE = 7
    SIM_LOCKED_OPERATOR = 8
    SIM_ERROR = 9
    CARD_DETECTED = 11
    USER_LOCKED = 12


# Base Response Models
class BaseResponse(BaseModel):
    """Base response model for API responses."""
    code: int = Field(..., description="Result code")
    reason: str = Field(..., description="Reason description")


# SMS Models
class SMSTask(BaseModel):
    """SMS task configuration."""
    tid: int = Field(..., description="Task ID")
    from_: Optional[str] = Field(None, alias="from", description="Sender port(s)")
    to: str = Field(..., description="Recipient number(s)")
    sms: str = Field(..., description="SMS content")
    chs: str = Field("utf8", description="Character encoding set")
    coding: int = Field(0, description="SMS codec: 0=auto, 1=USC2, 2=7bit")
    smstype: int = Field(0, description="SMS type: 0=SMS")
    smsc: str = Field("", description="SMSC number")
    intvl: str = Field("0", description="Interval between SMS in ms")
    tmo: int = Field(30, description="Timeout in seconds")
    sdr: int = Field(0, description="Enable delivery report: 0=disable, 1=enable")
    fdr: int = Field(1, description="Enable failed report: 0=disable, 1=enable")
    dr: int = Field(0, description="Enable SMS delivery report: 0=disable, 1=enable")
    sr_prd: int = Field(60, description="Status report period in seconds")
    sr_cnt: int = Field(10, description="Status report message count")


class SMSSendRequest(BaseModel):
    """SMS send request."""
    type: str = Field("send-sms", description="Message type")
    task_num: int = Field(..., description="Number of tasks")
    tasks: List[SMSTask] = Field(..., description="List of SMS tasks")
    # Global settings
    sr_url: Optional[str] = Field(None, description="Status report URL")
    sr_cnt: int = Field(100, description="Max SMS results in cache")
    sr_prd: int = Field(30, description="Max time SMS results in cache")
    sms_url: Optional[str] = Field(None, description="SMS forward URL")
    sms_cnt: int = Field(1, description="Max SMS in cache")
    sms_prd: int = Field(30, description="Max time SMS in cache")


class SMSTaskStatus(BaseModel):
    """SMS task status."""
    tid: int = Field(..., description="Task ID")
    status: str = Field(..., description="Status code and description")


class SMSSendResponse(BaseResponse):
    """SMS send response."""
    type: str = Field("task-status", description="Response type")
    status: List[SMSTaskStatus] = Field(..., description="Task status list")


class SMSTaskReport(BaseModel):
    """SMS task report details."""
    tid: int = Field(..., description="Task ID")
    sending: int = Field(0, description="Number of SMS being sent")
    sent: int = Field(0, description="Number of SMS successfully sent")
    failed: int = Field(0, description="Number of SMS failed")
    unsent: int = Field(0, description="Number of unsent SMS")
    sdr: List[List[Union[int, str]]] = Field(default_factory=list, description="Success delivery reports")
    fdr: List[List[Union[int, str]]] = Field(default_factory=list, description="Failed delivery reports")


class SMSStatusReport(BaseModel):
    """SMS status report from device."""
    type: str = Field("status-report", description="Message type")
    rpt_num: int = Field(..., description="Number of reports")
    rpts: List[SMSTaskReport] = Field(..., description="Task reports")


class SMSControlRequest(BaseModel):
    """Request to pause/resume/delete SMS tasks."""
    tids: List[int] = Field(..., description="Task IDs to control")


class SMSQueryRequest(BaseModel):
    """SMS task query parameters."""
    port: int = Field(..., description="Port number (1-based)")
    pos: int = Field(0, description="Starting position")
    num: int = Field(10, description="Number of tasks to return")
    has_content: int = Field(0, description="Include SMS content: 0=no, 1=yes")


class SMSQueryResponse(BaseResponse):
    """SMS query response."""
    total_num: int = Field(..., description="Total number of tasks")
    task_num: int = Field(..., description="Number of tasks returned")
    tasks: List[SMSTask] = Field(..., description="Task list")


# Device Operation Models
class DeviceOperation(BaseModel):
    """Device operation request."""
    type: str = Field("command", description="Message type")
    op: str = Field(..., description="Operation type")
    ports: Optional[str] = Field(None, description="Target ports")
    ops: Optional[List[Dict[str, Any]]] = Field(None, description="Multiple operations")
    # Parameters for specific operations
    mode: Optional[int] = Field(None, description="Redial mode: 0=flight, 1=fast")
    delay: Optional[int] = Field(None, description="Delay in seconds")
    par_name: Optional[Dict[str, str]] = Field(None, description="Parameter name/value pairs")


# Status Models
class PortStatus(BaseModel):
    """Individual port status."""
    port: str = Field(..., description="Port identifier")
    st: str = Field(..., description="Status code and details")
    bal: Optional[str] = Field(None, description="SIM card balance")
    opr: Optional[str] = Field(None, description="Operator name and ID")
    sn: Optional[str] = Field(None, description="SIM number")
    imei: Optional[str] = Field(None, description="IMEI")
    imsi: Optional[str] = Field(None, description="IMSI")
    iccid: Optional[str] = Field(None, description="ICCID")


class DeviceStatus(BaseModel):
    """Device status message."""
    type: str = Field("dev-status", description="Message type")
    seq: int = Field(..., description="Sequence number")
    expires: int = Field(180, description="Status validity period")
    mac: str = Field(..., description="Device MAC address")
    ip: str = Field(..., description="Device IP address")
    max_ports: int = Field(..., description="Maximum ports")
    max_slots: int = Field(4, description="Maximum SIM slots")
    status: List[PortStatus] = Field(..., description="Port status list")


class PortStatusMessage(BaseModel):
    """Individual port status change message."""
    type: str = Field("port-status", description="Message type")
    port: str = Field(..., description="Port identifier")
    seq: int = Field(..., description="Sequence number")
    status: str = Field(..., description="Status code and details")
    bal: Optional[str] = Field(None, description="Balance")
    opr: Optional[str] = Field(None, description="Operator")
    sn: Optional[str] = Field(None, description="SIM number")
    imei: Optional[str] = Field(None, description="IMEI")
    imsi: Optional[str] = Field(None, description="IMSI")
    iccid: Optional[str] = Field(None, description="ICCID")


# Inbox and SMS Receiving Models
class ReceivedSMS(BaseModel):
    """Received SMS message."""
    type: str = Field("recv-sms", description="Message type")
    sms_num: int = Field(..., description="Number of SMS")
    sms: List[List[Union[int, str]]] = Field(..., description="SMS array data")


class SMSQueryInboxRequest(BaseModel):
    """SMS inbox query request."""
    sms_id: int = Field(1, description="Starting SMS ID")
    sms_num: int = Field(0, description="Number of SMS to query (0=all)")
    sms_del: int = Field(0, description="Delete after query: 0=no, 1=yes")


class SMSInboxResponse(BaseResponse):
    """SMS inbox query response."""
    ssrc: str = Field(..., description="Synchronization source ID")
    sms_num: int = Field(..., description="Number of SMS returned")
    next_sms: int = Field(..., description="Next SMS ID")
    data: List[List[Union[int, str]]] = Field(..., description="SMS data array")


# Proxy Configuration Models
class ProxyConfig(BaseModel):
    """Proxy configuration."""
    name: str = Field(..., description="Proxy name")
    port: int = Field(..., description="Proxy port")
    interfaces: List[int] = Field(..., description="SIM WAN interfaces")
    active: int = Field(1, description="Active status: 0=disabled, 1=enabled")


class ProxyUser(BaseModel):
    """Proxy user configuration."""
    name: str = Field(..., description="Username")
    pwd: str = Field(..., description="Password")
    interfaces: List[int] = Field(..., description="SIM WAN interfaces")
    mark: Optional[str] = Field(None, description="User mark/comment")


class ProxyRequest(BaseModel):
    """Proxy configuration request."""
    proxies: Optional[List[ProxyConfig]] = Field(None, description="Proxy configurations")
    users: Optional[List[ProxyUser]] = Field(None, description="Proxy users")
    urls: Optional[List[str]] = Field(None, description="URL whitelist/blacklist")


class ProxyResponse(BaseResponse):
    """Proxy configuration response."""
    mode: Optional[int] = Field(None, description="Proxy mode")
    enabled: Optional[int] = Field(None, description="Enable status")
    size: Optional[int] = Field(None, description="Number of configurations")
    proxies: Optional[List[ProxyConfig]] = Field(None, description="Proxy configurations")
    users: Optional[List[ProxyUser]] = Field(None, description="Proxy users")
    urls: Optional[List[str]] = Field(None, description="URL list")


# IP Whitelist/Blacklist Models
class IPListConfig(BaseModel):
    """IP whitelist/blacklist configuration."""
    enable: int = Field(0, description="Enable status: 0=disabled, 1=enabled")
    deleted_set: Optional[List[str]] = Field(None, description="IPs to delete")
    added_set: Optional[List[str]] = Field(None, description="IPs to add")


class IPListResponse(BaseResponse):
    """IP list response."""
    enable: int = Field(..., description="Enable status")
    ipset: List[str] = Field(..., description="IP address list")


# Enhanced SMS Inbox Models
from datetime import datetime
from enum import Enum
import base64

class MessageType(str, Enum):
    """SMS message type classification."""
    REGULAR = "regular"  # Normal SMS from users
    DELIVERY_REPORT = "delivery_report"  # SMS delivery confirmations
    SYSTEM = "system"  # System/operator messages
    STOP = "stop"  # Opt-out messages containing STOP
    KEYWORD = "keyword"  # Messages containing specific keywords
    
class SMSMessage(BaseModel):
    """Parsed SMS message with enhanced metadata."""
    id: int = Field(..., description="SMS ID")
    message_type: MessageType = Field(..., description="Classified message type")
    is_delivery_report: bool = Field(..., description="Is this a delivery report")
    port: str = Field(..., description="Receiving port (e.g., '1A', '2B')")
    timestamp: datetime = Field(..., description="Message received timestamp")
    sender: str = Field(..., description="Sender phone number or SMSC")
    recipient: Optional[str] = Field(None, description="Recipient (for delivery reports)")
    content: str = Field(..., description="Decoded message content")
    raw_content: str = Field(..., description="Raw base64 content")
    contains_keywords: List[str] = Field(default_factory=list, description="Detected keywords")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @classmethod
    def from_api_data(cls, sms_id: int, sms_array: List[Union[int, str]]) -> "SMSMessage":
        """Create SMSMessage from API array format.
        
        Array format: [delivery_flag, port, timestamp, sender, recipient, content]
        - delivery_flag (int): 0=normal SMS, 1=delivery report
        - port (str): Receive port like '1.01', '1.02' 
        - timestamp (int): Unix timestamp
        - sender (str): Phone number or SMSC
        - recipient (str): Recipient number (for delivery reports)
        - content (str): Base64 encoded SMS content or delivery report
        """
        if len(sms_array) < 6:
            raise ValueError(f"Invalid SMS array format: {sms_array}")
            
        delivery_flag = int(sms_array[0])
        port = str(sms_array[1])
        timestamp = datetime.fromtimestamp(int(sms_array[2]))
        sender = str(sms_array[3])
        recipient = str(sms_array[4]) if sms_array[4] else None
        raw_content = str(sms_array[5])
        
        # Decode content
        if delivery_flag == 1:
            # Delivery report format: "code scts"
            content = raw_content
            message_type = MessageType.DELIVERY_REPORT
        else:
            # Regular SMS: BASE64 encoded UTF-8
            try:
                content = base64.b64decode(raw_content).decode('utf-8')
            except Exception:
                content = raw_content  # Fallback to raw if decoding fails
            message_type = cls._classify_message(content)
        
        # Detect keywords
        keywords = cls._extract_keywords(content)
        
        return cls(
            id=sms_id,
            message_type=message_type,
            is_delivery_report=delivery_flag == 1,
            port=cls._format_port(port),
            timestamp=timestamp,
            sender=sender,
            recipient=recipient,
            content=content,
            raw_content=raw_content,
            contains_keywords=keywords
        )
    
    @staticmethod
    def _format_port(port: str) -> str:
        """Convert port format from '1.01' to '1A' style."""
        if '.' in port:
            # Convert decimal format to letter format
            slot, port_num = port.split('.')
            port_letter = chr(ord('A') + int(port_num) - 1)
            return f"{slot}{port_letter}"
        return port
    
    @staticmethod
    def _classify_message(content: str) -> MessageType:
        """Classify message type based on content."""
        content_lower = content.lower()
        
        # Check for STOP messages
        if any(word in content_lower for word in ['stop', 'unsubscribe', 'opt out', 'opt-out']):
            return MessageType.STOP
        
        # Check for system messages (common patterns)
        system_indicators = [
            'balance', 'credit', 'recharge', 'expired', 'network',
            'service', 'plan', 'bundle', 'data', 'minutes', 'sms left'
        ]
        if any(indicator in content_lower for indicator in system_indicators):
            return MessageType.SYSTEM
            
        # Default to regular message
        return MessageType.REGULAR
    
    @staticmethod
    def _extract_keywords(content: str) -> List[str]:
        """Extract important keywords from message content."""
        keywords = []
        content_lower = content.lower()
        
        # Common keywords to detect
        keyword_patterns = {
            'stop': ['stop', 'unsubscribe', 'opt out', 'opt-out'],
            'help': ['help', 'info', 'information'],
            'balance': ['balance', 'credit', 'amount'],
            'urgent': ['urgent', 'emergency', 'important'],
            'promotion': ['offer', 'deal', 'discount', 'promo', 'sale']
        }
        
        for category, patterns in keyword_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                keywords.append(category)
        
        return keywords

class SMSInboxFilter(BaseModel):
    """Filter criteria for SMS inbox queries."""
    message_type: Optional[MessageType] = Field(None, description="Filter by message type")
    contains_text: Optional[str] = Field(None, description="Filter by text content")
    sender: Optional[str] = Field(None, description="Filter by sender number")
    port: Optional[str] = Field(None, description="Filter by receiving port")
    since: Optional[datetime] = Field(None, description="Messages since this timestamp")
    until: Optional[datetime] = Field(None, description="Messages until this timestamp")
    keywords: Optional[List[str]] = Field(None, description="Filter by keywords")
    delivery_reports_only: bool = Field(False, description="Show only delivery reports")
    exclude_delivery_reports: bool = Field(False, description="Exclude delivery reports")

# Status Code Mappings
STATUS_CODE_DESCRIPTIONS = {
    0: "OK",
    1: "Invalid User",
    2: "Invalid Port",
    3: "USSD Expected",
    4: "Pending USSD",
    5: "SIM Unregistered",
    6: "Timeout",
    7: "Server Error",
    8: "SMS Expected",
    9: "TO Expected",
    10: "Pending Transaction",
    11: "TID Expected",
    12: "FROM Expected",
    13: "Duplicated TaskId",
    14: "Unauthorized",
    15: "Invalid CMD",
    16: "Too Many Task",
}

PORT_STATUS_DESCRIPTIONS = {
    0: "No SIM card",
    1: "Idle SIM card", 
    2: "Registering",
    3: "Registered",
    5: "No balance or alarm",
    6: "Register failed",
    7: "SIM card locked by device",
    8: "SIM card locked by operator", 
    9: "Recognize SIM card error",
    11: "Card Detected",
    12: "User locked",
}


def get_status_description(code: int, code_type: str = "sms") -> str:
    """Get human-readable description for status codes."""
    if code_type == "port":
        return PORT_STATUS_DESCRIPTIONS.get(code, f"Unknown port status: {code}")
    return STATUS_CODE_DESCRIPTIONS.get(code, f"Unknown status: {code}")


# Validation helpers
def validate_port_format(port: str) -> str:
    """Validate port format."""
    import re
    if not re.match(r"^(\d+[A-D]|\d+\.\d+)$", port):
        raise ValueError(f"Invalid port format: {port}")
    return port


def validate_phone_number(phone: str) -> str:
    """Basic phone number validation."""
    import re
    if not re.match(r"^\+?[\d\-\s()]+$", phone):
        raise ValueError(f"Invalid phone number format: {phone}")
    return phone