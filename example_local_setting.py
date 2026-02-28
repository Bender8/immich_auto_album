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

# CONFIGURATION GUIDE:
# 1. 'name': The album name (will be created automatically if missing).
# 2. 'filters': A list of conditions. Assets must pass ALL filters to be added (AND logic).
# 3. 'key' & 'val': The metadata field and the value to match (e.g., "type": "VIDEO").
# 4. 'people': Use the Display Name from the Immich Web UI (e.g., "John Doe"), NOT the UUID.
# 5. 'operator' (Optional - Case Insensitive):
#    - "OR" (Default): Adds photo if AT LEAST ONE listed value matches.
#    - "AND": Adds photo only if EVERY listed value is present.
#    - "NOT": Adds photo only if NONE of the listed values are present.
#    - "ONLY": Adds photo only if the metadata matches your list EXACTLY (no others allowed).

# SPECIAL CASE: "val": None
# Using "key": "people" with "val": None finds photos with no face tags.
# If used with "operator": "NOT", it finds photos that HAVE at least one face tag.

SYNC_CONFIGS = [
    # Example 1: Simple Boolean Filter (Favorites)
    {"name": "Favorites-Auto", "filters": [{"key": "isFavorite", "val": True, "operator": "OR"}]},
    # Example 2: Attribute Filter (Exclude Videos)
    {"name": "Photos-Only-Auto", "filters": [{"key": "type", "val": "VIDEO", "operator": "NOT"}]},
    # Example 3: Find photos with NO people tagged (Landscapes/Objects/Untagged)
    {"name": "Things-Auto", "filters": [{"key": "people", "val": None, "operator": "OR"}]},
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
    # Example 7: Complex Multi-filter (Specific people AND must be a favorite AND NOT a video)
    {
        "name": "Best-Family-Moments-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "operator": "OR"},
            {"key": "isFavorite", "val": True, "operator": "OR"},
            {"key": "type", "val": "VIDEO", "operator": "NOT"},
        ],
    },
]
