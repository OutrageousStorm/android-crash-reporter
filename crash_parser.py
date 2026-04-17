#!/usr/bin/env python3
"""
crash_parser.py -- Parse Android logcat crashes and ANRs from bugreport or live logcat
Usage: python3 crash_parser.py bugreport.zip
       adb logcat | python3 crash_parser.py --live
"""
import subprocess, re, sys, zipfile, json, argparse
from datetime import datetime
from pathlib import Path

CRASH_PATTERNS = [
    (r'FATAL EXCEPTION: (.+)', 'Exception'),
    (r'E/(.+): (.*Exception.*)', 'LogException'),
    (r'Application (.+) \(pid \d+\) has stopped', 'Crash'),
    (r'ANR in (.+)', 'ANR'),
]

def parse_crash(text):
    crashes = []
    current = None
    for line in text.splitlines():
        # Detect crash start
        for pattern, crash_type in CRASH_PATTERNS:
            m = re.search(pattern, line)
            if m:
                if current:
                    crashes.append(current)
                current = {
                    'type': crash_type,
                    'app': m.group(1) if m.groups() else '?',
                    'time': datetime.now().isoformat(),
                    'stack': [],
                    'message': m.group(2) if len(m.groups()) > 1 else '',
                }
                break
        
        # Collect stack trace
        if current and (line.startswith('\tat ') or 'Exception' in line):
            current['stack'].append(line.strip())

    if current:
        crashes.append(current)
    return crashes

def format_crash(crash):
    output = f"\n{'━'*60}\n"
    output += f"🔴 {crash['type']} — {crash['app']}\n"
    output += f"   Time: {crash['time']}\n"
    if crash['message']:
        output += f"   Message: {crash['message'][:80]}\n"
    if crash['stack']:
        output += f"\n   Stack trace:\n"
        for line in crash['stack'][:10]:
            output += f"     {line[:70]}\n"
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bugreport", nargs='?', help="bugreport.zip file")
    parser.add_argument("--live", action="store_true", help="Parse live logcat")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--app", help="Filter by app name")
    args = parser.parse_args()

    if args.live:
        print("🔴 Parsing live logcat (Ctrl+C to stop)...\n")
        try:
            proc = subprocess.Popen("adb logcat", shell=True, stdout=subprocess.PIPE, text=True)
            buffer = ""
            for line in proc.stdout:
                buffer += line
                if re.search(r'(Exception|ANR|FATAL)', line):
                    # Flush crashes so far
                    crashes = parse_crash(buffer)
                    for c in crashes:
                        if not args.app or args.app.lower() in c['app'].lower():
                            if args.json:
                                print(json.dumps(c))
                            else:
                                print(format_crash(c))
                    buffer = ""
        except KeyboardInterrupt:
            print("\n✓ Stopped")
        return

    if not args.bugreport:
        parser.print_help()
        sys.exit(1)

    # Parse bugreport
    try:
        with zipfile.ZipFile(args.bugreport) as z:
            for name in z.namelist():
                if 'log' in name.lower():
                    with z.open(name) as f:
                        text = f.read().decode('utf-8', errors='ignore')
                        breaks = parse_crash(text)
                        for crash in breaks:
                            if not args.app or args.app.lower() in crash['app'].lower():
                                if args.json:
                                    print(json.dumps(crash))
                                else:
                                    print(format_crash(crash))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
