from groq import Groq
import json
import uuid
from typing import List
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

# Words that indicate a requirement is NOT code-verifiable
_VAGUE_PATTERNS = re.compile(
    r'\b(user.friendly|easy to use|intuitive|seamless|beautiful|nice|clean|'
    r'good (ux|ui|experience|performance|design)|fast|secure system|'
    r'scalable|maintainable|readable|well.documented|best practices|'
    r'ensure|make sure|should be|must be (easy|simple|fast|secure))\b',
    re.IGNORECASE
)

_GENERATE_CHECKLIST_SYSTEM = """You are a senior software engineer breaking a project into implementation milestones for a developer freelance platform. Your output will be used to verify actual code submissions.

STRICT RULES:
1. Every milestone title must name a concrete technical component (e.g. "Implement JWT Authentication API", "Build PostgreSQL Schema & Migrations", "Create React Dashboard Component").
2. Every requirement must be a specific, code-verifiable deliverable — something an automated code reviewer can check by reading the source files.
3. Requirements MUST reference: function/method names, class names, API endpoint paths, database table/column names, file names, library names, or specific algorithms.
4. FORBIDDEN in requirements: "user-friendly", "easy to use", "intuitive", "good UX", "clean code", "best practices", "ensure security", "make it fast", or any subjective/non-code term.
5. Each milestone must represent a distinct, independently deliverable code module.
6. estimated_hours must be a realistic integer for a developer (not a project manager).

REQUIREMENT FORMAT — each item must follow one of these patterns:
- "Implement <FunctionName>() in <FileName> that <does specific thing>"
- "Create <ClassName> with methods: <method1>, <method2>"
- "Add <HTTP_METHOD> /<endpoint> endpoint that accepts <input> and returns <output>"
- "Create database migration adding <table>(<col1> <type>, <col2> <type>)"
- "Write unit tests for <function/class> covering <specific cases>"
- "Integrate <LibraryName> for <specific purpose> with config in <file>"

Return ONLY a valid JSON array. No markdown, no explanation, no extra text.

[
  {
    "id": "<uuid>",
    "title": "<Technical Component Name>",
    "description": "<What gets built and how — implementation details only>",
    "requirements": [
      "<specific code-verifiable deliverable>",
      "<specific code-verifiable deliverable>"
    ],
    "estimated_hours": <integer>
  }
]"""

_CHAT_SYSTEM = """You are a senior software architect helping a client plan a software project. The client may not be technical — your job is to ask simple, high-level questions about what they want to build, then translate their answers into a precise technical milestone checklist yourself.

## PHASE 1 — UNDERSTAND THE PROJECT (ask first, build later)

When a client gives a vague description, ask 2-3 short, plain-English questions to understand:
- What the product does and who uses it
- The main features or screens they need
- Any specific services they want (e.g. payments, maps, login with Google)
- Their deadline — when do they need this done?

Keep questions simple and friendly. Don't ask about tech stack, frameworks, or architecture — you will decide those yourself based on what they tell you.

Example: if they say "I want a travel website", ask:
- What can users do on it? (search flights, book hotels, share itineraries?)
- Do they need accounts/login?
- Any payment processing?
- When do you need this ready?

## PHASE 2 — GENERATE MILESTONES (once you understand the project)

Once you have a clear picture of the features and deadline, generate the technical milestone checklist. You choose the tech stack and architecture — pick sensible modern defaults (e.g. React + FastAPI, or Next.js + Supabase) unless the client specified something.

Rules for milestones:
1. Titles name a concrete technical component (e.g. "User Auth API", "Flight Search Integration", "Booking Database Schema").
2. Requirements are specific and code-verifiable — reference function names, endpoint paths, DB tables, library names, file names.
3. No vague language: no "user-friendly", "clean code", "best practices", "ensure security", "make it fast".
4. Hours should be realistic for a developer.
5. Space milestones to fit within the client's deadline.

## DEADLINE EXTRACTION
When the client gives a deadline or timeframe, extract it as:
<project_deadline>YYYY-MM-DDTHH:MM:SSZ</project_deadline>
Convert relative dates ("2 weeks", "end of March") to absolute ISO 8601 UTC.

## RESPONSE FORMAT
<explanation>
Your message to the client — questions, or a summary of what you're building before showing milestones
</explanation>

<project_deadline>ISO 8601 — only when client gave a deadline</project_deadline>

<milestones>
[JSON array — only when ready to generate]
</milestones>

Each milestone: { "id": "<uuid>", "title": "<string>", "description": "<string>", "requirements": ["<string>", ...], "estimated_hours": <int> }"""


class ArchitectAgent:
    def __init__(self, gemini_api_key: str = None, groq_api_key: str = None):
        api_key = groq_api_key or gemini_api_key
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.config = self._load_deadline_config()

    def _load_deadline_config(self) -> dict:
        try:
            with open('deadline_config.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("deadline_config.json issue (%s), using defaults", e)
        return {
            'hours_to_days_ratio': 1.0,
            'reputation_weights': {
                'on_time_bonus': 2, 'late_penalty': 5,
                'high_quality_bonus': 1, 'low_quality_penalty': 2
            }
        }

    def _calculate_deadline(self, estimated_hours: int) -> str:
        ratio = self.config.get('hours_to_days_ratio', 1.0)
        days = estimated_hours * ratio
        return (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

    def _chat(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def _scrub_requirements(self, requirements: list) -> list:
        """Remove or flag requirements that contain vague/non-technical language."""
        clean = []
        for req in requirements:
            if _VAGUE_PATTERNS.search(req):
                logger.warning("Dropping vague requirement: %s", req)
                continue
            if len(req.strip()) < 15:
                continue
            clean.append(req)
        # If scrubbing removed everything, keep originals (better than empty)
        return clean if clean else requirements

    def _extract_json_from_markdown(self, text: str) -> str:
        lines = text.split('\n')
        json_lines, in_block = [], False
        for line in lines:
            if line.strip().startswith('```'):
                in_block = not in_block
                continue
            if in_block or (not line.strip().startswith('```') and json_lines):
                json_lines.append(line)
        return '\n'.join(json_lines).strip()

    def _validate_milestone_schema(self, data: dict) -> bool:
        for field in ['title', 'description', 'requirements', 'estimated_hours']:
            if field not in data:
                return False
        if not isinstance(data['title'], str) or not data['title']:
            return False
        if not isinstance(data['requirements'], list) or not data['requirements']:
            return False
        if not isinstance(data['estimated_hours'], int) or data['estimated_hours'] <= 0:
            return False
        return True

    def _normalize_hours(self, data: dict) -> dict:
        h = data.get('estimated_hours', 1)
        if isinstance(h, float):
            data['estimated_hours'] = max(1, int(round(h)))
        elif isinstance(h, str):
            try:
                data['estimated_hours'] = max(1, int(float(h)))
            except ValueError:
                data['estimated_hours'] = 1
        return data

    def _ensure_uuid(self, data: dict) -> dict:
        mid = data.get('id', '')
        if not mid or len(str(mid)) < 10:
            data['id'] = str(uuid.uuid4())
        else:
            try:
                uuid.UUID(str(mid))
            except (ValueError, AttributeError):
                data['id'] = str(uuid.uuid4())
        return data

    def generate_checklist(self, prompt: str) -> List[dict]:
        """Convert a project description into technical, code-verifiable milestones."""
        try:
            raw = self._chat(_GENERATE_CHECKLIST_SYSTEM, f"Project description: {prompt}")

            if raw.startswith('```'):
                raw = self._extract_json_from_markdown(raw)

            milestones_data = json.loads(raw)

            validated = []
            for data in milestones_data:
                data = self._normalize_hours(data)
                if not self._validate_milestone_schema(data):
                    logger.warning("Skipping invalid milestone schema: %s", data.get('title'))
                    continue
                data = self._ensure_uuid(data)
                data['requirements'] = self._scrub_requirements(data['requirements'])
                data['deadline'] = self._calculate_deadline(data['estimated_hours'])
                validated.append(data)

            if not validated:
                raise ValueError("No valid milestones generated")

            return validated

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from Groq: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate checklist: {e}")

    def _extract_tag(self, text: str, tag: str) -> str:
        """Extract content between <tag> and </tag>."""
        open_tag = f"<{tag}>"
        close_tag = f"</{tag}>"
        if open_tag in text and close_tag in text:
            return text[text.find(open_tag) + len(open_tag):text.find(close_tag)].strip()
        return ""

    def chat_response(self, message: str, conversation_history: str = "",
                      current_milestones: List[dict] = None) -> dict:
        """Interactive chat for iterative milestone planning."""
        if current_milestones is None:
            current_milestones = []

        user_content = ""
        if conversation_history:
            user_content += f"Previous conversation:\n{conversation_history}\n\n"
        if current_milestones:
            user_content += f"Current milestones:\n{json.dumps(current_milestones, indent=2)}\n\n"
        user_content += f"Client message: {message}"

        try:
            response_text = self._chat(_CHAT_SYSTEM, user_content)

            explanation = self._extract_tag(response_text, "explanation")
            project_deadline = self._extract_tag(response_text, "project_deadline")
            milestones_raw = self._extract_tag(response_text, "milestones")

            # Fallback: if no tags, treat whole response as explanation
            if not explanation:
                explanation = response_text
                # Try to pull out a JSON array if present
                if '[' in response_text and ']' in response_text:
                    try:
                        s = response_text.find('[')
                        e = response_text.rfind(']') + 1
                        milestones_raw = response_text[s:e]
                        explanation = response_text[:s].strip()
                    except Exception:
                        pass

            milestones = []
            if milestones_raw:
                try:
                    milestones = self._normalize_milestones(json.loads(milestones_raw))
                    # If client provided a project deadline, distribute milestones within it
                    if project_deadline and milestones:
                        milestones = self._distribute_deadlines(milestones, project_deadline)
                except json.JSONDecodeError:
                    pass

            result = {
                "response": explanation or "Understood. What would you like to adjust?",
                "milestones": milestones
            }
            if project_deadline:
                result["project_deadline"] = project_deadline

            return result

        except Exception as e:
            return {
                "response": f"Error: {str(e)}. Please rephrase.",
                "milestones": []
            }

    def _distribute_deadlines(self, milestones: list, project_deadline: str) -> list:
        """Distribute milestone deadlines evenly within the project deadline."""
        try:
            end_dt = datetime.fromisoformat(project_deadline.replace('Z', '+00:00')).replace(tzinfo=None)
            now = datetime.utcnow()
            total_hours = sum(m.get('estimated_hours', 1) for m in milestones)
            total_duration = (end_dt - now).total_seconds() / 3600  # hours available

            if total_duration <= 0:
                return milestones  # deadline already passed, keep as-is

            cumulative = 0
            for m in milestones:
                hours = m.get('estimated_hours', 1)
                cumulative += hours
                fraction = cumulative / total_hours
                milestone_deadline = now + timedelta(hours=total_duration * fraction)
                m['deadline'] = milestone_deadline.isoformat() + 'Z'
            return milestones
        except Exception as e:
            logger.warning("Could not distribute deadlines: %s", e)
            return milestones

    def _normalize_milestones(self, milestones: list) -> list:
        result = []
        for m in milestones:
            m = self._normalize_hours(m)
            m = self._ensure_uuid(m)
            if 'requirements' in m:
                m['requirements'] = self._scrub_requirements(m['requirements'])
            if 'estimated_hours' in m:
                m['deadline'] = self._calculate_deadline(m['estimated_hours'])
            result.append(m)
        return result
