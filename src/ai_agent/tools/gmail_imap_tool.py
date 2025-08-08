"""
Simple Gmail access using IMAP with app passwords
Users just need to provide email + app password
"""
import imaplib
import email
from email.header import decode_header
from typing import List, Optional
from datetime import datetime, timedelta
import time

from ..state import Message, InputType


class GmailIMAPTool:
    def __init__(self, email_address: str, app_password: str):
        self.email = email_address
        self.password = app_password
        self.imap = None
    
    def connect(self) -> bool:
        """Connect to Gmail via IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            self.imap.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"Failed to connect to Gmail: {e}")
            return False
    
    def get_unread_messages(self, max_count: int = 10) -> List[Message]:
        """Get unread messages from the last hour via IMAP"""
        if not self.imap:
            if not self.connect():
                return []
        
        try:
            self.imap.select('INBOX')
            
            # Get emails from the last hour only
            one_hour_ago = datetime.now() - timedelta(hours=1)
            since_date = one_hour_ago.strftime('%d-%b-%Y')
            
            print(f"Searching for unread messages since {since_date} (last hour)")
            search_criteria = f'(UNSEEN SINCE {since_date})'
            
            status, messages = self.imap.search(None, search_criteria)
            if status != 'OK':
                return []
            
            message_ids = messages[0].split()[-max_count:]  # Get latest N
            parsed_messages = []
            
            for msg_id in message_ids:
                status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    parsed_msg = self._parse_email(raw_email)
                    if parsed_msg:
                        # Double-check the timestamp is within the last hour
                        try:
                            msg_time = datetime.fromisoformat(parsed_msg.timestamp.replace('Z', '+00:00'))
                            if msg_time.replace(tzinfo=None) >= one_hour_ago:
                                parsed_messages.append(parsed_msg)
                        except:
                            # If timestamp parsing fails, include the message anyway
                            parsed_messages.append(parsed_msg)
            
            return parsed_messages
            
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def get_latest_message(self) -> Optional[Message]:
        """Get most recent unread message"""
        messages = self.get_unread_messages(max_count=1)
        return messages[0] if messages else None
    
    def _parse_email(self, raw_email: bytes) -> Optional[Message]:
        """Parse raw email into Message object"""
        try:
            email_msg = email.message_from_bytes(raw_email)
            
            # Get headers
            sender = self._decode_header(email_msg.get('From', ''))
            recipient = self._decode_header(email_msg.get('To', ''))
            subject = self._decode_header(email_msg.get('Subject', ''))
            
            # Get body
            body = self._extract_body(email_msg)
            
            # Get timestamp
            date_str = email_msg.get('Date', '')
            timestamp = datetime.now().isoformat()  # Fallback
            
            return Message(
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                timestamp=timestamp,
                input_type=InputType.EMAIL,
                source="gmail"
            )
            
        except Exception as e:
            print(f"Error parsing email: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded = decode_header(header)[0]
            if decoded[1]:
                return decoded[0].decode(decoded[1])
            return str(decoded[0])
        except:
            return header
    
    def _extract_body(self, email_msg) -> str:
        """Extract email body text"""
        body = ""
        
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            if email_msg.get_content_type() == "text/plain":
                body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def disconnect(self):
        """Close IMAP connection"""
        if self.imap:
            self.imap.close()
            self.imap.logout()