#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path
from collections import defaultdict

def main():
    kiro_path = Path(os.path.expandvars(r'%APPDATA%\Kiro\User\globalStorage\kiro.kiroagent'))
    
    if not kiro_path.exists():
        print(f"Directory not found: {kiro_path}")
        return

    sessions = [d for d in os.listdir(kiro_path) if re.match(r'^[a-f0-9]{32}$', d)]
    
    total_human = 0
    total_bot = 0
    total_tools = 0
    error_instances = []

    print(f"Scanning {len(sessions)} session directories...")

    for session_dir in sessions:
        session_path = kiro_path / session_dir
        if not session_path.is_dir():
            continue
            
        chat_files = [f for f in os.listdir(session_path) if f.endswith('.chat')]
        
        for chat_name in chat_files:
            chat_file = session_path / chat_name
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Message Counts
                msgs = data.get('chat', [])
                for m in msgs:
                    role = m.get('role')
                    if role == 'human':
                        total_human += 1
                    elif role == 'bot':
                        total_bot += 1
                    elif role == 'tool':
                        total_tools += 1

                # Tool Errors
                for action in data.get("actions", []):
                    if action.get("actionState") == "Error":
                        error_instances.append({
                            "session": session_dir,
                            "file": chat_name,
                            "actionType": action.get("actionType"),
                            "error": action.get("output", {}).get("error", "Unknown error")
                        })
            except Exception as e:
                # Silently skip corrupted files
                pass

    print("\n=== Chat & Tool Summary ===")
    print(f"Total .chat Sessions Parsed: {len(sessions)}")
    print(f"Total Human Messages: {total_human}")
    print(f"Total Bot Messages:   {total_bot}")
    print(f"Total Tool Invocations: {total_tools}")

    print("\n=== Tool Execution Errors ===")
    if not error_instances:
        print("No tool execution errors found.")
    else:
        print(f"Found {len(error_instances)} failures:")
        # Group by actionType
        grouped = defaultdict(list)
        for err in error_instances:
            grouped[err['actionType']].append(err)
            
        for atype, errs in grouped.items():
            print(f"\n- Action Type: {atype} ({len(errs)} failures)")
            # Show up to 3 distinct examples
            seen_errs = set()
            for e in errs:
                err_msg = str(e['error']).strip()
                if err_msg not in seen_errs:
                    print(f"  Example: {err_msg}")
                    seen_errs.add(err_msg)
                if len(seen_errs) >= 3:
                    break

if __name__ == "__main__":
    main()
