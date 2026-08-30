import os
import requests
import time
from typing import Dict, List, Any, Optional

class MondayServiceError(Exception):
    """Custom exception for Monday.com API failures."""
    pass

class MondayService:
    def __init__(self):
        self.base_url = "https://api.monday.com/v2"
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes caching

    def _get_cached_data(self, key: str):
        cached = self._cache.get(key)
        if cached and time.time() - cached['timestamp'] < self._cache_ttl:
            return cached['data']
        return None

    def _set_cached_data(self, key: str, data: Any):
        self._cache[key] = {
            'timestamp': time.time(),
            'data': data
        }

    def _get_config(self) -> Dict[str, str]:
        api_token = os.getenv("MONDAY_API_TOKEN")
        deals_id = os.getenv("MONDAY_DEALS_BOARD_ID")
        work_orders_id = os.getenv("MONDAY_WORK_ORDERS_BOARD_ID")
        
        if not api_token:
            raise MondayServiceError("MONDAY_API_TOKEN is missing. Please configure it in .env")
        if not deals_id or not work_orders_id:
            raise MondayServiceError("Monday.com board IDs are missing. Please configure them in .env")
            
        return {
            "token": api_token,
            "deals_id": deals_id,
            "work_orders_id": work_orders_id
        }

    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": token,
            "API-Version": "2024-01",
            "Content-Type": "application/json",
        }

    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Executes a GraphQL query against the Monday.com API."""
        config = self._get_config()
        try:
            response = requests.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
                headers=self._get_headers(config["token"]),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                raise MondayServiceError(f"Monday API returned errors: {data['errors']}")
            return data["data"]
        except requests.exceptions.RequestException as e:
            raise MondayServiceError(f"Network error communicating with Monday.com: {str(e)}")

    def fetch_board_metadata(self, board_id: str) -> Dict[str, str]:
        """Fetches columns for a board and maps column titles (lowercase) to column IDs."""
        query = """
        query ($boardId: [ID!]) {
            boards(ids: $boardId) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        data = self._execute_query(query, {"boardId": [board_id]})
        try:
            columns = data["boards"][0]["columns"]
            # Map lowercase title to column ID for dynamic discovery
            return {col["title"].lower().strip(): col["id"] for col in columns}
        except (KeyError, IndexError) as e:
            raise MondayServiceError(f"Failed to parse board metadata: {str(e)}")

    def fetch_all_items(self, board_id: str, title_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetches all items from a board with pagination and maps values using the title mapping."""
        items = []
        cursor = None
        
        # Reverse mapping: column_id -> normalized title name
        id_to_title = {v: k for k, v in title_mapping.items()}

        while True:
            # Query items with pagination
            query = """
            query ($boardId: [ID!], $cursor: String) {
                boards(ids: $boardId) {
                    items_page(limit: 500, cursor: $cursor) {
                        cursor
                        items {
                            id
                            name
                            column_values {
                                id
                                text
                                value
                            }
                        }
                    }
                }
            }
            """
            data = self._execute_query(query, {"boardId": [board_id], "cursor": cursor})
            try:
                items_page = data["boards"][0]["items_page"]
                raw_items = items_page["items"]
                cursor = items_page.get("cursor")
                
                for item in raw_items:
                    record = {
                        "item_id": item["id"],
                        "name": item["name"] # Usually the primary item name
                    }
                    for cv in item.get("column_values", []):
                        col_id = cv["id"]
                        if col_id in id_to_title:
                            # Use the text field for display values
                            record[id_to_title[col_id]] = cv.get("text", "")
                    items.append(record)

                if not cursor:
                    break
            except (KeyError, IndexError) as e:
                raise MondayServiceError(f"Failed to parse items data: {str(e)}")
        
        return items
        
    def get_deals_data(self) -> List[Dict[str, Any]]:
        """Fetch Deals data dynamically with caching."""
        cached = self._get_cached_data("deals")
        if cached is not None:
            return cached
            
        config = self._get_config()
        mapping = self.fetch_board_metadata(config["deals_id"])
        data = self.fetch_all_items(config["deals_id"], mapping)
        self._set_cached_data("deals", data)
        return data
        
    def get_work_orders_data(self) -> List[Dict[str, Any]]:
        """Fetch Work Orders data dynamically with caching."""
        cached = self._get_cached_data("work_orders")
        if cached is not None:
            return cached
            
        config = self._get_config()
        mapping = self.fetch_board_metadata(config["work_orders_id"])
        data = self.fetch_all_items(config["work_orders_id"], mapping)
        self._set_cached_data("work_orders", data)
        return data

# Singleton instance
monday_service = MondayService()
