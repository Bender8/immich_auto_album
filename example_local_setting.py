# --- IMMICH CONNECTION SETTINGS ---
# Base URL of your Immich instance (e.g., "http://192.168.1.28:2283").
IMMICH_BASE_URL: str = "http://localhost:2283"

# API Key generated from Immich User Settings.
API_KEY: str = "YOUR_API_KEY_HERE"

# Maximum simultaneous API requests (higher is faster, but may stress the server).
MAX_CONCURRENT_REQUESTS: int = 4

# --- SYNC_CONFIGS SETUP ---
# Each entry creates or updates an Immich Album based on "Sync Rules."
# Rules use keys from the Immich Search API: https://api.immich.app/endpoints/search/searchAssets

# CONFIGURATION GUIDE:
# 1. 'name': The album name (will be created automatically if missing).
# 2. 'filters': A list of conditions. Assets must pass ALL filters to be added (AND logic).
# 3. 'key' & 'val': The metadata field and the value to match (e.g., "type": "VIDEO").
# 4. 'people': Use the Display Name from the Immich Web UI (e.g., "John Doe"), NOT the UUID.
# 5. 'match_all' (Optional):
#    - False (Default): OR logic. Adds photo if ANY listed person is present.
#    - True: AND logic. Adds photo only if EVERY listed person is present.

# SPECIAL CASE: "val": None
# Using "key": "people" with "val": None creates an album of photos with no face tags.
# This is useful for finding untagged people or filtering for landscapes/objects.

SYNC_CONFIGS = [
    # Example 1: Simple Boolean filter (Favorites)
    {"name": "Favorites-Auto", "filters": [{"key": "isFavorite", "val": True}]},
    # Example 2: Simple Attribute filter (All Videos)
    {"name": "All-Videos-Auto", "filters": [{"key": "type", "val": "VIDEO"}]},
    # Example 3: Find photos with NO people tagged (Landscapes/Objects/Untagged)
    {"name": "Things-Auto", "filters": [{"key": "people", "val": None}]},
    # Example 4: OR logic (Includes photos of Person A, Person B, OR Person C)
    {
        "name": "Family-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B", "Person C"], "match_all": False},
        ],
    },
    # Example 5: AND logic (Only includes photos where Person A AND Person B are together)
    {
        "name": "Couple-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B"], "match_all": True},
        ],
    },
    # Example 6: Complex Multi-filter (Specific people AND must be a video)
    {
        "name": "Family-Videos-Auto",
        "filters": [
            {"key": "people", "val": ["Person A", "Person B", "Person C"], "match_all": False},
            {"key": "type", "val": "VIDEO"},
        ],
    },
]
