import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from app.models.query_models import StructuredQueryPlan
from pydantic import ValidationError

class LLMServiceError(Exception):
    pass

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise LLMServiceError("GEMINI_API_KEY is not configured in .env")
        
        genai.configure(api_key=self.api_key)
        # Use gemini-3.5-flash for speed and cost-effectiveness in processing json
        self.model = genai.GenerativeModel('gemini-3.5-flash')

    def parse_query(self, user_message: str) -> StructuredQueryPlan:
        """Parses a natural language query into a StructuredQueryPlan."""
        prompt = f"""
You are an expert Business Intelligence Agent for executives.
Analyze the user's question and extract a structured query plan in JSON format.
The query plan MUST strictly adhere to this schema:
{{
  "intent": "pipeline_health|work_order_status|cross_board|leadership_update|unknown",
  "datasets": ["deals", "work_orders"],
  "metrics": ["total_pipeline", "weighted_pipeline", "won_value", "open_deals", "ongoing_projects", "completed_projects"],
  "filters": {{
    "sector": "string or null",
    "status": ["array of status strings"],
    "date_range": {{"type": "current_quarter|last_quarter|current_month|upcoming"}}
  }},
  "needs_clarification": boolean,
  "clarification_question": "string or null"
}}

User Question: "{user_message}"

Respond ONLY with the raw JSON object. Do not wrap it in markdown code blocks.
"""
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            parsed_json = json.loads(raw_text)
            
            # Use Pydantic to validate
            plan = StructuredQueryPlan(**parsed_json)
            return plan
        except json.JSONDecodeError:
            raise LLMServiceError("Failed to parse LLM response into valid JSON.")
        except ValidationError as e:
            raise LLMServiceError(f"LLM generated invalid query plan structure: {e}")
        except Exception as e:
            raise LLMServiceError(f"LLM service error: {str(e)}")

    def generate_executive_response(self, user_message: str, query_plan: StructuredQueryPlan, metrics: Dict[str, Any], warnings: List[str]) -> str:
        """Generates a concise executive summary based on deterministic metrics."""
        
        warnings_text = "\n".join([f"- {w}" for w in warnings]) if warnings else "None"
        
        prompt = f"""
You are an AI Business Intelligence Agent. Provide a concise, executive-level answer to the user's question using ONLY the provided metrics.
Do NOT fabricate numbers or perform complex arithmetic. If metrics are missing, state that.
Include a brief "Data Quality Notes" section at the bottom if there are any warnings.

User Question: "{user_message}"
Calculated Metrics: {json.dumps(metrics, indent=2)}
Data Quality Warnings:
{warnings_text}

Format the response nicely using markdown (KPIs as bullet points, bold text for emphasis). 
Keep it very professional and concise.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise LLMServiceError(f"Failed to generate executive response: {str(e)}")

# Singleton instance
# llm_service = LLMService() # Will initialize dynamically to handle missing config cleanly
