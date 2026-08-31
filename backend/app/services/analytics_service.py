import pandas as pd
from typing import Dict, Any
import re
from app.services.normalization_service import parse_currency, normalize_probability, normalize_status

class AnalyticsService:
    @staticmethod
    def calculate_deals_metrics(df: pd.DataFrame, filters: Dict = None, user_query: str = "") -> Dict[str, Any]:
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
            
        # Determine semantic date column for Deals
        user_query_lower = user_query.lower()
        if re.search(r'\b(historical|won|actual closure|closed)\b', user_query_lower):
            target_date_col = 'close date (a)'
        else:
            # Default to pipeline/expected
            target_date_col = 'tentative close date'

        # Apply filters
        if filters:
            if filters.get("status"):
                statuses = [s.lower() for s in filters["status"]]
                df = df[df['status_norm'].isin(statuses)]
            
            if filters.get("date_range"):
                # Use semantic date column if it exists in df
                if target_date_col in df.columns:
                    try:
                        from app.services.normalization_service import parse_date
                        df['parsed_date'] = df[target_date_col].apply(parse_date)
                        now = pd.Timestamp.now()
                        dr_type = filters["date_range"].get("type", "")
                        if dr_type == "current_quarter":
                            q_start = pd.Timestamp(now.year, (now.quarter - 1) * 3 + 1, 1)
                            q_end = q_start + pd.DateOffset(months=3)
                            df = df[(df['parsed_date'] >= q_start) & (df['parsed_date'] < q_end)]
                        elif dr_type == "current_month":
                            m_start = pd.Timestamp(now.year, now.month, 1)
                            m_end = m_start + pd.DateOffset(months=1)
                            df = df[(df['parsed_date'] >= m_start) & (df['parsed_date'] < m_end)]
                        elif dr_type == "last_quarter":
                            q_current_start = pd.Timestamp(now.year, (now.quarter - 1) * 3 + 1, 1)
                            q_last_start = q_current_start - pd.DateOffset(months=3)
                            df = df[(df['parsed_date'] >= q_last_start) & (df['parsed_date'] < q_current_start)]
                        elif dr_type == "upcoming":
                            today_start = pd.Timestamp(now.year, now.month, now.day)
                            upcoming_end = today_start + pd.DateOffset(days=90)
                            df = df[(df['parsed_date'] >= today_start) & (df['parsed_date'] < upcoming_end)]
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
    def calculate_work_orders_metrics(df: pd.DataFrame, filters: Dict = None, user_query: str = "") -> Dict[str, Any]:
        if df.empty:
            return {
                "total_work_orders": 0, 
                "ongoing": 0, 
                "completed": 0, 
                "partially_completed": 0,
                "paused_or_stuck": 0,
                "not_started": 0,
                "pending_client_details": 0,
                "executed_until_current_month": 0,
                "active_or_incomplete_projects": 0
            }
            
        if 'execution status' in df.columns:
            df['status_norm'] = df['execution status'].apply(normalize_status).str.lower()
        else:
            df['status_norm'] = "unknown"

        # Determine semantic date column for Work Orders
        user_query_lower = user_query.lower()
        if re.search(r'\b(end|ending|finish|complete)\b', user_query_lower):
            target_date_col = 'probable end date'
        elif re.search(r'\b(delivery|deliver)\b', user_query_lower):
            target_date_col = 'data delivery date'
        elif re.search(r'\b(po|loi|order)\b', user_query_lower):
            target_date_col = 'date of po/loi'
        else:
            # Default for "starting soon" or generic pipeline questions
            target_date_col = 'probable start date'

        if filters and filters.get("date_range"):
            if target_date_col in df.columns:
                try:
                    from app.services.normalization_service import parse_date
                    df['parsed_date'] = df[target_date_col].apply(parse_date)
                    now = pd.Timestamp.now()
                    dr_type = filters["date_range"].get("type", "")
                    if dr_type == "current_quarter":
                        q_start = pd.Timestamp(now.year, (now.quarter - 1) * 3 + 1, 1)
                        q_end = q_start + pd.DateOffset(months=3)
                        df = df[(df['parsed_date'] >= q_start) & (df['parsed_date'] < q_end)]
                    elif dr_type == "current_month":
                        m_start = pd.Timestamp(now.year, now.month, 1)
                        m_end = m_start + pd.DateOffset(months=1)
                        df = df[(df['parsed_date'] >= m_start) & (df['parsed_date'] < m_end)]
                    elif dr_type == "last_quarter":
                        q_current_start = pd.Timestamp(now.year, (now.quarter - 1) * 3 + 1, 1)
                        q_last_start = q_current_start - pd.DateOffset(months=3)
                        df = df[(df['parsed_date'] >= q_last_start) & (df['parsed_date'] < q_current_start)]
                    elif dr_type == "upcoming":
                        today_start = pd.Timestamp(now.year, now.month, now.day)
                        upcoming_end = today_start + pd.DateOffset(days=90)
                        df = df[(df['parsed_date'] >= today_start) & (df['parsed_date'] < upcoming_end)]
                except Exception:
                    pass

        # Granular Work Order Status Semantics
        ongoing = df[df['status_norm'] == 'ongoing']
        completed = df[df['status_norm'] == 'completed']
        partially_completed = df[df['status_norm'] == 'partial completed']
        paused_or_stuck = df[df['status_norm'] == 'pause / struck']
        not_started = df[df['status_norm'] == 'not started']
        pending_client_details = df[df['status_norm'] == 'details pending from client']
        executed_until_current_month = df[df['status_norm'] == 'executed until current month']

        # Broad aggregate for anything that is actively being worked on or waiting to be finished
        active_or_incomplete = df[~df['status_norm'].isin(['completed', 'unknown'])]
        
        return {
            "total_work_orders": len(df),
            "ongoing": len(ongoing),
            "completed": len(completed),
            "partially_completed": len(partially_completed),
            "paused_or_stuck": len(paused_or_stuck),
            "not_started": len(not_started),
            "pending_client_details": len(pending_client_details),
            "executed_until_current_month": len(executed_until_current_month),
            "active_or_incomplete_projects": len(active_or_incomplete),
            "status_distribution": df['status_norm'].value_counts().to_dict() if 'status_norm' in df.columns else {}
        }
