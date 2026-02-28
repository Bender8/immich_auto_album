IMMICH_BASE_URL: str = (
    "http://localhost:2283"  # URL to your Immich instance. ex. "http://192.168.1.28:2283"
)
API_KEY: str = "YOUR_API_KEY_HERE"  # Your API key from Immich
MAX_CONCURRENT_REQUESTS: int = 4

# A list of dictionaries defining"Sync Rules"
# Format: {"name": "Album Name", "key": "Search Field Name", "val": "matching data in feild", "match_all": False}
# Possible values for "key" can be found here: https://api.immich.app/endpoints/search/searchAssets
# Albums that do not exist will automatically be created
# If you want to create albums by a list of one or more people examples are shown below.
# Use the names of people you have labled not their UUID, for example use "John" or "John Doe"
# Make sure people names are listed exactly as they are when you Explore People from the web UI
# You can list as many people as you want
# If Match_all is set to False photos will be added if any of the people listed are in the photo
# If Match_all is set to True photos will be added only if all people listed are in the photo
# If Match_all is missing the defualt behavior of Match_all is false
# an example called "Things" is also shown below. This will create an album of photos without faces
# an album of all photos without faces can be useful for finding photos with missing face tags
# I also like to use this album quickly find technical photos related to projects where the seach function isn't very good

SYNC_CONFIGS = [
    {"name": "Favorites", "key": "isFavorite", "val": True},
    {"name": "All-Videos", "key": "type", "val": "VIDEO"},
    {"name": "Things", "key": "people", "val": None},
    {"name": "Kids", "key": "people", "val": ["kid1", "kid2"], "match_all": False},
    {
        "name": "Family",
        "key": "people",
        "val": ["person1", "person2", "person3", "person4"],
        "match_all": True,
    },
    {
        "name": "Friends",
        "key": "people",
        "val": ["friend1", "friend2", "friend3", "friend4", "friend5", "friend6"],
        "match_all": False,
    },
]
