from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
import os
import sys
import logging
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import PlanRequest, PlanResponse, SubmitResponse, EscrowStatus
try:
    from backend.database import DatabaseManager
except ImportError:
    DatabaseManager = None
from agents.architect import ArchitectAgent
from agents.banker import BankerAgent
from agents.inspector import InspectorAgent
from agents.bureau import BureauAgent
from utils.file_processor import validate_file_types, validate_file_sizes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('gemini_api_key')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize database (will use mock if Supabase not configured)
db = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        # Check if it's the service role key or anon key
        if 'sb_publishable' in SUPABASE_KEY:
            logger.warning("Using publishable key - switching to anon key format")
            # Extract the actual key part after the prefix
            SUPABASE_KEY = SUPABASE_KEY.replace('sb_publishable_', '')
        
        from backend.database import DatabaseManager
        db = DatabaseManager(supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY)
        logger.info("✅ Connected to Supabase database")
    else:
        raise ImportError("Supabase credentials not configured")
except (ImportError, Exception) as e:
    logger.warning(f"⚠️  Supabase not available ({e}), using mock database")
    from backend.mock_database import MockDatabaseManager
    db = MockDatabaseManager()
    logger.info("Using mock database for development")

# Initialize agents
architect = ArchitectAgent(gemini_api_key=GEMINI_API_KEY)

# NEW: Initialize Reputation Manager
from agents.reputation_manager import ReputationManager
reputation_manager = ReputationManager(db_connection=db)

# Initialize Banker with Reputation Manager
banker = BankerAgent(db_connection=db, reputation_manager=reputation_manager)

inspector = InspectorAgent(gemini_api_key=GEMINI_API_KEY)
bureau = BureauAgent(db_connection=db)

# Create FastAPI app
app = FastAPI(title="Pillar Protocol API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.get("/")
async def root():
    """Serve the main HTML page"""
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "message": "Pillar Protocol API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Pillar Protocol API is running"}


@app.get("/script.js")
async def serve_script():
    """Serve the JavaScript file"""
    script_path = os.path.join(BASE_DIR, "script.js")
    if os.path.exists(script_path):
        return FileResponse(script_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Script not found")


@app.get("/style.css")
async def serve_style():
    """Serve the CSS file"""
    style_path = os.path.join(BASE_DIR, "style.css")
    if os.path.exists(style_path):
        return FileResponse(style_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="Style not found")


@app.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """Convert vague prompt into structured milestone checklist"""
    try:
        logger.info(f"Creating plan for user {request.user_id}")
        
        # Generate milestones using Architect
        milestones = architect.generate_checklist(request.prompt)
        
        # Extract title from first milestone or use prompt
        title = milestones[0]["title"] if milestones else "New Project"
        description = request.prompt
        
        # Save to database
        project_id = db.create_project(
            user_id=request.user_id,
            title=title,
            description=description,
            milestones=milestones
        )
        
        logger.info(f"Created project {project_id} with {len(milestones)} milestones")
        
        return PlanResponse(
            project_id=project_id,
            milestones=milestones
        )
        
    except ValueError as e:
        logger.error(f"Failed to generate plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_plan: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/chat/architect")
async def chat_with_architect(request: dict):
    """Interactive chat with Architect Agent for iterative planning"""
    try:
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", "")
        current_milestones = request.get("current_milestones", [])
        
        logger.info(f"Chat message: {message[:50]}...")
        
        # Generate response using Architect with conversation context
        response_data = architect.chat_response(
            message=message,
            conversation_history=conversation_history,
            current_milestones=current_milestones
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in chat_with_architect: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/plan/finalize")
async def finalize_plan(request: dict):
    """Finalize the checklist and create project in database"""
    try:
        user_id = request.get("user_id")
        milestones = request.get("milestones", [])
        
        if not milestones:
            raise HTTPException(status_code=400, detail="No milestones to finalize")
        
        # Extract title from first milestone
        title = milestones[0].get("title", "New Project")
        description = f"Project with {len(milestones)} milestones"
        
        # Save to database
        project_id = db.create_project(
            user_id=user_id,
            title=title,
            description=description,
            milestones=milestones
        )
        
        logger.info(f"Finalized project {project_id}")
        
        return {
            "project_id": project_id,
            "status": "finalized",
            "milestones_count": len(milestones)
        }
        
    except Exception as e:
        logger.error(f"Error in finalize_plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to finalize: {str(e)}")


@app.get("/estimate/{project_id}")
async def get_estimate(project_id: str):
    """Calculate estimated price for project"""
    try:
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Calculate total hours
        total_hours = sum(m.get("estimated_hours", 0) for m in project["milestones"])
        
        # Default hourly rate
        hourly_rate = 50
        total_price = total_hours * hourly_rate
        
        return {
            "project_id": project_id,
            "total_hours": total_hours,
            "hourly_rate": hourly_rate,
            "total_price": total_price,
            "milestones_count": len(project["milestones"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_estimate: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate estimate")


@app.post("/payment/confirm")
async def confirm_payment(request: dict):
    """Confirm payment - milestones remain PENDING until code submission"""
    try:
        project_id = request.get("project_id")
        amount = request.get("amount")
        card_last4 = request.get("card_last4", "****")
        
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Simulate payment processing
        transaction_id = f"txn_{project_id[:8]}_{card_last4}"
        
        # NOTE: Milestones are NOT locked here
        # They remain in PENDING state until code is actually submitted
        # This allows developers to submit code for each milestone independently
        
        logger.info(f"Payment confirmed for project {project_id}: ${amount}")
        logger.info(f"Milestones remain PENDING - ready for code submission")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount,
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in confirm_payment: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed")


@app.post("/github/fetch")
async def fetch_github_repo(request: dict):
    """Fetch code files from GitHub repository (recursively explores all folders)"""
    try:
        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        owner = request.get("owner")
        repo = request.get("repo")
        branch = request.get("branch", "main")
        path = request.get("path", "")
        
        logger.info(f"Fetching GitHub repo: {owner}/{repo}, branch: {branch}, path: {path}")
        
        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Owner and repo are required")
        
        code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.jsx', '.tsx', '.html', '.css']
        skip_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next', 'target'}
        
        headers = {}
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        def fetch_tree():
            """Use Git Trees API to get all files in one request"""
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            resp = requests.get(tree_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if not data.get('truncated'):
                    return data.get('tree', [])
            return None
        
        def fetch_file_content(file_url):
            try:
                resp = requests.get(file_url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    file_data = resp.json()
                    if file_data.get('encoding') == 'base64':
                        import base64
                        return base64.b64decode(file_data['content']).decode('utf-8', errors='replace')
            except Exception as e:
                logger.error(f"Error fetching {file_url}: {e}")
            return None
        
        files = []
        folders_explored = 0
        
        # Try fast path: Git Trees API (single request for entire repo)
        tree = fetch_tree()
        
        if tree is not None:
            # Filter to code files, skip excluded dirs
            candidate_files = []
            for item in tree:
                if item['type'] != 'blob':
                    continue
                file_path = item['path']
                # Skip if any path component is in skip_dirs
                parts = file_path.split('/')
                if any(p in skip_dirs for p in parts[:-1]):
                    continue
                if path and not file_path.startswith(path):
                    continue
                if any(file_path.endswith(ext) for ext in code_extensions):
                    candidate_files.append(item)
            
            folders_explored = len(set('/'.join(f['path'].split('/')[:-1]) for f in candidate_files)) + 1
            
            # Fetch file contents in parallel (max 20 workers, limit 80 files)
            candidate_files = candidate_files[:80]
            
            def fetch_one(item):
                content_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}?ref={branch}"
                content = fetch_file_content(content_url)
                if content:
                    return {
                        'name': item['path'].split('/')[-1],
                        'path': item['path'],
                        'content': content
                    }
                return None
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(fetch_one, item): item for item in candidate_files}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        files.append(result)
        
        else:
            # Fallback: recursive directory exploration
            def explore_directory(dir_path=""):
                nonlocal folders_explored
                folders_explored += 1
                if folders_explored > 50:
                    return
                
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{dir_path}"
                try:
                    resp = requests.get(api_url, params={"ref": branch}, headers=headers, timeout=15)
                    if resp.status_code == 404 and dir_path == "":
                        raise HTTPException(status_code=404, detail=f"Repository not found: {owner}/{repo}")
                    if resp.status_code == 403:
                        raise HTTPException(status_code=403, detail="GitHub API rate limit exceeded.")
                    if resp.status_code != 200:
                        return
                    
                    contents = resp.json()
                    if not isinstance(contents, list):
                        return
                    
                    file_items = []
                    for item in contents:
                        if item['type'] == 'dir' and item['name'] not in skip_dirs:
                            explore_directory(item['path'])
                        elif item['type'] == 'file' and any(item['name'].endswith(ext) for ext in code_extensions):
                            file_items.append(item)
                    
                    def fetch_one(item):
                        content = fetch_file_content(item['url'])
                        if content:
                            return {'name': item['name'], 'path': item['path'], 'content': content}
                        return None
                    
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        for result in executor.map(fetch_one, file_items):
                            if result:
                                files.append(result)
                
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error exploring {dir_path}: {e}")
            
            explore_directory(path)
        
        logger.info(f"Fetched {len(files)} files from {owner}/{repo} (explored ~{folders_explored} folders)")
        
        return {
            "files": files,
            "count": len(files),
            "repo": f"{owner}/{repo}",
            "branch": branch,
            "folders_explored": folders_explored
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in fetch_github_repo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch repository: {str(e)}")


@app.post("/submit", response_model=SubmitResponse)
async def submit_code(
    project_id: str = Form(...),
    milestone_id: str = Form(...),
    files: List[UploadFile] = File(default=None),
    github_files: str = Form(default=None)
):
    """Analyze uploaded code or GitHub files against checklist"""
    try:
        logger.info(f"Code submission for milestone {milestone_id} in project {project_id}")
        
        # Handle GitHub files or uploaded files
        if github_files:
            import json
            from io import BytesIO
            
            github_files_data = json.loads(github_files)
            
            # Convert GitHub files to UploadFile-like objects
            # Create a custom class that mimics UploadFile behavior
            class GitHubFile:
                def __init__(self, filename, content):
                    self.filename = filename
                    self.content_bytes = content.encode('utf-8')
                    self.file = BytesIO(self.content_bytes)
                
                async def read(self):
                    return self.content_bytes
                
                async def seek(self, position):
                    self.file.seek(position)
            
            files = []
            for file_data in github_files_data:
                files.append(GitHubFile(
                    filename=file_data['name'],
                    content=file_data['content']
                ))
        
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Validate file types (skip for GitHub files)
        if not github_files:
            valid, error_msg = validate_file_types(files)
            if not valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Validate file sizes
            valid, error_msg = await validate_file_sizes(files)
            if not valid:
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Get project and milestone
        project = db.get_project(project_id)
        if not project:
            logger.error(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
        
        logger.info(f"Project found: {project['title']}, Milestones: {len(project['milestones'])}")
        
        # Debug: Log all milestone IDs
        milestone_ids = [m["id"] for m in project["milestones"]]
        logger.info(f"Available milestone IDs: {milestone_ids}")
        logger.info(f"Looking for milestone ID: {milestone_id}")
        
        milestone = next((m for m in project["milestones"] if m["id"] == milestone_id), None)
        if not milestone:
            # Provide helpful error message
            available_ids = ", ".join(milestone_ids[:3])  # Show first 3 IDs
            error_msg = f"Milestone ID '{milestone_id}' not found in project. Available IDs: {available_ids}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        
        logger.info(f"Milestone found: {milestone['title']}")
        
        # Check milestone status before locking
        current_status = banker.get_milestone_status(milestone_id)
        if current_status and current_status != EscrowStatus.PENDING:
            # Special case: If milestone has been LOCKED for more than 5 minutes, auto-unlock it
            if current_status == EscrowStatus.LOCKED:
                milestone_data = db.get_milestone(milestone_id)
                if milestone_data and milestone_data.get('submission_time'):
                    from datetime import datetime, timedelta
                    try:
                        submission_time = datetime.fromisoformat(milestone_data['submission_time'].replace('Z', '+00:00'))
                        time_locked = datetime.utcnow() - submission_time.replace(tzinfo=None)
                        
                        # If locked for more than 5 minutes, auto-unlock
                        if time_locked > timedelta(minutes=5):
                            logger.warning(f"Milestone {milestone_id} has been LOCKED for {time_locked.total_seconds()/60:.1f} minutes. Auto-unlocking...")
                            db.update_milestone_status(milestone_id, EscrowStatus.PENDING.value)
                            logger.info(f"Milestone {milestone_id} auto-unlocked due to timeout")
                            # Continue with submission
                            current_status = EscrowStatus.PENDING
                    except Exception as e:
                        logger.error(f"Error checking lock timeout: {e}")
            
            # If still not PENDING, reject the submission
            if current_status != EscrowStatus.PENDING:
                status_messages = {
                    EscrowStatus.LOCKED: f"This milestone is currently LOCKED (under review). If this is stuck, use the 'View Project' tab to check the milestone status, or contact support to unlock it. Milestone ID: {milestone_id}",
                    EscrowStatus.RELEASED: "This milestone has already been completed and payment released. Completed milestones cannot accept new submissions.",
                    EscrowStatus.DISPUTED: "This milestone is disputed. Please resolve the dispute before submitting new code."
                }
                error_msg = status_messages.get(current_status, f"Cannot submit: milestone is {current_status.value}")
                logger.warning(f"Submission rejected - Milestone {milestone_id} status: {current_status.value}")
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Lock milestone for inspection
        lock_success = banker.lock_milestone(milestone_id)
        if not lock_success:
            current_status_after = banker.get_milestone_status(milestone_id)
            error_detail = f"Failed to lock milestone. Current status: {current_status_after.value if current_status_after else 'UNKNOWN'}. The milestone must be in PENDING state to accept submissions."
            logger.error(f"Lock failed for milestone {milestone_id}: {error_detail}")
            raise HTTPException(status_code=400, detail=error_detail)
        
        try:
            # Analyze code
            logger.info(f"Starting code analysis for milestone {milestone_id} with {len(files)} files")
            inspection_result = await inspector.analyze_code(files, [milestone])
            logger.info(f"Code analysis completed: passed={inspection_result.passed}, coverage={inspection_result.coverage_score}")
            
            # Save inspection result
            db.save_inspection_result(milestone_id, inspection_result)
            
            # Update submission counter
            db.increment_submission_counter(project["user_id"], inspection_result.passed)
            
            pfi_score = None
            reputation_change = None
            
            # If passed, calculate PFI and release payment
            if inspection_result.passed:
                pfi_metrics = bureau.calculate_pfi(
                    project_id=project_id,
                    user_id=project["user_id"],
                    inspection_result=inspection_result
                )
                
                bureau.update_reputation(
                    user_id=project["user_id"],
                    pfi=pfi_metrics,
                    project_id=project_id,
                    milestone_id=milestone_id
                )
                
                # NEW: Pass user_id and pfi_score to release_payment for reputation tracking
                pfi_score = pfi_metrics.combined_pfi
                payment_result = banker.release_payment(
                    milestone_id=milestone_id,
                    user_id=project["user_id"],
                    pfi_score=pfi_score
                )
                
                # Extract reputation change from payment result
                if isinstance(payment_result, dict):
                    reputation_change = payment_result.get('reputation_change')
                
                logger.info(f"Inspection PASSED - Milestone {milestone_id} released, PFI: {pfi_score}")
                if reputation_change:
                    logger.info(f"Reputation change: {reputation_change}")
            else:
                # If failed, unlock milestone so developer can resubmit
                db.update_milestone_status(milestone_id, EscrowStatus.PENDING.value)
                logger.info(f"Inspection FAILED - Milestone {milestone_id} unlocked for resubmission")
                logger.info(f"Developer can now submit new code for milestone {milestone_id}")
            
            logger.info(f"Submission result: passed={inspection_result.passed}, pfi={pfi_score}")
            
            return SubmitResponse(
                passed=inspection_result.passed,
                feedback=inspection_result.feedback,
                pfi_score=pfi_score,
                reputation_change=reputation_change  # NEW: Include reputation change
            )
            
        except Exception as inspection_error:
            # If inspection fails, unlock the milestone so user can try again
            logger.error(f"Inspection failed with error: {inspection_error}", exc_info=True)
            db.update_milestone_status(milestone_id, EscrowStatus.PENDING.value)
            logger.info(f"Milestone {milestone_id} unlocked due to inspection error")
            raise HTTPException(
                status_code=500, 
                detail=f"Code inspection failed: {str(inspection_error)}. Milestone has been unlocked - you can try submitting again."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")


@app.get("/project/{project_id}")
async def get_project(project_id: str):
    """Retrieve project state and milestones"""
    try:
        from datetime import datetime
        
        project = db.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Enhance milestones with deadline and days_remaining
        current_time = datetime.utcnow()
        for milestone in project.get("milestones", []):
            deadline_str = milestone.get("deadline")
            if deadline_str:
                try:
                    # Parse ISO 8601 timestamp
                    deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                    # Calculate days remaining
                    time_delta = deadline_dt.replace(tzinfo=None) - current_time
                    days_remaining = time_delta.days
                    milestone["days_remaining"] = days_remaining
                    milestone["overdue"] = days_remaining < 0
                except (ValueError, AttributeError):
                    # Invalid deadline format, skip calculation
                    milestone["days_remaining"] = None
                    milestone["overdue"] = False
            else:
                # No deadline set
                milestone["days_remaining"] = None
                milestone["overdue"] = False
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_project: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")


@app.get("/milestone/{milestone_id}/status")
async def get_milestone_status(milestone_id: str):
    """Get detailed milestone status information"""
    try:
        status = banker.get_milestone_status(milestone_id)
        if not status:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        status_info = {
            "milestone_id": milestone_id,
            "status": status.value,
            "can_submit": status == EscrowStatus.PENDING,
            "can_delete": status == EscrowStatus.PENDING,
            "description": {
                "PENDING": "Ready for code submission",
                "LOCKED": "Under review - code has been submitted and is being analyzed",
                "RELEASED": "Completed - payment has been released",
                "DISPUTED": "Disputed - requires resolution"
            }.get(status.value, "Unknown status")
        }
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting milestone status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get milestone status")


@app.delete("/milestone/{milestone_id}")
async def delete_milestone(milestone_id: str):
    """Delete milestone if not locked"""
    try:
        if not banker.can_delete_milestone(milestone_id):
            raise HTTPException(status_code=403, detail="Cannot delete locked milestone")
        
        success = db.delete_milestone(milestone_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete milestone")
        
        return {"status": "success", "message": "Milestone deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_milestone: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete milestone")


@app.post("/milestone/{milestone_id}/unlock")
async def unlock_milestone(milestone_id: str):
    """
    Unlock a stuck milestone (reset from LOCKED to PENDING)
    
    Use this if a milestone is stuck in LOCKED state due to a failed submission.
    """
    try:
        # Get current status
        current_status = banker.get_milestone_status(milestone_id)
        if not current_status:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        if current_status == EscrowStatus.RELEASED:
            raise HTTPException(
                status_code=400,
                detail="Cannot unlock a RELEASED milestone. Payment has already been released."
            )
        
        if current_status == EscrowStatus.PENDING:
            return {
                "status": "success",
                "message": "Milestone is already in PENDING state",
                "milestone_id": milestone_id,
                "previous_status": current_status.value,
                "new_status": "PENDING"
            }
        
        # Unlock the milestone by setting it back to PENDING
        db.update_milestone_status(milestone_id, EscrowStatus.PENDING.value)
        
        logger.info(f"Milestone {milestone_id} unlocked: {current_status.value} -> PENDING")
        
        return {
            "status": "success",
            "message": f"Milestone unlocked successfully. You can now submit code again.",
            "milestone_id": milestone_id,
            "previous_status": current_status.value,
            "new_status": "PENDING"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking milestone: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unlock milestone: {str(e)}")


@app.get("/reputation/{user_id}")
async def get_reputation(user_id: str):
    """
    Get user reputation and history
    
    NEW: Returns comprehensive reputation data including timeline metrics
    """
    try:
        reputation_data = reputation_manager.get_reputation(user_id)
        return reputation_data
        
    except Exception as e:
        logger.error(f"Error in get_reputation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reputation")


@app.patch("/milestone/{milestone_id}/deadline")
async def adjust_deadline(milestone_id: str, request: dict):
    """
    Adjust milestone deadline
    
    Request body:
    {
        "new_deadline": "2024-02-01T23:59:59Z",
        "reason": "Scope changed" (optional)
    }
    """
    try:
        new_deadline = request.get('new_deadline')
        reason = request.get('reason')
        
        if not new_deadline:
            raise HTTPException(status_code=400, detail="new_deadline is required")
        
        # Validate ISO 8601 format
        try:
            from datetime import datetime
            datetime.fromisoformat(new_deadline.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ISO 8601 timestamp format")
        
        # Get milestone
        milestone = db.get_milestone(milestone_id)
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        # Check if milestone is released
        if milestone.get('status') == EscrowStatus.RELEASED.value:
            raise HTTPException(
                status_code=400,
                detail="Cannot adjust deadline for released milestone"
            )
        
        # Update deadline and log audit trail
        old_deadline = milestone.get('deadline')
        changed_at = datetime.utcnow().isoformat() + 'Z'
        
        db.update_milestone_deadline(milestone_id, new_deadline)
        db.log_deadline_change(
            milestone_id=milestone_id,
            old_deadline=old_deadline,
            new_deadline=new_deadline,
            changed_at=changed_at,
            reason=reason
        )
        
        logger.info(f"Deadline adjusted for milestone {milestone_id}: {old_deadline} -> {new_deadline}")
        
        return {
            'status': 'success',
            'milestone_id': milestone_id,
            'old_deadline': old_deadline,
            'new_deadline': new_deadline,
            'changed_at': changed_at,
            'reason': reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting deadline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to adjust deadline: {str(e)}")


@app.get("/projects/all")
async def get_all_projects():
    """Get all projects with milestones (for developer dashboard)"""
    try:
        projects = db.get_all_projects()
        return projects or []
    except Exception as e:
        logger.error(f"Error in get_all_projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")


@app.get("/projects/{user_id}")
async def get_projects_by_user(user_id: str):
    """Get all projects for a given user ID"""
    try:
        projects = db.get_projects_by_user(user_id)
        return projects or []
    except Exception as e:
        logger.error(f"Error in get_projects_by_user: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
