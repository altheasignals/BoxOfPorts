"""SMS inbox management service for EJOIN Multi-WAN Router."""

import logging
from typing import Any

from .api_models import MessageType, SMSInboxFilter, SMSMessage
from .config import EjoinConfig
from .http import EjoinHTTPError, create_sync_client

logger = logging.getLogger(__name__)


class SMSInboxService:
    """Service for managing SMS inbox operations."""

    def __init__(self, config: EjoinConfig):
        self.config = config
        self.client = create_sync_client(config)

    def get_messages(
        self,
        start_id: int = 1,
        count: int = 0,
        delete_after: bool = False
    ) -> list[SMSMessage]:
        """Retrieve SMS messages from the device inbox.
        
        Args:
            start_id: Starting SMS ID (1-based)
            count: Number of messages to retrieve (0 = all)
            delete_after: Delete messages from device after retrieval
            
        Returns:
            List of parsed SMS messages
        """
        try:
            response = self.client.get_sms_inbox(
                sms_id=start_id,
                sms_num=count,
                delete_after=delete_after
            )

            if response.get("code") != 0:
                raise EjoinHTTPError(
                    f"Failed to retrieve SMS: {response.get('reason', 'Unknown error')}"
                )

            messages = []
            sms_data = response.get("data", [])
            base_id = start_id

            for i, sms_array in enumerate(sms_data):
                try:
                    message = SMSMessage.from_api_data(base_id + i, sms_array)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Failed to parse SMS {base_id + i}: {e}")
                    continue

            logger.info(f"Retrieved {len(messages)} SMS messages")
            return messages

        except EjoinHTTPError:
            raise
        except Exception as e:
            raise EjoinHTTPError(f"Failed to retrieve SMS inbox: {e}") from e

    def filter_messages(
        self,
        messages: list[SMSMessage],
        filter_criteria: SMSInboxFilter
    ) -> list[SMSMessage]:
        """Filter messages based on criteria.
        
        Args:
            messages: List of SMS messages to filter
            filter_criteria: Filter criteria
            
        Returns:
            Filtered list of messages
        """
        filtered = messages

        # Filter by message type
        if filter_criteria.message_type:
            filtered = [msg for msg in filtered if msg.message_type == filter_criteria.message_type]

        # Filter by text content
        if filter_criteria.contains_text:
            search_text = filter_criteria.contains_text.lower()
            filtered = [msg for msg in filtered if search_text in msg.content.lower()]

        # Filter by sender
        if filter_criteria.sender:
            filtered = [msg for msg in filtered if filter_criteria.sender in msg.sender]

        # Filter by port (single or multiple)
        if filter_criteria.port:
            filtered = [msg for msg in filtered if msg.port == filter_criteria.port]
        elif filter_criteria.ports:
            filtered = [msg for msg in filtered if msg.port in filter_criteria.ports]

        # Filter by timestamp range
        if filter_criteria.since:
            filtered = [msg for msg in filtered if msg.timestamp >= filter_criteria.since]

        if filter_criteria.until:
            filtered = [msg for msg in filtered if msg.timestamp <= filter_criteria.until]

        # Filter by keywords
        if filter_criteria.keywords:
            filtered = [
                msg for msg in filtered
                if any(keyword in msg.contains_keywords for keyword in filter_criteria.keywords)
            ]

        # Filter delivery reports
        if filter_criteria.delivery_reports_only:
            filtered = [msg for msg in filtered if msg.is_delivery_report]
        elif filter_criteria.exclude_delivery_reports:
            filtered = [msg for msg in filtered if not msg.is_delivery_report]

        # Filter by delivery status code
        if filter_criteria.delivery_status_code is not None:
            filtered = [
                msg for msg in filtered
                if msg.is_delivery_report and msg.delivery_status_code == filter_criteria.delivery_status_code
            ]

        return filtered

    def get_stop_messages(self, start_id: int = 1) -> list[SMSMessage]:
        """Get all STOP/unsubscribe messages.
        
        Args:
            start_id: Starting SMS ID
            
        Returns:
            List of STOP messages
        """
        all_messages = self.get_messages(start_id=start_id)
        return [msg for msg in all_messages if msg.message_type == MessageType.STOP]

    def get_messages_containing(self, text: str, start_id: int = 1) -> list[SMSMessage]:
        """Get messages containing specific text.
        
        Args:
            text: Text to search for
            start_id: Starting SMS ID
            
        Returns:
            List of messages containing the text
        """
        filter_criteria = SMSInboxFilter(contains_text=text)
        all_messages = self.get_messages(start_id=start_id)
        return self.filter_messages(all_messages, filter_criteria)

    def get_messages_by_type(self, message_type: MessageType, start_id: int = 1) -> list[SMSMessage]:
        """Get messages by type.
        
        Args:
            message_type: Type of messages to retrieve
            start_id: Starting SMS ID
            
        Returns:
            List of messages of the specified type
        """
        filter_criteria = SMSInboxFilter(message_type=message_type)
        all_messages = self.get_messages(start_id=start_id)
        return self.filter_messages(all_messages, filter_criteria)

    def get_messages_by_port(self, port: str, start_id: int = 1) -> list[SMSMessage]:
        """Get messages received on a specific port.
        
        Args:
            port: Port identifier (e.g., '1A', '2B')
            start_id: Starting SMS ID
            
        Returns:
            List of messages received on the specified port
        """
        filter_criteria = SMSInboxFilter(port=port)
        all_messages = self.get_messages(start_id=start_id)
        return self.filter_messages(all_messages, filter_criteria)

    def get_delivery_reports(self, start_id: int = 1) -> list[SMSMessage]:
        """Get SMS delivery reports only.
        
        Args:
            start_id: Starting SMS ID
            
        Returns:
            List of delivery report messages
        """
        filter_criteria = SMSInboxFilter(delivery_reports_only=True)
        all_messages = self.get_messages(start_id=start_id)
        return self.filter_messages(all_messages, filter_criteria)

    def get_regular_messages(self, start_id: int = 1) -> list[SMSMessage]:
        """Get regular SMS messages (excluding delivery reports).
        
        Args:
            start_id: Starting SMS ID
            
        Returns:
            List of regular SMS messages
        """
        filter_criteria = SMSInboxFilter(exclude_delivery_reports=True)
        all_messages = self.get_messages(start_id=start_id)
        return self.filter_messages(all_messages, filter_criteria)

    def get_inbox_summary(self, start_id: int = 1) -> dict[str, Any]:
        """Get a summary of the inbox contents.
        
        Args:
            start_id: Starting SMS ID
        
        Returns:
            Dictionary with inbox statistics
        """
        try:
            messages = self.get_messages(start_id=start_id)

            summary = {
                "total_messages": len(messages),
                "by_type": {},
                "by_port": {},
                "stop_messages": 0,
                "delivery_reports": 0,
                "regular_messages": 0,
                "recent_senders": set(),
                "date_range": None
            }

            if not messages:
                return summary

            # Count by message type
            for msg_type in MessageType:
                summary["by_type"][msg_type.value] = len(
                    [msg for msg in messages if msg.message_type == msg_type]
                )

            # Count by port
            for msg in messages:
                port = msg.port
                summary["by_port"][port] = summary["by_port"].get(port, 0) + 1

            # Special counts
            summary["stop_messages"] = summary["by_type"].get(MessageType.STOP.value, 0)
            summary["delivery_reports"] = len([msg for msg in messages if msg.is_delivery_report])
            summary["regular_messages"] = len([msg for msg in messages if not msg.is_delivery_report])

            # Recent senders (limit to avoid memory issues)
            summary["recent_senders"] = list(set(
                msg.sender for msg in messages[:100] if not msg.is_delivery_report
            ))

            # Date range
            if messages:
                timestamps = [msg.timestamp for msg in messages]
                summary["date_range"] = {
                    "earliest": min(timestamps).isoformat(),
                    "latest": max(timestamps).isoformat()
                }

            return summary

        except Exception as e:
            logger.error(f"Failed to get inbox summary: {e}")
            raise EjoinHTTPError(f"Failed to get inbox summary: {e}") from e
