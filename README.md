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
(This section will detail how to configure the tool. It will cover parameters like the Immich API key, server URL, and most importantly, the structure for defining album creation rules based on metadata.)

```yaml
# Example configuration snippet (concept)
immich:
  url: "https://your-immich-instance.com"
  api_key: "YOUR_IMMICH_API_KEY"

albums:
  - name_pattern: "Year/Month - {year}-{month}"
    rules:
      - metadata_field: "creationDate"
        group_by: "month"
  - name_pattern: "Camera - {cameraModel}"
    rules:
      - metadata_field: "exif.make"
      - metadata_field: "exif.model"
```

## Contributing
We welcome contributions to `immich_auto_album`! If you'd like to contribute, please refer to our contributing guidelines (which will be in a `CONTRIBUTING.md` file) for details on how to set up your development environment, run tests, and submit pull requests.

## Licensing
This project is licensed under the MIT License - see the `LICENSE` file for details.
