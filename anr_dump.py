#!/usr/bin/env python3
"""
anr_dump.py -- Pull and parse ANR (App Not Responding) traces from Android device
Requires root or Shizuku for /data/anr/ access, OR uses dumpsys for basic ANR info.
Usage: python3 anr_dump.py [--output anr_report.txt]
"""
import subprocess, re, argparse
from datetime import datetime

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout

def pull_anr_traces():
    # Try to pull ANR traces (needs root or Shizuku)
    result = subprocess.run("adb pull /data/anr/traces.txt /tmp/anr_traces.txt",
        shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        with open('/tmp/anr_traces.txt') as f:
            return f.read()
    # Fallback: dumpsys activity
    return adb("dumpsys activity processes | grep -A 5 'ANR'")

def parse_anr(raw):
    anrs = []
    current = {}
    for line in raw.splitlines():
        pkg_m = re.search(r'Process: (\S+)', line)
        pid_m = re.search(r'PID: (\d+)', line)
        reason_m = re.search(r'Reason: (.+)', line)
        if pkg_m: current['pkg'] = pkg_m.group(1)
        if pid_m: current['pid'] = pid_m.group(1)
        if reason_m:
            current['reason'] = reason_m.group(1)
            anrs.append(dict(current))
            current = {}
    return anrs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Save report to file")
    args = parser.parse_args()

    print("📊 Pulling ANR traces...")
    raw = pull_anr_traces()
    anrs = parse_anr(raw)

    print(f"\nFound {len(anrs)} ANR record(s)\n")
    lines = []
    for a in anrs:
        line = f"  [{a.get('pkg','unknown')}] PID={a.get('pid','?')} — {a.get('reason','?')}"
        print(line)
        lines.append(line)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"ANR Report — {datetime.now()}\n{'='*50}\n")
            f.write("\n".join(lines))
        print(f"\n✅ Saved to {args.output}")

if __name__ == "__main__":
    main()
