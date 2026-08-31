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
        # Deal 1: Q4 (current quarter), Current Month (Nov)
        {"deal status": "open", "tentative close date": "2023-11-01", "close date (a)": "2023-11-05"},
        # Deal 2: Q3 (last quarter), Last Month (Oct)
        {"deal status": "won", "tentative close date": "2023-09-01", "close date (a)": "2023-09-15"},
        # Deal 3: Q1 next year (future)
        {"deal status": "open", "tentative close date": "2024-02-01", "close date (a)": "2024-02-01"},
    ])
    
    # 1. Test Current Quarter Boundary
    filters_cq = {"date_range": {"type": "current_quarter"}}
    metrics_cq = AnalyticsService.calculate_deals_metrics(df.copy(), filters_cq, user_query="expected to close")
    assert metrics_cq["total_deals"] == 1 # Excludes past (Q3) and future (2024 Q1)
    
    # 2. Test Last Quarter Boundary
    filters_lq = {"date_range": {"type": "last_quarter"}}
    metrics_lq = AnalyticsService.calculate_deals_metrics(df.copy(), filters_lq, user_query="actual closure won")
    assert metrics_lq["total_deals"] == 1 # Captures Q3, ignores Q4 and 2024
    
    # 3. Test Upcoming Boundary (90 days forward from Nov 15)
    filters_up = {"date_range": {"type": "upcoming"}}
    metrics_up = AnalyticsService.calculate_deals_metrics(df.copy(), filters_up, user_query="expected to close")
    assert metrics_up["total_deals"] == 1 # Captures Deal 3 (Feb), excludes Deal 1 (Nov 1 is past) and Deal 2

def test_work_orders_status_buckets():
    df = pd.DataFrame([
        {"execution status": "ongoing"},
        {"execution status": "completed"},
        {"execution status": "partial completed"},
        {"execution status": "pause / struck"},
        {"execution status": "not started"},
        {"execution status": "details pending from client"},
        {"execution status": "executed until current month"}
    ])
    
    metrics = AnalyticsService.calculate_work_orders_metrics(df, user_query="status overview")
    assert metrics["ongoing"] == 1
    assert metrics["completed"] == 1
    assert metrics["partially_completed"] == 1
    assert metrics["paused_or_stuck"] == 1
    assert metrics["not_started"] == 1
    assert metrics["pending_client_details"] == 1
    assert metrics["executed_until_current_month"] == 1
    assert metrics["active_or_incomplete_projects"] == 6 # everything except 'completed'

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
