from supabase import create_client, Client
from typing import Optional
import uuid
from datetime import datetime
from backend.models import InspectionResult, UserReputation, PFISnapshot


class DatabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client with connection pooling"""
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def create_project(self, user_id: str, title: str, description: str, milestones: list[dict],
                       developer_id: str = None) -> str:
        """Create new project with milestones in a single transaction"""
        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Snapshot the developer's hourly rate at project creation time
        developer_hourly_rate = None
        if developer_id:
            dev = self.get_user_by_id(developer_id)
            if dev:
                developer_hourly_rate = dev.get("hourly_rate")

        # Insert project
        project_data = {
            "id": project_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "developer_hourly_rate": developer_hourly_rate,
            "created_at": now,
            "updated_at": now
        }
        if developer_id:
            project_data["assigned_developer_id"] = developer_id
        
        self.client.table("projects").insert(project_data).execute()
        
        # Insert milestones
        for milestone in milestones:
            milestone_data = {
                "id": milestone.get("id", str(uuid.uuid4())),
                "project_id": project_id,
                "title": milestone["title"],
                "description": milestone["description"],
                "requirements": milestone["requirements"],
                "estimated_hours": milestone["estimated_hours"],
                "status": "PENDING",
                "deadline": milestone.get("deadline"),  # NEW: Include deadline if provided
                "created_at": now
            }
            self.client.table("milestones").insert(milestone_data).execute()
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """Retrieve project with all milestones"""
        # Get project
        project_response = self.client.table("projects").select("*").eq("id", project_id).execute()
        
        if not project_response.data:
            return None
        
        project = project_response.data[0]
        
        # Get milestones
        milestones_response = self.client.table("milestones").select("*").eq("project_id", project_id).execute()
        project["milestones"] = milestones_response.data
        
        # Get inspection results for each milestone
        for milestone in project["milestones"]:
            inspection_response = self.client.table("inspection_results").select("*").eq("milestone_id", milestone["id"]).execute()
            if inspection_response.data:
                milestone["inspection_result"] = inspection_response.data[0]
        
        return project
    
    def update_milestone_status(self, milestone_id: str, status: str) -> None:
        """Update milestone escrow status"""
        self.client.table("milestones").update({
            "status": status,
            "submitted_at": datetime.utcnow().isoformat() if status == "LOCKED" else None
        }).eq("id", milestone_id).execute()
    
    def get_milestone_status(self, milestone_id: str) -> Optional[str]:
        """Get current milestone status"""
        response = self.client.table("milestones").select("status").eq("id", milestone_id).execute()
        if response.data:
            return response.data[0]["status"]
        return None
    
    def delete_milestone(self, milestone_id: str) -> bool:
        """Delete milestone if not locked"""
        status = self.get_milestone_status(milestone_id)
        if status and status != "PENDING":
            return False
        
        self.client.table("milestones").delete().eq("id", milestone_id).execute()
        return True
    
    def save_inspection_result(self, milestone_id: str, result: InspectionResult) -> None:
        """Save code inspection results"""
        result_data = {
            "milestone_id": milestone_id,
            "passed": result.passed,
            "coverage_score": result.coverage_score,
            "feedback": result.feedback,
            "missing_requirements": result.missing_requirements,
            "analyzed_at": result.analyzed_at.isoformat(),
            "code_blob_hash": result.code_blob_hash
        }
        self.client.table("inspection_results").insert(result_data).execute()
    
    def update_user_reputation(self, user_id: str, pfi: float, snapshot: PFISnapshot) -> None:
        """Update user reputation score"""
        # Get current reputation
        response = self.client.table("user_reputation").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            # Update existing
            current = response.data[0]
            history = current.get("reputation_history", [])
            history.append({
                "timestamp": snapshot.timestamp.isoformat(),
                "pfi_score": snapshot.pfi_score,
                "project_id": snapshot.project_id,
                "milestone_id": snapshot.milestone_id
            })
            
            self.client.table("user_reputation").update({
                "current_pfi": pfi,
                "reputation_history": history,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
        else:
            # Create new
            self.client.table("user_reputation").insert({
                "user_id": user_id,
                "current_pfi": pfi,
                "total_projects": 0,
                "successful_submissions": 0,
                "failed_submissions": 0,
                "average_coverage": 0,
                "reputation_history": [{
                    "timestamp": snapshot.timestamp.isoformat(),
                    "pfi_score": snapshot.pfi_score,
                    "project_id": snapshot.project_id,
                    "milestone_id": snapshot.milestone_id
                }],
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
    
    def get_user_reputation(self, user_id: str) -> Optional[dict]:
        """Retrieve user reputation data"""
        response = self.client.table("user_reputation").select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    
    def increment_submission_counter(self, user_id: str, passed: bool) -> None:
        """Increment successful or failed submission counter"""
        reputation = self.get_user_reputation(user_id)
        if reputation:
            field = "successful_submissions" if passed else "failed_submissions"
            self.client.table("user_reputation").update({
                field: reputation[field] + 1
            }).eq("user_id", user_id).execute()
    
    # ============================================
    # NEW METHODS FOR PAYOUT-REPUTATION-SYSTEM
    # ============================================
    
    def update_milestone_submission_time(self, milestone_id: str, submission_time: str) -> None:
        """Update milestone submission time (ISO 8601 timestamp)"""
        self.client.table("milestones").update({
            "submission_time": submission_time
        }).eq("id", milestone_id).execute()
    
    def update_milestone_timeline_status(self, milestone_id: str, timeline_status: str) -> None:
        """Update milestone timeline status ('on-time' or 'late')"""
        self.client.table("milestones").update({
            "timeline_status": timeline_status
        }).eq("id", milestone_id).execute()
    
    def update_milestone_deadline(self, milestone_id: str, new_deadline: str) -> None:
        """Update milestone deadline (ISO 8601 timestamp)"""
        self.client.table("milestones").update({
            "deadline": new_deadline
        }).eq("id", milestone_id).execute()
    
    def log_deadline_change(self, milestone_id: str, old_deadline: Optional[str], 
                           new_deadline: str, changed_at: str, changed_by: Optional[str] = None,
                           reason: Optional[str] = None) -> None:
        """Log deadline change to audit trail"""
        audit_data = {
            "milestone_id": milestone_id,
            "old_deadline": old_deadline,
            "new_deadline": new_deadline,
            "changed_at": changed_at,
            "changed_by": changed_by,
            "reason": reason
        }
        self.client.table("deadline_audit").insert(audit_data).execute()
    
    def get_milestone(self, milestone_id: str) -> Optional[dict]:
        """Get full milestone data including deadline and timeline fields"""
        response = self.client.table("milestones").select("*").eq("id", milestone_id).execute()
        if response.data:
            return response.data[0]
        return None
    
    def update_user_reputation_score(self, user_id: str, new_score: float, events: list[dict]) -> None:
        """Update user reputation score and append history events"""
        reputation = self.get_user_reputation(user_id)
        
        if reputation:
            # Update existing reputation
            history = reputation.get("reputation_history", [])
            history.extend(events)
            
            self.client.table("user_reputation").update({
                "reputation_score": new_score,
                "reputation_history": history,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
        else:
            # Create new reputation record with initial score
            self.client.table("user_reputation").insert({
                "user_id": user_id,
                "reputation_score": new_score,
                "current_pfi": 0,
                "total_projects": 0,
                "successful_submissions": 0,
                "failed_submissions": 0,
                "average_coverage": 0,
                "total_on_time_deliveries": 0,
                "total_late_deliveries": 0,
                "reputation_history": events,
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
    
    def increment_on_time_count(self, user_id: str) -> None:
        """Increment on-time delivery counter"""
        reputation = self.get_user_reputation(user_id)
        if reputation:
            self.client.table("user_reputation").update({
                "total_on_time_deliveries": reputation.get("total_on_time_deliveries", 0) + 1
            }).eq("user_id", user_id).execute()
    
    def increment_late_count(self, user_id: str) -> None:
        """Increment late delivery counter"""
        reputation = self.get_user_reputation(user_id)
        if reputation:
            self.client.table("user_reputation").update({
                "total_late_deliveries": reputation.get("total_late_deliveries", 0) + 1
            }).eq("user_id", user_id).execute()

    def save_submission_source(self, milestone_id: str, source: str,
                                files: list = None, github_url: str = None) -> None:
        """Save submission source metadata to milestone (local files or github url)"""
        import json
        data = {"submission_source": source}
        if source == "github" and github_url:
            data["submission_github_url"] = github_url
        elif source == "local" and files:
            # Store as JSON: list of {name, content}
            data["submission_files"] = json.dumps(files)
        self.client.table("milestones").update(data).eq("id", milestone_id).execute()

    def get_projects_by_user(self, user_id: str) -> list:
        """Get all projects for a given user ID"""
        response = self.client.table("projects").select("*").eq("user_id", user_id).execute()
        projects = response.data or []
        for project in projects:
            milestones_response = self.client.table("milestones").select("*").eq("project_id", project["id"]).execute()
            project["milestones"] = milestones_response.data or []
        return projects

    def get_all_projects(self) -> list:
        """Get all projects with their milestones"""
        response = self.client.table("projects").select("*").order("created_at", desc=True).execute()
        projects = response.data or []
        for project in projects:
            milestones_response = self.client.table("milestones").select("*").eq("project_id", project["id"]).execute()
            project["milestones"] = milestones_response.data or []
        return projects

    # ============================================
    # AUTH METHODS
    # ============================================

    def create_user(self, user_id: str, name: str, email: str, password_hash: str,
                    role: str, payment_threshold: float = None) -> dict:
        """Create a new user account"""
        now = datetime.utcnow().isoformat()
        hourly_rate = round(payment_threshold / 160, 2) if payment_threshold else None
        data = {
            "id": user_id,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "payment_threshold": payment_threshold,
            "hourly_rate": hourly_rate,
            "created_at": now
        }
        self.client.table("users").insert(data).execute()
        return data

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Fetch user by email"""
        response = self.client.table("users").select("*").eq("email", email).execute()
        if response.data:
            return response.data[0]
        return None

    def get_all_developers(self) -> list:
        """Get all users with role='developer'"""
        response = self.client.table("users").select("id,name,email,payment_threshold,hourly_rate,created_at").eq("role", "developer").execute()
        return response.data or []

    def get_projects_by_developer(self, developer_id: str) -> list:
        """Get all projects assigned to a developer, with milestones and client info"""
        response = self.client.table("projects").select("*").eq("assigned_developer_id", developer_id).order("created_at", desc=True).execute()
        projects = response.data or []
        for project in projects:
            milestones_response = self.client.table("milestones").select("*").eq("project_id", project["id"]).execute()
            project["milestones"] = milestones_response.data or []
            # Fetch client name
            client = self.get_user_by_id(project["user_id"])
            project["client_name"] = client["name"] if client else "Unknown"
        return projects

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Fetch user by ID"""
        response = self.client.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
