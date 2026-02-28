import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional, Set

import aiohttp

# --- LOGGING CONFIGURATION ---
# maxBytes: 5 * 1024 * 1024 is 5 Megabytes
# backupCount: Keeps the 3 most recent historical log files
rotating_handler = RotatingFileHandler(
    "immich_auto_album.log", maxBytes=5 * 1024 * 1024, backupCount=3
)

# Define the format for both handlers
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
rotating_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[rotating_handler, stream_handler])
logger = logging.getLogger(__name__)

# --- CONFIGURATION LOADING ---
try:
    from local_settings import (
        API_KEY,
        IMMICH_BASE_URL,
        MAX_CONCURRENT_REQUESTS,
        SYNC_CONFIGS,
    )
except ImportError:
    logger.error("local_settings.py not found! Please create it from example_local_setting.py.")
    sys.exit(1)

# Constants derived from settings
BASE_URL: str = IMMICH_BASE_URL.rstrip("/")
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


class ImmichClient:
    """
    The ImmichClient class encapsulates all communication with the Immich API.
    """

    def __init__(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
        self.session = session
        self.sem = semaphore
        self._album_cache: Dict[str, str] = {}  # Mapping of "Album Name" -> "uuid"
        self._people_lookup: Dict[str, str] = {}  # Mapping of "person name" -> "uuid"

    async def fetch_metadata_page(self, page: int) -> Optional[List[dict]]:
        """Returns metadata list if successful, [] if end of data, None if error."""
        url = f"{BASE_URL}/api/search/metadata"
        payload = {"withPeople": True, "size": 1000, "page": page}

        async with self.sem:
            try:
                async with self.session.post(url, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Return items list; Immich usually returns [] at the end
                        return data.get("assets", {}).get("items", [])

                    logger.error(f"Page {page} failed with status {resp.status}")
                    return None  # Signal a non-terminal error
            except Exception as e:
                logger.error(f"Exception on page {page}: {e}")
                return None

    async def pull_all_metadata(self) -> List[dict]:
        all_items: List[dict] = []
        page = 1
        keep_going = True

        while keep_going:
            batch_range = range(page, page + MAX_CONCURRENT_REQUESTS)
            tasks = [self.fetch_metadata_page(p) for p in batch_range]
            results = await asyncio.gather(*tasks)

            for page_items in results:
                if page_items is None:
                    # OPTION: Raise error to prevent data loss
                    raise RuntimeError(f"Metadata pull failed at page {page}. Data is incomplete.")

                if not page_items:  # True empty list [] means end of library
                    keep_going = False
                    break

                all_items.extend(page_items)

            if keep_going:
                page += MAX_CONCURRENT_REQUESTS

        return all_items

    async def load_albums(self):
        """Pre-loads all existing albums into the local cache to minimize API calls."""
        url = f"{BASE_URL}/api/albums"
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            albums = await resp.json()
            self._album_cache = {a["albumName"]: a["id"] for a in albums}

    async def get_or_create_album(self, name: str) -> str:
        """Returns album ID from cache; creates the album if it doesn't exist."""
        if name in self._album_cache:
            return self._album_cache[name]

        logger.info(f"Creating new album: '{name}'")
        url = f"{BASE_URL}/api/albums"
        async with self.session.post(url, json={"albumName": name}) as resp:
            resp.raise_for_status()
            new_album = await resp.json()
            album_id = str(new_album["id"])
            self._album_cache[name] = album_id
            return album_id

    async def load_people(self):
        """Pre-loads people mapping into the local cache."""
        url = f"{BASE_URL}/api/people"
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            people_list = data.get("people", [])
            self._people_lookup = {p["name"].lower(): p["id"] for p in people_list if p.get("name")}

    def resolve_people_names(self, names: List[str]) -> List[str]:
        """Converts a list of person names to their UUIDs using the cache."""
        uuids = []
        for name in names:
            clean_name = name.lower().strip()
            if clean_name in self._people_lookup:
                uuids.append(self._people_lookup[clean_name])
            else:
                logger.warning(f"Could not find person '{name}' in Immich. Check spelling!")
        return uuids

    async def get_album_assets(self, album_id: str) -> Set[str]:
        """Retrieves asset IDs currently in a specific album."""
        url = f"{BASE_URL}/api/albums/{album_id}"
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return {asset["id"] for asset in data.get("assets", [])}

    async def update_album_assets(self, album_id: str, to_add: List[str], to_remove: List[str]):
        """Performs bulk addition and removal of assets in chunks for stability."""
        url = f"{BASE_URL}/api/albums/{album_id}/assets"
        chunk_size = 2000

        # Add assets
        for i in range(0, len(to_add), chunk_size):
            chunk = to_add[i : i + chunk_size]
            async with self.session.put(url, json={"ids": chunk}) as resp:
                if resp.status not in (200, 201):
                    logger.error(f"Failed to add assets to {album_id}: {await resp.text()}")

        # Remove assets
        for i in range(0, len(to_remove), chunk_size):
            chunk = to_remove[i : i + chunk_size]
            async with self.session.delete(url, json={"ids": chunk}) as resp:
                if resp.status not in (200, 204):
                    logger.error(f"Failed to remove assets from {album_id}: {await resp.text()}")


def check_single_filter(asset: Dict[str, Any], key: str, val: Any, match_all: bool = False) -> bool:
    """Returns True if the asset passes this specific filter rule."""
    raw_meta = asset.get(key)

    # 1. Handle "None" (Untagged/No People)
    if val is None:
        return not raw_meta  # Returns True if metadata is None, [], or ""

    # 2. Normalize target into a set
    target_set = set(val) if isinstance(val, list) else {val}

    # 3. Handle single values (type="IMAGE", isFavorite=True)
    if not isinstance(raw_meta, list):
        return raw_meta in target_set

    # 4. Handle Lists (People/Tags)
    photo_meta_set = {(p.get("id") if isinstance(p, dict) else p) for p in raw_meta if p}

    if match_all:
        return target_set.issubset(photo_meta_set)
    return not target_set.isdisjoint(photo_meta_set)


def filter_assets(assets: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[str]:
    """
    Applies a list of rules to the assets.
    Every rule in the 'rules' list must be True (AND logic between rules).
    """
    results: List[str] = []

    for a in assets:
        asset_id = a.get("id")
        if not asset_id:
            continue
        # A photo starts as "passed" and must survive every rule
        if all(
            check_single_filter(a, r["key"], r["val"], r.get("match_all", False)) for r in rules
        ):
            results.append(str(asset_id))
    return results


async def sync_album_task(client: ImmichClient, all_assets: List[dict], config: dict) -> dict:
    """Worker task that processes a list of filters for a single album."""
    name: str = config["name"]
    rules: List[dict] = config["filters"]  # No more fallback checks

    # Clean up any 'people' names in the filters into UUIDs immediately
    for r in rules:
        if r.get("key") == "people" and isinstance(r.get("val"), list):
            r["val"] = client.resolve_people_names(r["val"])

    try:
        album_id = await client.get_or_create_album(name)

        # All logic is now centralized in filter_assets
        target_ids = set(filter_assets(all_assets, rules))
        current_ids = await client.get_album_assets(album_id)

        to_add = list(target_ids - current_ids)
        to_remove = list(current_ids - target_ids)

        if to_add or to_remove:
            await client.update_album_assets(album_id, to_add, to_remove)
            logger.info(f"Album '{name}': Added {len(to_add)}, Removed {len(to_remove)}")
        else:
            logger.debug(f"Album '{name}': Already in sync")

        return {
            "name": name,
            "added": len(to_add),
            "removed": len(to_remove),
            "total": len(target_ids),
        }
    except Exception as e:
        logger.error(f"Failed to sync album '{name}': {e}")
        return {"name": name, "error": str(e)}


async def main() -> None:
    """
    Main orchestration function:
    1. Sets up the client and concurrency semaphore.
    2. Parallelizes the initial data fetch (Metadata, Albums, People).
    3. Triggers parallel sync tasks for every album in SYNC_CONFIGS.
    4. Logs a formatted final report.
    """
    logger.info("--- Starting Sync Run ---")
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        client = ImmichClient(session, sem)
        logger.info("Loading data (Metadata, Albums, People)...")
        try:
            # Run all three initialization tasks in parallel and unpack results
            # The '_' variables are for tasks that populate the client's internal cache
            all_assets, _, _ = await asyncio.gather(
                client.pull_all_metadata(), client.load_albums(), client.load_people()
            )
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return

        logger.info(f"Syncing {len(SYNC_CONFIGS)} albums defined in local_settings.py...")

        # Schedule sync tasks for all configured albums
        sync_tasks = [sync_album_task(client, all_assets, config) for config in SYNC_CONFIGS]

        # results will be a list of dictionaries containing sync summaries or errors
        summaries: List[Dict[str, Any]] = await asyncio.gather(*sync_tasks)

        # Build and Log the Final Report
        # Using logger.info ensures this table is saved to your .log file for cron history
        report_header = "\n" + "=" * 65
        report_header += f"\n{'ALBUM NAME':<25} | {'ADDED':<6} | {'REM':<6} | {'TOTAL':<6}"
        report_header += "\n" + "-" * 65
        logger.info(report_header)

        for s in summaries:
            name: str = s.get("name", "Unknown")
            if "error" in s:
                logger.error(f"{name:<25} | ERROR: {s['error']}")
            else:
                added: int = s.get("added", 0)
                removed: int = s.get("removed", 0)
                total: int = s.get("total", 0)
                logger.info(f"{name:<25} | {added:<6} | {removed:<6} | {total:<6}")

        logger.info("=" * 65)
        logger.info(f"--- Sync Run Complete. {len(summaries)} albums processed. ---")


if __name__ == "__main__":
    try:
        # Standard entry point for the async loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
    except Exception as e:
        # Final catch-all for any unhandled exceptions
        logger.error(f"Fatal error during execution: {e}")
