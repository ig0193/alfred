import asyncio
import sys
import os
import argparse
import threading
import queue
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_agent.workflow import run_workflow


async def main():
    parser = argparse.ArgumentParser(description="AI Agent - Multi-Purpose Assistant")
    parser.add_argument("--gmail-interval", type=int, default=60,
                       help=f"Gmail scraping interval in seconds (default: {60})")
    
    args = parser.parse_args()
    await run_unified_daemon(args.gmail_interval)


async def run_unified_daemon(gmail_interval: int):
    # Queue for CLI commands
    cli_queue = queue.Queue()
    
    # Start CLI input thread
    cli_thread = threading.Thread(target=cli_input_thread, args=(cli_queue,), daemon=True)
    cli_thread.start()
    
    gmail_last_check = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Check for CLI commands (non-blocking)
            try:
                while not cli_queue.empty():
                    command = cli_queue.get_nowait()
                    if command.lower().strip() in ['quit', 'exit', 'stop']:
                        print("Stopping daemon...")
                        return
                    
                    print(f"\nProcessing CLI command: {command[:50]}...")
                    final_state = await run_workflow({"input_mode": "cli", "cli_command": command})
                    await print_workflow_summary(final_state)
                    
            except queue.Empty:
                pass
            
            # Check Gmail scraping interval
            if current_time - gmail_last_check >= gmail_interval:
                print(f"\nAuto-checking Gmail...")
                try:
                    final_state = await run_workflow({"input_mode": "gmail", "gmail_last_check": gmail_last_check})
                    await print_workflow_summary(final_state)
                except Exception as e:
                    print(f"Gmail scraping error: {e}")
                gmail_last_check = current_time
            
            
            # Short sleep to prevent busy waiting
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nDaemon stopped by Ctrl+C")


def cli_input_thread(cli_queue):
    """Thread function to handle CLI input non-blocking"""
    while True:
        try:
            command = input()
            if command.strip():
                cli_queue.put(command.strip())
        except (EOFError, KeyboardInterrupt):
            break


async def print_workflow_summary(final_state):
    print("\n" + "="*50)
    print("WORKFLOW SUMMARY")
    print("="*50)
    
    if final_state.get('input_message'):
        msg = final_state['input_message']
        print(f"Input type: {msg.get('input_type', 'unknown')}")
        print(f"Source: {msg.get('source', 'unknown')}")
        if msg.get('sender'):
            print(f"From: {msg['sender']}")
        if msg.get('subject'):
            print(f"Subject: {msg['subject']}")
    
    if final_state.get('action_type'):
        print(f"Action: {final_state['action_type']}")
        if final_state.get('action_confidence'):
            print(f"Confidence: {final_state['action_confidence']:.2f}")
    
    if final_state.get('tool'):
        print(f"Tool: {final_state['tool']}")
    
    if final_state.get('retrieved_context'):
        print(f"Context items: {len(final_state['retrieved_context'])}")
    
    if final_state.get('result'):
        result = final_state['result']
        print(f"Generated: {result.get('type', 'unknown')} draft")
    
    print("="*50)


if __name__ == "__main__":
    exit_code = asyncio.run(main())