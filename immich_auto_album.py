import asyncio
from typing import Any

import aiohttp

# Configuration load
try:
    from local_settings import (
        API_KEY,
        IMMICH_BASE_URL,
        MAX_CONCURRENT_REQUESTS,
        SYNC_CONFIGS,
    )
except ImportError:
    print("❌ ERROR: local_settings.py not found!")
    exit(1)

# Safety check for URL trailing slashes
IMMICH_BASE_URL: str = IMMICH_BASE_URL.rstrip("/")
# -----------------------------------------------------------------------------


async def fetch_page(
    session: aiohttp.ClientSession, page: int, sem: asyncio.Semaphore
) -> list[dict]:
    """Fetches a single page. Returns empty list if 404 or no items."""
    url: str = f"{IMMICH_BASE_URL}/api/search/metadata"
    payload: dict = {"withPeople": True, "size": 1000, "page": page}

    async with sem:
        try:
            async with session.post(url, json=payload, timeout=30) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                # Use .get() chains to safely reach the items list
                return data.get("assets", {}).get("items", [])
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            return []


async def pull_all_immich_metadata(session: aiohttp.ClientSession) -> dict[str, Any]:
    """
    Fetches assets in concurrent batches until an empty page is hit.
    This bypasses the unreliable 'total' field in Immich v2.5.6.
    """
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    all_items: list[dict] = []
    page = 1
    keep_going = True

    print(f"Starting metadata pull (Batch size: {MAX_CONCURRENT_REQUESTS})...")

    while keep_going:
        # Create a batch of tasks (e.g., pages 1-5, then 6-10)
        batch_range = range(page, page + MAX_CONCURRENT_REQUESTS)
        tasks = [fetch_page(session, p, sem) for p in batch_range]

        results = await asyncio.gather(*tasks)

        for page_items in results:
            if not page_items:
                keep_going = False
                break
            all_items.extend(page_items)

        if keep_going:
            page += MAX_CONCURRENT_REQUESTS
            # print(f"Downloaded {len(all_items)} assets so far...")

    print(f"Finished. Total assets retrieved: {len(all_items)}")
    return {"assets": {"items": all_items}}


async def get_or_create_album(session: aiohttp.ClientSession, name: str) -> str:
    """Finds or creates an album using the shared session."""
    url: str = f"{IMMICH_BASE_URL}/api/albums"
    async with session.get(url) as response:
        response.raise_for_status()
        albums = await response.json()
        for album in albums:
            if album.get("albumName") == name:
                return str(album["id"])

    async with session.post(url, json={"albumName": name}) as response:
        response.raise_for_status()
        new_album = await response.json()
        return str(new_album["id"])


def get_asset_ids_by_filter(
    metadata_dict: dict, filter_key: str, filter_value: Any
) -> list[str]:
    """Extracts asset IDs based on metadata criteria."""
    assets = metadata_dict.get("assets", {}).get("items", [])
    # 1. Handle "None" (Things/No People)
    if filter_value is None:
        return [a["id"] for a in assets if not a.get(filter_key) and "id" in a]
    # 2. NEW: Handle a List of UUIDs (People)
    if isinstance(filter_value, list):
        results: list[str] = []
        for a in assets:
            # Get the list of people objects for this asset
            people_on_photo = a.get(filter_key, [])  # Usually a list of dicts
            # Extract just the IDs from those objects
            photo_person_ids = [p.get("id") for p in people_on_photo]
            # If ANY of our target UUIDs are in the photo's person list
            if any(target_id in photo_person_ids for target_id in filter_value):
                results.append(a["id"])
        return results
    # 3. Handle strict matches (isFavorite, type, etc.)
    return [a["id"] for a in assets if a.get(filter_key) == filter_value and "id" in a]


async def get_current_album_asset_ids(
    session: aiohttp.ClientSession, album_id: str
) -> list[str]:
    """Retrieves all asset IDs currently inside a specific album."""
    url: str = f"{IMMICH_BASE_URL}/api/albums/{album_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        current_album_data = await response.json()
        return [asset["id"] for asset in current_album_data.get("assets", [])]


async def get_people_lookup(session: aiohttp.ClientSession) -> dict[str, str]:
    """Creates a mapping of { 'Person Name': 'uuid' } from Immich."""
    url: str = f"{IMMICH_BASE_URL}/api/people"
    async with session.get(url) as response:
        response.raise_for_status()
        people_data = await response.json()
        # We use .lower() to make the lookup case-insensitive
        # Note: people_data['people'] is the list in Immich v1.115+
        people_list = people_data.get("people", [])
        return {p["name"].lower(): p["id"] for p in people_list if p.get("name")}


def resolve_names_to_uuids(
    target_names: list[str], lookup: dict[str, str]
) -> list[str]:
    """Converts a list of names to UUIDs using the lookup table."""
    uuids = []
    for name in target_names:
        clean_name = name.lower().strip()
        if clean_name in lookup:
            uuids.append(lookup[clean_name])
        else:
            print(
                f"⚠️ WARNING: Could not find person '{name}'. Is the spelling correct in Immich?"
            )
    return uuids


async def add_assets_to_album(
    session: aiohttp.ClientSession, album_id: str, asset_ids: list[str]
) -> bool:
    """
    Adds a list of asset IDs to a specific album.
    Chunks the input to ensure stability with large datasets.
    """
    if not asset_ids:
        print(f"No assets to add to album {album_id}.")
        return False
    url: str = f"{IMMICH_BASE_URL}/api/albums/{album_id}/assets"
    chunk_size = 2000  # Safe limit for most reverse proxies
    # Split list into manageable chunks
    for i in range(0, len(asset_ids), chunk_size):
        chunk = asset_ids[i : i + chunk_size]
        payload = {"ids": chunk}
        async with session.put(url, json=payload) as response:
            if response.status not in (200, 201):
                print(f"Failed to add assets: {await response.text()}")
                return False
    return True


async def remove_assets_from_album(
    session: aiohttp.ClientSession, album_id: str, asset_ids: list[str]
) -> bool:
    """Removes a list of asset IDs from a specific album."""
    if not asset_ids:
        return True

    url: str = f"{IMMICH_BASE_URL}/api/albums/{album_id}/assets"
    payload = {"ids": asset_ids}
    # Immich uses DELETE with a JSON body for bulk removal
    async with session.delete(url, json=payload) as response:
        if response.status not in (200, 204):
            # print if there's an error (like a 401 or 500)
            error_text = await response.text()
            print(f"Failed to remove assets from {album_id}: {error_text}")
            return False
    return True


async def sync_album(session, data, name, key, val):
    album_id = await get_or_create_album(session, name)
    target_ids = set(get_asset_ids_by_filter(data, key, val))
    current_ids = set(await get_current_album_asset_ids(session, album_id))

    to_add = list(target_ids - current_ids)
    to_remove = list(current_ids - target_ids)

    if to_add:
        await add_assets_to_album(session, album_id, to_add)
    if to_remove:
        await remove_assets_from_album(session, album_id, to_remove)

    # RETURN the stats for our summary
    return {"added": len(to_add), "removed": len(to_remove), "total": len(target_ids)}


async def main() -> None:
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    async with aiohttp.ClientSession(headers=headers) as session:
        data = await pull_all_immich_metadata(session)
        people_lookup = await get_people_lookup(session)
        summary = {}

        for config in SYNC_CONFIGS:
            name = config["name"]
            val = config["val"]
            # 2. If the filter is 'people' and we provided names, resolve them
            if config["key"] == "people" and isinstance(val, list):
                val = resolve_names_to_uuids(val, people_lookup)

            stats = await sync_album(session, data, name, config["key"], val)
            summary[name] = stats

        # --- PRINT SUMMARY ---
        print("\n" + "=" * 30)
        print("FINAL SYNC SUMMARY")
        print("=" * 30)
        for name, stats in summary.items():
            print(f"ALBUM: {name}")
            print(f"  - Added:   {stats['added']}")
            print(f"  - Removed: {stats['removed']}")
            print(f"  - Current Total: {stats['total']}")
            print("-" * 15)


if __name__ == "__main__":
    asyncio.run(main())
