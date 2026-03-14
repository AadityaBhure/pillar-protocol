from groq import Groq
import json
import hashlib
from datetime import datetime
from typing import List
from fastapi import UploadFile
from backend.models import InspectionResult, Milestone
from utils.file_processor import concatenate_upload_files
import logging

logger = logging.getLogger(__name__)


class InspectorAgent:
    def __init__(self, gemini_api_key: str = None, groq_api_key: str = None):
        """Initialize with Groq API credentials"""
        api_key = groq_api_key or gemini_api_key  # accept either param name
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def analyze_code(self, files: List[UploadFile], checklist: List[dict]) -> InspectionResult:
        """Analyze uploaded code against checklist."""
        code_blob = await self._concatenate_files(files)

        all_requirements = []
        milestone_id = None
        for milestone in checklist:
            for req in milestone.get("requirements", []):
                all_requirements.append(str(req) if not isinstance(req, str) else req)
            if milestone_id is None:
                milestone_id = milestone.get("id")

        result_data = await self._check_logic_coverage(code_blob, all_requirements)
        code_hash = hashlib.sha256(code_blob.encode()).hexdigest()

        return InspectionResult(
            milestone_id=milestone_id,
            passed=result_data["passed"],
            coverage_score=result_data["coverage_score"],
            feedback=result_data["feedback"],
            missing_requirements=result_data.get("missing_requirements", []),
            analyzed_at=datetime.utcnow(),
            code_blob_hash=code_hash
        )

    async def _concatenate_files(self, files: List[UploadFile]) -> str:
        try:
            return await concatenate_upload_files(files)
        except Exception as e:
            logger.error(f"Error concatenating files: {e}", exc_info=True)
            raise ValueError(f"Failed to concatenate files: {str(e)}")

    async def _check_logic_coverage(self, code_blob: str, requirements: List[str]) -> dict:
        """Send to Groq for logic coverage analysis."""
        requirements = [str(r) for r in requirements]

        try:
            requirements_json = json.dumps(requirements, indent=2)
        except TypeError as e:
            logger.error(f"Failed to serialize requirements: {e}")
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to process requirements: {e}",
                "missing_requirements": []
            }

        system_prompt = """You are a code review AI. Analyze code for logic coverage against requirements.
Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{
    "passed": true or false,
    "coverage_score": 0-100,
    "feedback": "detailed explanation",
    "missing_requirements": ["list of unmet requirements"]
}"""

        user_prompt = f"""Check if this code implements all requirements.

Requirements:
{requirements_json}

Code:
{code_blob}

Rules:
1. Are all requirements implemented with actual logic?
2. Are functions defined AND actually used?
3. Is there real functionality, not just imports?"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            raw_json = response.choices[0].message.content.strip()

            if raw_json.startswith('```'):
                raw_json = self._extract_json_from_markdown(raw_json)

            result_data = json.loads(raw_json)

            if 'passed' not in result_data or not isinstance(result_data['passed'], bool):
                raise ValueError("Invalid result: missing or invalid 'passed' field")
            if 'coverage_score' not in result_data:
                raise ValueError("Invalid result: missing 'coverage_score' field")

            result_data['coverage_score'] = max(0, min(100, float(result_data['coverage_score'])))
            result_data.setdefault('feedback', 'Analysis completed')
            result_data.setdefault('missing_requirements', [])

            return result_data

        except json.JSONDecodeError as e:
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to analyze code: Invalid JSON response from AI. Error: {e}",
                "missing_requirements": requirements
            }
        except Exception as e:
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to analyze code: {e}",
                "missing_requirements": requirements
            }

    def _extract_json_from_markdown(self, text: str) -> str:
        lines = text.split('\n')
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block or (not line.strip().startswith('```') and json_lines):
                json_lines.append(line)
        return '\n'.join(json_lines).strip()
