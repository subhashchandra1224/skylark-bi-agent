import pandas as pd
from typing import Dict, Any
from app.services.normalization_service import parse_currency, normalize_probability, normalize_status

class AnalyticsService:
    @staticmethod
    def calculate_deals_metrics(df: pd.DataFrame, filters: Dict = None) -> Dict[str, Any]:
        if df.empty:
            return {"total_pipeline": 0, "open_deals": 0, "weighted_pipeline": 0, "won_value": 0}
            
        # Normalize columns for calculation
        if 'masked deal value' in df.columns:
            df['deal_value_num'] = df['masked deal value'].apply(parse_currency)
        else:
            df['deal_value_num'] = 0.0
            
        if 'closure probability' in df.columns:
            df['prob_num'] = df['closure probability'].apply(normalize_probability)
        else:
            df['prob_num'] = 0.0
            
        if 'deal status' in df.columns:
            df['status_norm'] = df['deal status'].apply(normalize_status).str.lower()
        else:
            df['status_norm'] = "unknown"
            
        # Apply filters
        if filters:
            if filters.get("status"):
                statuses = [s.lower() for s in filters["status"]]
                df = df[df['status_norm'].isin(statuses)]
            
            if filters.get("date_range") and 'date' in df.columns:
                try:
                    from app.services.normalization_service import parse_date
                    df['parsed_date'] = df['date'].apply(parse_date)
                    now = pd.Timestamp.now()
                    dr_type = filters["date_range"].get("type", "")
                    if dr_type == "current_quarter":
                        q_start = pd.Timestamp(now.year, (now.quarter - 1) * 3 + 1, 1)
                        df = df[df['parsed_date'] >= q_start]
                    elif dr_type == "current_month":
                        m_start = pd.Timestamp(now.year, now.month, 1)
                        df = df[df['parsed_date'] >= m_start]
                except Exception:
                    pass # Fail open if dates are unparseable

        open_df = df[df['status_norm'] == 'open']
        won_df = df[df['status_norm'] == 'won']
        
        total_pipeline = open_df['deal_value_num'].sum()
        weighted_pipeline = (open_df['deal_value_num'] * open_df['prob_num']).sum()
        won_value = won_df['deal_value_num'].sum()
        
        return {
            "total_pipeline": float(total_pipeline),
            "weighted_pipeline": float(weighted_pipeline),
            "won_value": float(won_value),
            "open_deals": len(open_df),
            "won_deals": len(won_df),
            "total_deals": len(df)
        }

    @staticmethod
    def calculate_work_orders_metrics(df: pd.DataFrame, filters: Dict = None) -> Dict[str, Any]:
        if df.empty:
            return {"total_work_orders": 0, "ongoing": 0, "completed": 0}
            
        if 'execution status' in df.columns:
            df['status_norm'] = df['execution status'].apply(normalize_status).str.lower()
        else:
            df['status_norm'] = "unknown"

        ongoing = df[df['status_norm'].str.contains('ongoing|partial|pause', case=False, na=False)]
        completed = df[df['status_norm'].str.contains('completed|executed', case=False, na=False)]
        
        return {
            "total_work_orders": len(df),
            "ongoing_projects": len(ongoing),
            "completed_projects": len(completed),
            "status_distribution": df['status_norm'].value_counts().to_dict() if 'status_norm' in df.columns else {}
        }
