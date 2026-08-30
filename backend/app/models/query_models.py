from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class DateRange(BaseModel):
    type: str  # e.g. "current_quarter", "specific_dates"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Filters(BaseModel):
    sector: Optional[str] = None
    status: Optional[List[str]] = None
    date_range: Optional[DateRange] = None

class StructuredQueryPlan(BaseModel):
    intent: str
    datasets: List[str]  # e.g., ["deals", "work_orders"]
    metrics: List[str]
    filters: Optional[Filters] = None
    group_by: Optional[str] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
