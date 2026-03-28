# 💥 Android Crash Reporter

Capture and parse Android crashes and ANRs from any device via ADB.

## Tools
| Script | What it does |
|--------|-------------|
| `crash_watcher.py` | Live crash monitor — prints stack traces as they happen |
| `anr_dump.py` | Pull and parse ANR traces from /data/anr/ |
| `crash_report.py` | Generate a crash report from logcat history |

## Quick start
```bash
python3 crash_watcher.py                    # watch for any crash
python3 crash_watcher.py --app com.example  # watch specific app
python3 anr_dump.py --output anr_report.txt
```
