from groq import Groq
import json
import uuid
from typing import List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ArchitectAgent:
    def __init__(self, gemini_api_key: str = None, groq_api_key: str = None):
        """Initialize with Groq API credentials"""
        api_key = groq_api_key or gemini_api_key  # accept either param name
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.config = self._load_deadline_config()

    def _load_deadline_config(self) -> dict:
        try:
            with open('deadline_config.json', 'r') as f:
                config = json.load(f)
                logger.info("Loaded deadline_config.json successfully")
                return config
        except FileNotFoundError:
            logger.warning("deadline_config.json not found, using defaults")
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
        ratio = self.config.get('hours_to_days_ratio', 1.0)
        days = estimated_hours * ratio
        deadline_dt = datetime.utcnow() + timedelta(days=days)
        deadline_str = deadline_dt.isoformat() + 'Z'
        logger.info(
            "Calculated deadline: %d hours * %.2f ratio = %.2f days -> %s",
            estimated_hours, ratio, days, deadline_str
        )
        return deadline_str

    def _chat(self, system: str, user: str) -> str:
        """Single helper to call Groq chat completions"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def generate_checklist(self, prompt: str) -> List[dict]:
        """Convert vague prompt into structured milestone list."""
        system_prompt = """You are a technical project planning AI for developers. Convert the user's project idea into a JSON array of developer-focused milestones that can be verified against actual code.

Each milestone must have:
- id: unique identifier (generate a UUID-like string)
- title: technical task name (max 200 chars)
- description: technical implementation details
- requirements: list of SPECIFIC, VERIFIABLE technical deliverables checkable in code
- estimated_hours: integer estimate (must be positive)

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
      "Add password hashing using bcrypt with salt rounds >= 10"
    ],
    "estimated_hours": 8
  }
]"""

        try:
            raw_json = self._chat(system_prompt, f"User prompt: {prompt}")

            if raw_json.startswith('```'):
                raw_json = self._extract_json_from_markdown(raw_json)

            milestones_data = json.loads(raw_json)

            validated_milestones = []
            for data in milestones_data:
                if not self._validate_milestone_schema(data):
                    continue

                if 'id' not in data or not data['id'] or len(str(data['id'])) < 10:
                    data['id'] = str(uuid.uuid4())
                else:
                    try:
                        uuid.UUID(str(data['id']))
                    except (ValueError, AttributeError):
                        data['id'] = str(uuid.uuid4())

                if 'estimated_hours' in data:
                    if isinstance(data['estimated_hours'], float):
                        data['estimated_hours'] = int(round(data['estimated_hours']))
                    elif isinstance(data['estimated_hours'], str):
                        try:
                            data['estimated_hours'] = int(float(data['estimated_hours']))
                        except ValueError:
                            data['estimated_hours'] = 1

                validated_milestones.append(data)

            if not validated_milestones:
                raise ValueError("No valid milestones generated")

            for milestone in validated_milestones:
                milestone['deadline'] = self._calculate_deadline(milestone['estimated_hours'])

            return validated_milestones

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from Groq: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate checklist: {e}")

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

    def _validate_milestone_schema(self, data: dict) -> bool:
        required_fields = ['title', 'description', 'requirements', 'estimated_hours']
        for field in required_fields:
            if field not in data:
                return False
        if not isinstance(data['title'], str) or not data['title']:
            return False
        if not isinstance(data['requirements'], list) or not data['requirements']:
            return False
        if not isinstance(data['estimated_hours'], int) or data['estimated_hours'] <= 0:
            return False
        return True

    def chat_response(self, message: str, conversation_history: str = "", current_milestones: List[dict] = None) -> dict:
        """Interactive chat response for iterative milestone planning."""
        if current_milestones is None:
            current_milestones = []

        system_prompt = """You are a technical project planning AI assistant for developers. Help users refine their project milestones through conversation.

All milestones and requirements must be DEVELOPER-FOCUSED and CODE-VERIFIABLE.

Format your response as:
<explanation>
Your conversational response here
</explanation>

<milestones>
[JSON array of developer-focused milestones if applicable]
</milestones>

Each milestone must have: id, title, description, requirements (list of strings), estimated_hours (integer)"""

        user_content = ""
        if conversation_history:
            user_content += f"Previous conversation:\n{conversation_history}\n\n"
        if current_milestones:
            user_content += f"Current milestones:\n{json.dumps(current_milestones, indent=2)}\n\n"
        user_content += f"User message: {message}"

        try:
            response_text = self._chat(system_prompt, user_content)

            explanation = ""
            milestones = []

            if "<explanation>" in response_text and "</explanation>" in response_text:
                explanation = response_text[
                    response_text.find("<explanation>") + len("<explanation>"):
                    response_text.find("</explanation>")
                ].strip()

                if "<milestones>" in response_text and "</milestones>" in response_text:
                    milestones_json = response_text[
                        response_text.find("<milestones>") + len("<milestones>"):
                        response_text.find("</milestones>")
                    ].strip()
                    try:
                        milestones = json.loads(milestones_json)
                        milestones = self._normalize_milestones(milestones)
                    except json.JSONDecodeError:
                        pass
            else:
                explanation = response_text
                if '[' in response_text and ']' in response_text:
                    try:
                        json_start = response_text.find('[')
                        json_end = response_text.rfind(']') + 1
                        milestones = json.loads(response_text[json_start:json_end])
                        explanation = response_text[:json_start].strip()
                        milestones = self._normalize_milestones(milestones)
                    except Exception:
                        pass

            return {
                "response": explanation or "I understand. How would you like to proceed?",
                "milestones": milestones
            }

        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}. Could you rephrase your request?",
                "milestones": []
            }

    def _normalize_milestones(self, milestones: list) -> list:
        """Ensure IDs are valid UUIDs and hours are ints, add deadlines."""
        for m in milestones:
            if 'id' not in m or not m['id'] or len(str(m['id'])) < 10:
                m['id'] = str(uuid.uuid4())
            else:
                try:
                    uuid.UUID(str(m['id']))
                except (ValueError, AttributeError):
                    m['id'] = str(uuid.uuid4())

            if 'estimated_hours' in m:
                if isinstance(m['estimated_hours'], float):
                    m['estimated_hours'] = int(round(m['estimated_hours']))
                elif isinstance(m['estimated_hours'], str):
                    try:
                        m['estimated_hours'] = int(float(m['estimated_hours']))
                    except ValueError:
                        m['estimated_hours'] = 1
                m['deadline'] = self._calculate_deadline(m['estimated_hours'])
        return milestones
