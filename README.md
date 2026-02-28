# Immich Auto-Album Sync

An asynchronous Python script to create declarative "Smart Albums" in Immich. The script syncs assets into albums based on flexible metadata rules (People, Favorites, Asset Type, etc.) and is designed to run as a recurring cron job.

---

## Features

- Fast & Asynchronous: Uses `aiohttp` and `asyncio` to process thousands of assets quickly.
- Smart Logic: Supports both "AND" (all people present) and "OR" (any of these people) filtering.
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

Minimal `local_settings.py` example:
```immich_auto_album/README.md#L214-229
# local_settings.py
IMMICH_BASE_URL = "https://immich.example.com"
API_KEY = "your_api_key_here"

# Example of a SYNC_CONFIGS entry:
SYNC_CONFIGS = [
    {
        "name": "Family",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "match_all": False}
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
      "match_all": false
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
      "match_all": true
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
    {"key": "people", "val": ["Person A"], "match_all": false},
    {"key": "is_favorite", "val": true},
    {"key": "asset_type", "val": "video"}
  ]
}
```

Supported filter keys (examples):
- `people` — list of person names or `null` for no faces
- `is_favorite` — boolean
- `asset_type` — `"photo"` or `"video"`
- (Extendable — check script docs or source for additional keys)

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

---

## FAQ

Q: How do I know what person names to use in `people`?
A: Use the exact display names used in Immich's face tags. If in doubt, export or inspect Immich tagging data via the API or the web UI.

---

## License

This project is available under the MIT License — free to use and modify.

---
