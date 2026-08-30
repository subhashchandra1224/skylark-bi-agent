import os
import json
from dotenv import load_dotenv
load_dotenv()
from app.services.monday_service import monday_service
import pandas as pd

def debug():
    config = monday_service._get_config()
    mapping = monday_service.fetch_board_metadata(config["work_orders_id"])
    
    query = """
    query ($boardId: [ID!]) {
        boards(ids: $boardId) {
            items_page(limit: 10) {
                items {
                    name
                    column_values {
                        id
                        text
                        value
                        type
                    }
                }
            }
        }
    }
    """
    data = monday_service._execute_query(query, {"boardId": [config["work_orders_id"]]})
    items = data["boards"][0]["items_page"]["items"]
    
    col_id = None
    for k, v in mapping.items():
        if k == "probable start date":
            col_id = v
            break
            
    print(f"Column ID for 'probable start date': {col_id}")
    
    from app.services.normalization_service import parse_date
    for item in items:
        name = item["name"]
        for cv in item["column_values"]:
            if cv["id"] == col_id:
                raw_text = cv.get('text', '')
                parsed = parse_date(raw_text)
                print(f"Item: {name} | Raw: {raw_text} | Parsed: {parsed}")
                
    print("\nTotal items checked: 10")

if __name__ == "__main__":
    debug()
