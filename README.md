# 💥 Android Crash Reporter

Parse crashes and ANRs from Android logcat or bugreport files.

## Usage

```bash
# Parse bugreport
python3 crash_parser.py bugreport.zip

# Live logcat monitoring
adb logcat | python3 crash_parser.py --live

# Filter by app
python3 crash_parser.py bugreport.zip --app com.example.app

# JSON output
python3 crash_parser.py bugreport.zip --json
```

Extracts: crash type, app name, timestamp, exception message, and stack trace (first 10 frames).
