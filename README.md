# Immich Auto-Album Sync

An asynchronous Python script to create declarative "Smart Albums" in Immich. The script syncs assets into albums based on flexible metadata rules (People, Favorites, Asset Type, etc.) and is designed to run as a recurring cron job.

---

## Features

- Fast & Asynchronous: Uses `aiohttp` and `asyncio` to process thousands of assets quickly.
- Smart Logic: Supports flexible operators (`AND`, `OR`, `NOT`, `ONLY`) for precise filtering.
- Multi-filter Support: Combine rules (e.g., "Favorite Videos of Person A").
- Declarative Sync: Automatically adds matching assets and removes those that no longer match.
- Safe Execution: Concurrency semaphores prevent overwhelming your Immich server.
- Logging & Rotation: Built-in log rotation suitable for 6-hour cron intervals.

---

## Requirements

- Python 3.10+
- An Immich instance (v2.x recommended)
- An API Key (Generated in Immich under Account Settings → API Keys)

---

## Installation

1. Clone the repository:
```immich_auto_album/README.md#L201-204
git clone https://github.com/<your-org>/immich-auto-album.git
```

2. Change into the project directory:
```immich_auto_album/README.md#L205-206
cd immich-auto-album
```

3. Install dependencies:
```immich_auto_album/README.md#L207-208
pip install aiohttp
```

---

## Configuration

1. Copy the example settings file and fill in your details:
```immich_auto_album/README.md#L212-213
cp example_local_settings.py local_settings.py
```

2. Edit `local_settings.py` and set:
- `IMMICH_BASE_URL` — your Immich server base URL (e.g. `https://immich.example.com`)
- `API_KEY` — API key created in Immich
- `SYNC_CONFIGS` — a list of declarative album configs (examples below)
- Email Configuration (Optional, for error notifications):
    - `ENABLE_EMAIL_ON_ERROR` — set to `True` to enable email notifications on unhandled errors.
    - `EMAIL_SMTP_SERVER` — SMTP server address (e.g., `smtp.gmail.com`).
    - `EMAIL_SMTP_PORT` — SMTP server port (e.g., `465` for SSL).
    - `EMAIL_USERNAME` — Your email username (often your full email address).
    - `EMAIL_PASSWORD` — Your email password or app-specific password. **Highly recommended to use an app-specific password for security.**
    - `EMAIL_FROM` — The sender email address.
    - `EMAIL_TO` — The recipient email address for error notifications.

Minimal `local_settings.py` example:
```immich_auto_album/README.md#L214-229
# local_settings.py
IMMICH_BASE_URL = "https://immich.example.com"
API_KEY = "your_api_key_here"

# Optional: Email error notifications
ENABLE_EMAIL_ON_ERROR = False  # Set to True to enable
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 465
EMAIL_USERNAME = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use an app-specific password!
EMAIL_FROM = "immich-auto-album@example.com"
EMAIL_TO = "your_admin_email@example.com"

# Example of a SYNC_CONFIGS entry:
SYNC_CONFIGS = [
    {
        "name": "Family",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "operator": "OR"}
        ],
    },
]
```

---

## Configuration Examples

Simple "OR" Filter — Finds any photo containing Person A or Person B:
```immich_auto_album/README.md#L230-235
{
  "name": "Family",
  "filters": [
    {
      "key": "people",
      "val": ["Person A", "Person B"],
      "operator": "OR"
    }
  ]
}
```

Strict "AND" Filter — Only finds photos where Person A and Person B are together:
```immich_auto_album/README.md#L236-241
{
  "name": "Couple",
  "filters": [
    {
      "key": "people",
      "val": ["Person A", "Person B"],
      "operator": "AND"
    }
  ]
}
```

Exclusive "ONLY" Filter — Only finds photos containing *exactly* Person A and Person B, and no one else:
```immich_auto_album/README.md#L85-94
{
  "name": "Only Us",
  "filters": [
    {
      "key": "people",
      "val": ["Person A", "Person B"],
      "operator": "ONLY"
    }
  ]
}
```

Exclusion "NOT" Filter — Finds photos that do NOT contain Person C:
```immich_auto_album/README.md#L95-104
{
  "name": "No Person C",
  "filters": [
    {
      "key": "people",
      "val": ["Person C"],
      "operator": "NOT"
    }
  ]
}
```

Untagged / Landscapes — Finds photos with no faces detected (useful for troubleshooting missing face tags):
```immich_auto_album/README.md#L242-247
{
  "name": "Things",
  "filters": [
    {
      "key": "people",
      "val": null
    }
  ]
}
```

You can combine multiple filters in a single album config. For example, "Favorite Videos of Person A":
```immich_auto_album/README.md#L248-256
{
  "name": "Person A - Favorite Videos",
  "filters": [
    {"key": "people", "val": ["Person A"], "operator": "OR"},
    {"key": "is_favorite", "val": true},
    {"key": "asset_type", "val": "video"}
  ]
}
```

Supported filter keys (examples):
- `people` — list of person names or `null` for no faces
- `is_favorite` — boolean
- `asset_type` — `"photo"` or `"video"`

Supported operators:
- `OR` (default) — asset matches at least one value in `val`
- `AND` — asset matches all values in `val`
- `NOT` — asset matches none of the values in `val`
- `ONLY` — asset matches exactly the values in `val` and no others

---

## Running & Automation (Cron)

To keep your albums in sync every 6 hours, add an entry to your crontab (run `crontab -e`):
```immich_auto_album/README.md#L257-260
0 */6 * * * /usr/bin/python3 /path/to/immich_sync.py >> /path/to/immich_sync.log 2>&1
```

Notes:
- Use absolute paths for the Python interpreter and the script.
- Redirect logs to a file that is rotated regularly (the script has built-in rotation options).

---

## Logging

- The script supports configurable log rotation; defaults are tuned for a 6-hour run interval.
- Check the log file referenced in your cron job (`immich_sync.log` in the example above) for errors and operational information.

---

## Safety & Performance

- The script uses semaphores to limit concurrent requests and avoid overloading the Immich API.
- It processes assets asynchronously and supports batching for efficient syncs.
- Always test with a small `SYNC_CONFIGS` entry before enabling wide syncs.

---

## Development & Contributing

- If you want additional filter keys or behaviors, open an issue or submit a PR.
- Add unit tests for new features where possible.
- Keep configuration declarative and documented in `example_local_settings.py`.


## License

This project is available under the MIT License — free to use and modify.

---
