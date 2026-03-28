#!/usr/bin/env python3
"""
crash_watcher.py -- Real-time Android crash and ANR monitor
Watches logcat and extracts full stack traces when a crash occurs.
Usage: python3 crash_watcher.py [--app com.example.pkg] [--output crashes.log]
"""
import subprocess, re, argparse, sys
from datetime import datetime

CRASH_TRIGGERS = [
    "FATAL EXCEPTION",
    "AndroidRuntime",
    "Force finishing activity",
    "am_crash",
    "am_anr",
]

def watch(filter_pkg=None, output_file=None):
    print("\n💥 Android Crash Watcher — press Ctrl+C to stop")
    if filter_pkg:
        print(f"   Filtering: {filter_pkg}")
    print()

    proc = subprocess.Popen(
        "adb logcat -v threadtime",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1
    )

    capturing = False
    buffer = []
    crash_count = 0
    log_f = open(output_file, 'a') if output_file else None

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break

            # Start capture on crash trigger
            triggered = any(t in line for t in CRASH_TRIGGERS)
            if triggered:
                if filter_pkg and filter_pkg not in line:
                    # peek at next lines for pkg
                    buffer = [line]
                    capturing = True
                else:
                    capturing = True
                    buffer = [line]
                    crash_count += 1
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"\n{'='*60}")
                    print(f"💥 CRASH #{crash_count} at {ts}")
                    print(f"{'='*60}")

            if capturing:
                buffer.append(line)
                # Print stack trace lines
                if "at " in line or "Caused by:" in line or "Exception" in line:
                    print(f"  {line.rstrip()}")

                # Stop after blank line or new log section
                if len(buffer) > 5 and line.strip() == "":
                    if log_f:
                        log_f.writelines(buffer)
                        log_f.flush()
                    capturing = False
                    buffer = []
                    print(f"\n[Crash #{crash_count} captured]")

    except KeyboardInterrupt:
        print(f"\n\nStopped. Caught {crash_count} crash(es).")
    finally:
        proc.terminate()
        if log_f:
            log_f.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Filter by package name")
    parser.add_argument("--output", help="Save crashes to log file")
    args = parser.parse_args()
    watch(args.app, args.output)

if __name__ == "__main__":
    main()
