from typing import List, Dict, Any
import pandas as pd

class DataQualityService:
    @staticmethod
    def analyze_deals(df: pd.DataFrame) -> List[str]:
        warnings = []
        
        # Check missing deal values
        if 'masked deal value' in df.columns:
            missing_vals = df['masked deal value'].replace('', pd.NA).isna().sum()
            if missing_vals > 0:
                warnings.append(f"Pipeline totals exclude {missing_vals} deals with missing deal values.")
        
        # Check missing probability
        if 'closure probability' in df.columns:
            missing_prob = df['closure probability'].replace('', pd.NA).isna().sum()
            if missing_prob > 0:
                warnings.append(f"{missing_prob} deals are missing closure probability, defaulting to 0 for weighted calculations.")
                
        # Check missing status
        if 'deal status' in df.columns:
            missing_status = df['deal status'].replace('', pd.NA).isna().sum()
            if missing_status > 0:
                warnings.append(f"{missing_status} deals are missing a deal status.")
                
        return warnings

    @staticmethod
    def analyze_work_orders(df: pd.DataFrame) -> List[str]:
        warnings = []
        
        # Check missing status
        if 'execution status' in df.columns:
            missing_status = df['execution status'].replace('', pd.NA).isna().sum()
            if missing_status > 0:
                warnings.append(f"{missing_status} work orders are missing an execution status.")
                
        # Check date consistency (End Date before Start Date)
        if 'probable start date' in df.columns and 'probable end date' in df.columns:
            from app.services.normalization_service import parse_date
            start_dates = df['probable start date'].apply(parse_date)
            end_dates = df['probable end date'].apply(parse_date)
            
            inconsistent = ((end_dates < start_dates) & start_dates.notna() & end_dates.notna()).sum()
            if inconsistent > 0:
                warnings.append(f"{inconsistent} work orders contain inconsistent project dates (end before start).")
                
        return warnings
