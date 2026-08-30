import pandas as pd
from fastapi import APIRouter, HTTPException
from app.models.response_models import ChatRequest, ChatResponse
from app.services.monday_service import monday_service, MondayServiceError
from app.services.llm_service import LLMService, LLMServiceError
from app.services.data_quality_service import DataQualityService
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    try:
        # Initialize LLM service per request (MondayService is imported as singleton for caching)
        llm_service = LLMService()
        
        # 1. Parse intent using LLM
        query_plan = llm_service.parse_query(request.message)
        
        if query_plan.needs_clarification and query_plan.clarification_question:
            return ChatResponse(
                answer=query_plan.clarification_question,
                intent="clarification_needed",
                metrics={},
                warnings=[],
                sources=[]
            )

        # 2. Fetch Data & Analyze based on datasets requested
        metrics = {}
        warnings = []
        sources = []
        
        # Handle Deals
        if "deals" in query_plan.datasets or query_plan.intent in ["pipeline_health", "leadership_update"]:
            deals_data = monday_service.get_deals_data()
            df_deals = pd.DataFrame(deals_data)
            deals_warnings = DataQualityService.analyze_deals(df_deals)
            warnings.extend(deals_warnings)
            
            filter_dict = query_plan.filters.model_dump() if query_plan.filters else {}
            deals_metrics = AnalyticsService.calculate_deals_metrics(df_deals, filter_dict, request.message)
            metrics.update(deals_metrics)
            sources.append("Deals")
            
        # Handle Work Orders
        if "work_orders" in query_plan.datasets or query_plan.intent in ["work_order_status", "leadership_update"]:
            wo_data = monday_service.get_work_orders_data()
            df_wo = pd.DataFrame(wo_data)
            wo_warnings = DataQualityService.analyze_work_orders(df_wo)
            warnings.extend(wo_warnings)
            
            filter_dict = query_plan.filters.model_dump() if query_plan.filters else {}
            wo_metrics = AnalyticsService.calculate_work_orders_metrics(df_wo, filter_dict, request.message)
            metrics.update(wo_metrics)
            sources.append("Work Orders")

        # 3. Generate Executive Response
        executive_summary = llm_service.generate_executive_response(
            user_message=request.message,
            query_plan=query_plan,
            metrics=metrics,
            warnings=warnings
        )
        
        return ChatResponse(
            answer=executive_summary,
            intent=query_plan.intent,
            metrics=metrics,
            warnings=warnings,
            sources=list(set(sources))
        )

    except (MondayServiceError, LLMServiceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
