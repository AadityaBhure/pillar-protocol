import google.generativeai as genai
import json
import hashlib
from datetime import datetime
from typing import List
from fastapi import UploadFile
from backend.models import InspectionResult, Milestone
from utils.file_processor import concatenate_upload_files


class InspectorAgent:
    def __init__(self, gemini_api_key: str):
        """Initialize with Gemini API credentials"""
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def analyze_code(
        self,
        files: List[UploadFile],
        checklist: List[dict]
    ) -> InspectionResult:
        """
        Analyze uploaded code against checklist.
        Checks logic coverage, not just imports.
        Verifies functions are actually used.
        """
        # Concatenate files
        code_blob = await self._concatenate_files(files)
        
        # Extract requirements from checklist
        all_requirements = []
        milestone_id = None
        for milestone in checklist:
            # Ensure all requirements are strings
            requirements = milestone.get("requirements", [])
            for req in requirements:
                if isinstance(req, str):
                    all_requirements.append(req)
                else:
                    # Convert non-string requirements to strings
                    all_requirements.append(str(req))
            if milestone_id is None:
                milestone_id = milestone.get("id")
        
        # Analyze logic coverage
        result_data = await self._check_logic_coverage(code_blob, all_requirements)
        
        # Generate code blob hash
        code_hash = hashlib.sha256(code_blob.encode()).hexdigest()
        
        # Create inspection result
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
        """
        Concatenate files with [FILE_START] and [FILE_END] tags.
        Format: [FILE_START:filename.py]\n<content>\n[FILE_END:filename.py]
        """
        try:
            return await concatenate_upload_files(files)
        except Exception as e:
            # Log detailed error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error concatenating files: {e}", exc_info=True)
            raise ValueError(f"Failed to concatenate files: {str(e)}")
    
    async def _check_logic_coverage(self, code_blob: str, requirements: List[str]) -> dict:
        """Send to Gemini Flash for logic coverage analysis"""
        
        # Ensure all requirements are strings
        requirements = [str(req) if not isinstance(req, str) else req for req in requirements]
        
        try:
            # Create the analysis prompt
            requirements_json = json.dumps(requirements, indent=2)
        except TypeError as e:
            # If JSON serialization fails, log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to serialize requirements: {e}")
            logger.error(f"Requirements type: {type(requirements)}")
            logger.error(f"Requirements content: {requirements}")
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to process requirements: {e}",
                "missing_requirements": []
            }
        
        analysis_prompt = f"""Analyze this code for LOGIC COVERAGE against requirements.

Requirements:
{requirements_json}

Code:
{code_blob}

Check:
1. Are all requirements implemented with actual logic?
2. Are functions defined AND actually used?
3. Is there real functionality, not just imports?

Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{{
    "passed": true or false,
    "coverage_score": 0-100,
    "feedback": "detailed explanation",
    "missing_requirements": ["list of unmet requirements"]
}}
"""
        
        try:
            response = self.model.generate_content(analysis_prompt)
            raw_json = response.text.strip()
            
            # Remove markdown code blocks if present
            if raw_json.startswith('```'):
                raw_json = self._extract_json_from_markdown(raw_json)
            
            result_data = json.loads(raw_json)
            
            # Validate result structure
            if 'passed' not in result_data or not isinstance(result_data['passed'], bool):
                raise ValueError("Invalid result: missing or invalid 'passed' field")
            
            if 'coverage_score' not in result_data:
                raise ValueError("Invalid result: missing 'coverage_score' field")
            
            # Ensure coverage_score is in bounds
            result_data['coverage_score'] = max(0, min(100, float(result_data['coverage_score'])))
            
            if 'feedback' not in result_data:
                result_data['feedback'] = "Analysis completed"
            
            if 'missing_requirements' not in result_data:
                result_data['missing_requirements'] = []
            
            return result_data
            
        except json.JSONDecodeError as e:
            # Fallback result if JSON parsing fails
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to analyze code: Invalid JSON response from AI. Error: {e}",
                "missing_requirements": requirements
            }
        except Exception as e:
            # Fallback result for other errors
            return {
                "passed": False,
                "coverage_score": 0,
                "feedback": f"Failed to analyze code: {e}",
                "missing_requirements": requirements
            }
    
    def _extract_json_from_markdown(self, text: str) -> str:
        """Extract JSON from markdown code blocks"""
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
