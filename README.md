# immich_auto_album

## Overview
`immich_auto_album` is designed to automate the creation and management of albums within Immich based on the metadata embedded in your media files. This helps in organizing large photo and video collections effortlessly, ensuring your albums are always up-to-date and reflect your preferred categorization logic without manual intervention.

## Features
- **Metadata-driven Album Creation**: Automatically creates Immich albums using various metadata fields from your media (e.g., date, camera model, lens, location data, custom tags, etc.).
- **Customizable Rules**: Define flexible, user-friendly rules to specify how albums should be named and what criteria should be used for grouping assets. This allows for highly personalized album structures.
- **Incremental Processing**: Efficiently processes new or updated media files, adding them to relevant albums without the need to re-process the entire library every time.
- **Idempotent Operations**: Designed to be run repeatedly without unintended side effects, such as creating duplicate albums or redundant entries.
- **Command-line Interface (CLI)**: Provides an easy-to-use command-line interface, making it simple to integrate into automation scripts, cron jobs, or other workflows.

## How It Works
The `immich_auto_album` tool connects to your self-hosted Immich instance using the provided API key and server URL. It then fetches information about your assets, including their embedded metadata. Based on the rules defined in your configuration, it identifies which assets belong to which albums. The tool then either creates new albums in Immich or updates existing ones by adding the relevant assets. Its incremental processing logic ensures that only necessary changes are applied, minimizing API calls and processing time.

## Installation
(Details on how to install the tool will go here. This might include options like `pip install`, cloning the repository, or using Docker.)

## Usage
(Examples of how to run the tool will be provided here, including basic commands, specifying a configuration file, and using the preview mode.)

```bash
# Example usage:
# immich_auto_album --config my_config.yaml
# immich_auto_album --config my_config.yaml --preview
```

## Configuration
The `immich_auto_album` tool is configured through a `local_setting.py` file (you can copy `example_local_setting.py` and rename it to `local_setting.py`). This file contains essential parameters for connecting to your Immich instance and defining your album synchronization rules.

Here are the key configuration variables:

- `IMMICH_BASE_URL`: The URL to your Immich instance.
    ```C:/Users/jadeb/Documents/Github/immich_auto_album/example_local_setting.py#L1
    IMMICH_BASE_URL: str = "http://localhost:2283" # Example: "http://192.168.1.28:2283"
    ```
- `API_KEY`: Your API key obtained from your Immich account settings.
    ```C:/Users/jadeb/Documents/Github/immich_auto_album/example_local_setting.py#L2
    API_KEY: str = "YOUR_API_KEY_HERE"
    ```
- `MAX_CONCURRENT_REQUESTS`: The maximum number of concurrent API requests the tool will make to Immich.
    ```C:/Users/jadeb/Documents/Github/immich_auto_album/example_local_setting.py#L3
    MAX_CONCURRENT_REQUESTS: int = 4
    ```
- `SYNC_CONFIGS`: A list of dictionaries, where each dictionary defines a "Sync Rule" for album creation. Albums that do not exist will be automatically created.

    Each sync rule dictionary has the following format:
    `{"name": "Album Name", "key": "Search Field Name", "val": "matching data in field"}`

    - `name`: The name of the album to be created or updated in Immich.
    - `key`: The Immich asset search field to use for matching. Possible values for `key` can be found in the Immich API documentation (e.g., [https://api.immich.app/endpoints/search/searchAssets](https://api.immich.app/endpoints/search/searchAssets)).
    - `val`: The value to match against the specified `key`.

    **Special Considerations for `people` key:**
    When using `"key": "people"`, the `val` can be `None` to find photos without faces, or a list of person names (strings). Use the exact names of people as they appear in the "Explore People" section of the Immich web UI (e.g., "John Doe"). If `val` is a list of names, photos will be added to the album if *any* of the listed people are present in the photo.

    Here's an example of `SYNC_CONFIGS` from `example_local_setting.py`:

    ```C:/Users/jadeb/Documents/Github/immich_auto_album/example_local_setting.py#L17-38
    SYNC_CONFIGS = [
        {"name": "Favorites", "key": "isFavorite", "val": True},
        {"name": "All-Videos", "key": "type", "val": "VIDEO"},
        {"name": "Things", "key": "people", "val": None},
        {
            "name": "Kids",
            "key": "people",
            "val": ["kid1", "kid2"],
        },
        {
            "name": "Family",
            "key": "people",
            "val": ["person1", "person2", "person3", "person4"],
        },
        {
            "name": "Friends",
            "key": "people",
            "val": ["friend1", "friend2", "friend3", "friend4", "friend5", "friend6"],
        },
    ]
    ```

## Contributing
We welcome contributions to `immich_auto_album`! If you'd like to contribute, please refer to our contributing guidelines (which will be in a `CONTRIBUTING.md` file) for details on how to set up your development environment, run tests, and submit pull requests.

## Licensing
This project is licensed under the MIT License - see the `LICENSE` file for details.
