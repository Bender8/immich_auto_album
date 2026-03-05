# --- IMMICH CONNECTION SETTINGS ---
# Base URL of your Immich instance (e.g., "http://192.168.1.28:2283").
IMMICH_BASE_URL: str = "http://localhost:2283"

# API Key generated from Immich User Settings. -> API Keys.
API_KEY: str = "YOUR_API_KEY_HERE"

# Maximum simultaneous API requests (higher is faster, but increases server load).
MAX_CONCURRENT_REQUESTS: int = 4

# Email on error configuration
ENABLE_EMAIL_ON_ERROR: bool = True  # Set to True to enable sending emails
# Gmail SMTP settings (for Gmail use smtp.gmail.com and port 465 with SSL)
# NOTE: For Gmail you should use an app password (not your account password).
EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
EMAIL_SMTP_PORT: int = 465  # SSL port
EMAIL_USERNAME: str = "your.email@gmail.com"  # Gmail address
EMAIL_PASSWORD: str = "your_app_password"  # Use an app password
EMAIL_FROM: str = EMAIL_USERNAME
EMAIL_TO: str = "recipient@example.com"

# --- SYNC_CONFIGS SETUP ---
# Each entry creates or updates an Immich Album based on "Sync Rules."
# Rules use keys from the Immich Search API: https://api.immich.app/endpoints/search/searchAssets
# Example of metadata used for filtering below shown at end of this file.

# CONFIGURATION GUIDE:
# 1. 'name': The album name (will be created automatically if missing).
# 2. 'filters': A list of conditions. Assets must pass ALL filters to be added (AND logic).
# #3. 'key' & 'val': The metadata field and the value to match (e.g., "type": "VIDEO").
#    - For date filters ('BEFORE', 'AFTER'), 'val' MUST be a string in "YYYY-MM-DD" format.
#      This is important as it differs from common US date formats (e.g., MM-DD-YYYY).
# 4. 'people': Use the Display Name from the Immich Web UI (e.g., "John Doe"), NOT the UUID.
# 5. 'operator' (Optional - Case Insensitive):
#    - "OR" (Default): Adds photo if AT LEAST ONE listed value matches.
#    - "AND": Adds photo only if EVERY listed value is present.
#    - "NOT": Adds photo only if NONE of the listed values are present.
#    - "ONLY": Adds photo only if the metadata matches your list EXACTLY (no others allowed).
#    - "ONLY_ANY": Adds photo only if AT LEAST ONE listed value matches but no others are allowed.
#    - "BEFORE": Adds photo only if the date is before the specified value.
#    - "AFTER": Adds photo only if the date is after the specified value.

# SPECIAL CASE: "val": None
# Using "key": "people" with "val": None finds photos with no face tags.
# If used with "operator": "NOT", it finds photos that HAVE at least one face tag.

SYNC_CONFIGS = [
    # Example 1: Simple Boolean Filter (Favorites)
    {"name": "Favorites-Auto", "filters": [{"key": "isFavorite", "val": True}]},
    # Example 2: Attribute Filter (Exclude Videos)
    {"name": "Photos-Only-Auto", "filters": [{"key": "type", "val": "VIDEO", "operator": "NOT"}]},
    # Example 3: Find photos with NO people tagged (Landscapes/Objects/Untagged)
    {"name": "Things-Auto", "filters": [{"key": "people", "val": None}]},
    # Example 4: OR Logic (Includes photos of Person A, Person B, OR Person C)
    {
        "name": "Family-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B", "Person C"], "operator": "OR"},
        ],
    },
    # Example 5: AND Logic (Only includes photos where Person A AND Person B are together)
    {
        "name": "Couple-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "operator": "AND"},
        ],
    },
    # Example 6: ONLY Logic (Photos of Person A where NO ONE ELSE is present)
    {
        "name": "Just-Person-A-Auto",
        "filters": [
            {"key": "people", "val": ["Person A"], "operator": "ONLY"},
        ],
    },
    # Example 7: ONLY_ANY Logic (Only includes photos where Person A or Person B or Person C is present and no one else)
    {
        "name": "Couple-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B", "Person C"], "operator": "ONLY_ANY"},
        ],
    },
    # Example 8: Complex Multi-filter (Specific people AND must be a favorite AND NOT a video)
    {
        "name": "Best-Family-Moments-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "operator": "OR"},
            {"key": "isFavorite", "val": True},
            {"key": "type", "val": "VIDEO", "operator": "NOT"},
        ],
    },
    # Example 9: Date Range Filter (Photos taken between two dates)
    {
        "name": "Person A - 2023",
        "filters": [
            {"key": "people", "val": ["Person A"], "operator": "OR"},
            {"key": "fileCreatedAt", "val": "2022-12-31", "operator": "AFTER"},
            {"key": "fileCreatedAt", "val": "2024-01-01", "operator": "BEFORE"},
        ],
    },
]

# Example of metadata used for filtering below:
# {
# "id": "6418c37d-35b0-4011-882d-36946bc00eb7",
# "createdAt": "2026-01-20T15:23:58.024Z",
# "deviceAssetId": "cc2479e3-2d66-483c-8ad9-187b237d891d.jpg-1779462",
# "ownerId": "6bbe2767-7851-461a-aa2d-afbd3460aa85",
# "deviceId": "CLI",
# "libraryId": null,
# "type": "IMAGE",
# "originalPath": "/data/upload/6bbe2767-7851-461a-aa2d-afbd3460aa85/19/eb/19eb57f1-adf2-4f40-abbd-10412d55a70f.jpg",
# "originalFileName": "cc2479e3-2d66-483c-8ad9-187b237d891d.jpg",
# "originalMimeType": "image/jpeg",
# "thumbhash": "JggiBoCHeIePeIiFd3h3iIeIAAAAAAA=",
# "fileCreatedAt": "2025-04-30T00:13:05.000Z",
# "fileModifiedAt": "2025-05-01T14:27:18.591Z",
# "localDateTime": "2025-04-30T00:13:05.000Z",
# "updatedAt": "2026-03-02T00:19:21.409Z",
# "isFavorite": false,
# "isArchived": false,
# "isTrashed": false,
# "visibility": "timeline",
# "duration": "0:00:00.00000",
# "livePhotoVideoId": null,
# "people": [],
# "unassignedFaces": [],
# "checksum": "aVw2iQTS44pAOPYMVkWZrd4TIpA=",
# "isOffline": false,
# "hasMetadata": true,
# "duplicateId": null,
# "resized": true,
# "width": 4537,
# "height": 3648,
# "isEdited": false
# }
