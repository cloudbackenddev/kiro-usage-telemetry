#!/usr/bin/env python3
import sqlite3
import os
import json
import sys

def main():
    devdata_db = os.path.expandvars(r'%APPDATA%\Kiro\User\globalStorage\kiro.kiroagent\dev_data\devdata.sqlite')
    state_db = os.path.expandvars(r'%APPDATA%\Kiro\User\globalStorage\state.vscdb')

    print("=== Kiro Usage Analytics ===")
    
    # 1. Total tokens
    try:
        conn = sqlite3.connect(devdata_db)
        cur = conn.cursor()
        cur.execute("SELECT SUM(tokens_prompt) FROM tokens_generated")
        row = cur.fetchone()
        total_tokens = row[0] if (row and row[0]) else 0
        print(f"[Tokens] Lifetime Prompt Tokens: {total_tokens:,}")
        conn.close()
    except Exception as e:
        print(f"[Tokens] (Error reading devdata.sqlite): {e}", file=sys.stderr)

    # 2. Credits from Global State
    try:
        conn = sqlite3.connect(state_db)
        cur = conn.cursor()
        cur.execute("SELECT value FROM ItemTable WHERE key = 'kiro.kiroAgent'")
        row = cur.fetchone()
        if row and row[0]:
            val = row[0]
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            state_data = json.loads(val)
            
            usage_info = state_data.get("kiro.resourceNotifications.usageState", {})
            breakdowns = usage_info.get("usageBreakdowns", [])
            
            if breakdowns:
                for b in breakdowns:
                    usage = b.get('currentUsage', 0)
                    limit = b.get('usageLimit', 0)
                    percentage = b.get('percentageUsed', 0)
                    unit = b.get('unit', 'UNITS')
                    print(f"[Credits] Usage: {usage} / {limit} {unit}")
                    print(f"[Credits] Consumed: {percentage}%")
                    
                    if percentage >= 80:
                        print(f"** WARNING ** Credit usage is at {percentage}%. You are nearing or at your limit!")
            else:
                print("[Credits] No detailed credit tracking block found in state.")
        else:
            print("[Credits] Global state 'kiro.kiroAgent' key missing.")
        conn.close()
    except Exception as e:
        print(f"[Credits] (Error reading state.vscdb): {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
