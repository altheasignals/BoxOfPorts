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