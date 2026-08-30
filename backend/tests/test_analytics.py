import pandas as pd
from app.services.analytics_service import AnalyticsService
from unittest.mock import patch

def test_deals_metrics_calculations():
    df = pd.DataFrame([
        {"deal status": "open", "masked deal value": "1000", "closure probability": "High"},
        {"deal status": "won", "masked deal value": "2000", "closure probability": "Won"}
    ])
    
    metrics = AnalyticsService.calculate_deals_metrics(df, user_query="pipeline this quarter")
    assert metrics["open_deals"] == 1
    assert metrics["won_deals"] == 1
    assert metrics["total_pipeline"] == 1000.0
    assert metrics["weighted_pipeline"] == 750.0
    assert metrics["won_value"] == 2000.0

@patch('pandas.Timestamp.now')
def test_deals_date_filtering(mock_now):
    # Mock current date to be 2023-11-15 (Q4)
    mock_now.return_value = pd.Timestamp('2023-11-15')
    
    df = pd.DataFrame([
        # Deal 1: tentative close is Q4, close date (a) is Q3
        {"deal status": "open", "tentative close date": "2023-11-01", "close date (a)": "2023-09-01"},
        # Deal 2: tentative close is Q3, close date (a) is Q4
        {"deal status": "won", "tentative close date": "2023-09-01", "close date (a)": "2023-11-01"}
    ])
    
    filters = {"date_range": {"type": "current_quarter"}}
    
    # 1. Pipeline query (uses tentative close date, which for Deal 1 is Q4, Deal 2 is Q3)
    metrics_pipeline = AnalyticsService.calculate_deals_metrics(df.copy(), filters, user_query="expected to close")
    assert metrics_pipeline["total_deals"] == 1 # Only Deal 1 is in Q4 for tentative
    assert metrics_pipeline["open_deals"] == 1
    
    # 2. Historical/Won query (uses close date (a), which for Deal 1 is Q3, Deal 2 is Q4)
    metrics_historical = AnalyticsService.calculate_deals_metrics(df.copy(), filters, user_query="actual closure won")
    assert metrics_historical["total_deals"] == 1 # Only Deal 2 is in Q4 for close date (a)
    assert metrics_historical["won_deals"] == 1

def test_work_orders_status_buckets():
    df = pd.DataFrame([
        {"execution status": "ongoing"},
        {"execution status": "completed"},
        {"execution status": "partially completed"},
        {"execution status": "pause"},
        {"execution status": "not started"},
        {"execution status": "pending client details"}
    ])
    
    metrics = AnalyticsService.calculate_work_orders_metrics(df, user_query="status overview")
    assert metrics["ongoing"] == 1
    assert metrics["completed"] == 1
    assert metrics["partially_completed"] == 1
    assert metrics["paused_or_stuck"] == 1
    assert metrics["not_started"] == 1
    assert metrics["pending_client_details"] == 1
    assert metrics["active_or_incomplete_projects"] == 5 # everything except 'completed'

@patch('pandas.Timestamp.now')
def test_work_orders_date_filtering(mock_now):
    mock_now.return_value = pd.Timestamp('2023-11-15')
    
    df = pd.DataFrame([
        {
            "execution status": "ongoing",
            "probable start date": "2023-11-01", 
            "probable end date": "2023-09-01", 
            "data delivery date": "2023-09-01", 
            "date of po/loi": "2023-09-01"
        },
        {
            "execution status": "completed",
            "probable start date": "2023-09-01", 
            "probable end date": "2023-11-01", 
            "data delivery date": "2023-09-01", 
            "date of po/loi": "2023-09-01"
        }
    ])
    
    filters = {"date_range": {"type": "current_quarter"}}
    
    # "starting soon" -> uses probable start date
    m_start = AnalyticsService.calculate_work_orders_metrics(df.copy(), filters, user_query="starting soon")
    assert m_start["total_work_orders"] == 1
    
    # "ending soon" -> uses probable end date
    m_end = AnalyticsService.calculate_work_orders_metrics(df.copy(), filters, user_query="ending soon")
    assert m_end["total_work_orders"] == 1
