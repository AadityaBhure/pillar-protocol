import google.generativeai as genai
import json
import uuid
from typing import List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ArchitectAgent:
    def __init__(self, gemini_api_key: str):
        """Initialize with Gemini API credentials"""
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.config = self._load_deadline_config()
    
    def _load_deadline_config(self) -> dict:
        """
        Load deadline_config.json or return defaults
        
        Returns:
            dict with hours_to_days_ratio and reputation_weights
        """
        try:
            with open('deadline_config.json', 'r') as f:
                config = json.load(f)
                logger.info("Loaded deadline_config.json successfully")
                return config
        except FileNotFoundError:
            logger.warning("deadline_config.json not found, using defaults")
            return {
                'hours_to_days_ratio': 1.0,
                'reputation_weights': {
                    'on_time_bonus': 2,
                    'late_penalty': 5,
                    'high_quality_bonus': 1,
                    'low_quality_penalty': 2
                }
            }
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in deadline_config.json: %s, using defaults", e)
            return {
                'hours_to_days_ratio': 1.0,
                'reputation_weights': {
                    'on_time_bonus': 2,
                    'late_penalty': 5,
                    'high_quality_bonus': 1,
                    'low_quality_penalty': 2
                }
            }
    
    def _calculate_deadline(self, estimated_hours: int) -> str:
        """
        Calculate deadline using hours_to_days_ratio from config
        
        Args:
            estimated_hours: Estimated hours for milestone
            
        Returns:
            ISO 8601 timestamp string with 'Z' suffix
        """
        ratio = self.config.get('hours_to_days_ratio', 1.0)
        days = estimated_hours * ratio
        deadline_dt = datetime.utcnow() + timedelta(days=days)
        deadline_str = deadline_dt.isoformat() + 'Z'
        
        logger.info(
            "Calculated deadline: %d hours * %.2f ratio = %.2f days -> %s",
            estimated_hours, ratio, days, deadline_str
        )
        
        return deadline_str
    
    def generate_checklist(self, prompt: str) -> List[dict]:
        """
        Convert vague prompt into structured milestone list.
        Uses Gemini with system prompt enforcing milestone schema.
        Validates JSON output to prevent hallucinations.
        """
        system_prompt = """You are a technical project planning AI for developers. Convert the user's project idea into a JSON array of developer-focused milestones that can be verified against actual code.

Each milestone must have:
- id: unique identifier (generate a UUID-like string)
- title: technical task name (max 200 chars) - e.g., "Implement User Authentication API"
- description: technical implementation details - what needs to be built, not business value
- requirements: list of SPECIFIC, VERIFIABLE technical deliverables that can be checked in code
  * Use concrete technical terms: "Create POST /api/login endpoint", "Implement JWT token generation"
  * Avoid vague terms: Instead of "user-friendly", say "Return 400 status with error message for invalid input"
  * Each requirement should map to actual code artifacts: functions, classes, endpoints, files
  * Requirements should be checkable by inspecting the codebase
- estimated_hours: integer estimate (must be positive)

CRITICAL: Write requirements from a DEVELOPER'S perspective for CODE VERIFICATION:
✅ GOOD: "Create UserController class with login() method"
✅ GOOD: "Implement password hashing using bcrypt"
✅ GOOD: "Add email validation in User model"
✅ GOOD: "Create database migration for users table"
❌ BAD: "Easy to use interface" (not verifiable in code)
❌ BAD: "Good user experience" (subjective, not code-checkable)
❌ BAD: "Secure system" (too vague, not specific)

Return ONLY valid JSON array, no additional text or markdown formatting.

Example format:
[
  {
    "id": "milestone-1",
    "title": "Setup Authentication System",
    "description": "Implement JWT-based authentication with user registration and login endpoints",
    "requirements": [
      "Create User model with email, password_hash, created_at fields",
      "Implement POST /api/register endpoint with email validation",
      "Implement POST /api/login endpoint returning JWT token",
      "Add password hashing using bcrypt with salt rounds >= 10",
      "Create authentication middleware to verify JWT tokens",
      "Add error handling for invalid credentials (401 status)"
    ],
    "estimated_hours": 8
  }
]
"""
        
        full_prompt = f"{system_prompt}\n\nUser prompt: {prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            raw_json = response.text.strip()
            
            # Remove markdown code blocks if present
            if raw_json.startswith('```'):
                raw_json = self._extract_json_from_markdown(raw_json)
            
            # Parse JSON to prevent hallucinations
            milestones_data = json.loads(raw_json)
            
            # Validate schema for each milestone
            validated_milestones = []
            for data in milestones_data:
                if not self._validate_milestone_schema(data):
                    continue
                
                # Ensure id is a valid UUID (not just "1", "2", etc.)
                if 'id' not in data or not data['id'] or len(str(data['id'])) < 10:
                    data['id'] = str(uuid.uuid4())
                else:
                    # If ID exists but is not UUID format, convert it
                    try:
                        # Try to parse as UUID to validate
                        uuid.UUID(str(data['id']))
                    except (ValueError, AttributeError):
                        # Not a valid UUID, generate a new one
                        data['id'] = str(uuid.uuid4())
                
                # Convert estimated_hours to integer if it's a float
                if 'estimated_hours' in data:
                    if isinstance(data['estimated_hours'], float):
                        data['estimated_hours'] = int(round(data['estimated_hours']))
                    elif isinstance(data['estimated_hours'], str):
                        try:
                            data['estimated_hours'] = int(float(data['estimated_hours']))
                        except ValueError:
                            data['estimated_hours'] = 1  # Default to 1 hour
                
                validated_milestones.append(data)
            
            if len(validated_milestones) == 0:
                raise ValueError("No valid milestones generated")
            
            # NEW: Add deadline to each milestone
            for milestone in validated_milestones:
                deadline = self._calculate_deadline(milestone['estimated_hours'])
                milestone['deadline'] = deadline
            
            return validated_milestones
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from Gemini: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate checklist: {e}")
    
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
    
    def _validate_milestone_schema(self, data: dict) -> bool:
        """Validate milestone JSON structure"""
        required_fields = ['title', 'description', 'requirements', 'estimated_hours']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate types and constraints
        if not isinstance(data['title'], str) or len(data['title']) == 0:
            return False
        
        if not isinstance(data['requirements'], list) or len(data['requirements']) == 0:
            return False
        
        if not isinstance(data['estimated_hours'], int) or data['estimated_hours'] <= 0:
            return False
        
        return True
    
    def chat_response(self, message: str, conversation_history: str = "", current_milestones: List[dict] = None) -> dict:
        """
        Interactive chat response for iterative milestone planning.
        Allows users to refine milestones through conversation.
        """
        if current_milestones is None:
            current_milestones = []
        
        # Build context-aware prompt
        system_prompt = """You are a technical project planning AI assistant for developers. Help users refine their project milestones through conversation.

CRITICAL: All milestones and requirements must be DEVELOPER-FOCUSED and CODE-VERIFIABLE.

When generating or updating milestones:
1. Write from a DEVELOPER'S perspective, not a client's perspective
2. Requirements must be SPECIFIC and VERIFIABLE in actual code
3. Use technical terms: endpoints, functions, classes, database tables, API calls
4. Each requirement should map to actual code artifacts that can be inspected

GOOD Requirements (Developer-focused, verifiable):
✅ "Create UserService class with register() and login() methods"
✅ "Implement POST /api/users endpoint with JSON request body validation"
✅ "Add password hashing using bcrypt library"
✅ "Create users table migration with email, password_hash, created_at columns"
✅ "Implement JWT token generation in AuthMiddleware"
✅ "Add unit tests for authentication functions"

BAD Requirements (Client-focused, not verifiable):
❌ "User-friendly interface" (subjective, not code-checkable)
❌ "Good performance" (vague, not specific)
❌ "Secure system" (too broad, not verifiable)
❌ "Easy to use" (not a code requirement)

Format your response as:
<explanation>
Your conversational response here explaining the technical approach
</explanation>

<milestones>
[JSON array of developer-focused milestones if applicable]
</milestones>

Each milestone must have: id, title (technical task), description (implementation details), requirements (specific code deliverables), estimated_hours (integer)
"""
        
        # Add conversation context
        context = f"{system_prompt}\n\n"
        if conversation_history:
            context += f"Previous conversation:\n{conversation_history}\n\n"
        
        if current_milestones:
            context += f"Current milestones:\n{json.dumps(current_milestones, indent=2)}\n\n"
        
        context += f"User message: {message}"
        
        try:
            response = self.model.generate_content(context)
            response_text = response.text.strip()
            
            # Parse response to extract explanation and milestones
            explanation = ""
            milestones = []
            
            # Try to extract structured response
            if "<explanation>" in response_text and "</explanation>" in response_text:
                explanation_start = response_text.find("<explanation>") + len("<explanation>")
                explanation_end = response_text.find("</explanation>")
                explanation = response_text[explanation_start:explanation_end].strip()
                
                if "<milestones>" in response_text and "</milestones>" in response_text:
                    milestones_start = response_text.find("<milestones>") + len("<milestones>")
                    milestones_end = response_text.find("</milestones>")
                    milestones_json = response_text[milestones_start:milestones_end].strip()
                    
                    try:
                        milestones = json.loads(milestones_json)
                        # Validate and add IDs if missing, convert estimated_hours to int
                        for milestone in milestones:
                            # Ensure valid UUID
                            if 'id' not in milestone or not milestone['id'] or len(str(milestone['id'])) < 10:
                                milestone['id'] = str(uuid.uuid4())
                            else:
                                try:
                                    uuid.UUID(str(milestone['id']))
                                except (ValueError, AttributeError):
                                    milestone['id'] = str(uuid.uuid4())
                            # Convert estimated_hours to integer
                            if 'estimated_hours' in milestone:
                                if isinstance(milestone['estimated_hours'], float):
                                    milestone['estimated_hours'] = int(round(milestone['estimated_hours']))
                                elif isinstance(milestone['estimated_hours'], str):
                                    try:
                                        milestone['estimated_hours'] = int(float(milestone['estimated_hours']))
                                    except ValueError:
                                        milestone['estimated_hours'] = 1
                    except json.JSONDecodeError:
                        pass
            else:
                # Fallback: treat entire response as explanation
                explanation = response_text
                
                # Try to extract JSON if present
                if '[' in response_text and ']' in response_text:
                    try:
                        json_start = response_text.find('[')
                        json_end = response_text.rfind(']') + 1
                        potential_json = response_text[json_start:json_end]
                        milestones = json.loads(potential_json)
                        
                        # Remove JSON from explanation
                        explanation = response_text[:json_start].strip()
                        
                        # Validate and add IDs, convert estimated_hours to int
                        for milestone in milestones:
                            # Ensure valid UUID
                            if 'id' not in milestone or not milestone['id'] or len(str(milestone['id'])) < 10:
                                milestone['id'] = str(uuid.uuid4())
                            else:
                                try:
                                    uuid.UUID(str(milestone['id']))
                                except (ValueError, AttributeError):
                                    milestone['id'] = str(uuid.uuid4())
                            # Convert estimated_hours to integer
                            if 'estimated_hours' in milestone:
                                if isinstance(milestone['estimated_hours'], float):
                                    milestone['estimated_hours'] = int(round(milestone['estimated_hours']))
                                elif isinstance(milestone['estimated_hours'], str):
                                    try:
                                        milestone['estimated_hours'] = int(float(milestone['estimated_hours']))
                                    except ValueError:
                                        milestone['estimated_hours'] = 1
                            # NEW: Add deadline
                            if 'estimated_hours' in milestone:
                                milestone['deadline'] = self._calculate_deadline(milestone['estimated_hours'])
                    except:
                        pass
            
            return {
                "response": explanation if explanation else "I understand. How would you like to proceed?",
                "milestones": milestones
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Could you rephrase your request?",
                "milestones": []
            }
