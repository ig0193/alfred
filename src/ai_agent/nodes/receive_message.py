from typing import Dict, Any, Optional
import sys
import os
from datetime import datetime
from ..state import AgentState, Message, InputType
from ..tools.gmail_imap_tool import GmailIMAPTool


def receive_message_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent_state = AgentState.from_dict(state)
    
    input_mode = state.get("input_mode", "mock")
    cli_command = state.get("cli_command")  # For daemon-provided CLI commands
    
    if input_mode == "gmail":
        message = _scrape_gmail_messages()
        if message is None:
            print("No new messages found - stopping workflow")
            return None  # This will stop the workflow execution
    elif input_mode == "slack":
        message = _scrape_slack_messages()
    elif input_mode == "cli":
        message = _receive_cli_command(cli_command)
    
    agent_state.input_message = message
    
    print(f"Received {message.input_type.value}: {message.source}")
    if message.sender:
        print(f"From: {message.sender}")
    if message.subject:
        print(f"Subject: {message.subject}")
    print(f"Content preview: {message.body[:100]}...")
    
    return agent_state.to_dict()


def _scrape_gmail_messages() -> Optional[Message]:
    print("Scraping Gmail for new messages...")
    
    # Try IMAP method first (simpler for users)
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if gmail_email and gmail_app_password:
        try:
            print("Using Gmail IMAP (app password method)...")
            imap_tool = GmailIMAPTool(gmail_email, gmail_app_password)
            messages = imap_tool.get_unread_messages(max_count=1)
            latest_message = messages[0] if messages else None
            
            if latest_message:
                print(f"Found new message from: {latest_message.sender}")
                imap_tool.disconnect()
                return latest_message
            else:
                print("No unread messages found via IMAP")
                imap_tool.disconnect()
                return None
                
        except Exception as e:
            print(f"IMAP method failed: {e}")
    
    print("No Gmail credentials configured or no messages found")
    return None
    


def _scrape_slack_messages() -> Message:
    print("Scraping Slack for new mentions/DMs...")
    
    return Message(
        sender="john.smith",
        recipient="ai-agent",
        subject="Direct message",
        body="""Hey, can you send a quick status update to the #engineering channel about the deployment we did yesterday?

Let them know everything went smoothly and the new features are live.""",
        timestamp=datetime.now().isoformat(),
        input_type=InputType.COMMAND,
        source="slack"
    )


def _receive_cli_command(cli_command: Optional[str] = None) -> Message:
    print(f"Received CLI command: {cli_command}")
    if not cli_command:
        command = ""
    command = cli_command
    return Message(
        body=command,
        timestamp=datetime.now().isoformat(),
        input_type=InputType.COMMAND,
        source="cli"
    )


def _get_mock_message() -> Message:
    return Message(
        sender="support@example.com",
        recipient="agent@company.com",
        subject="System outage follow-up",
        body="Please provide an update on the root cause analysis for last week's outage.",
        timestamp=datetime.now().isoformat(),
        input_type=InputType.EMAIL,
        source="mock"
    )