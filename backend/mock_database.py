from typing import Optional
import uuid
from datetime import datetime
from backend.models import InspectionResult, PFISnapshot


class MockDatabaseManager:
    """Mock database for testing without Supabase"""
    
    def __init__(self):
        self.projects = {}
        self.milestones = {}
        self.inspection_results = {}
        self.user_reputation = {}
    
    def create_project(self, user_id: str, title: str, description: str, milestones: list[dict]) -> str:
        """Create new project with milestones"""
        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        self.projects[project_id] = {
            "id": project_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "created_at": now,
            "updated_at": now,
            "milestones": []
        }
        
        for milestone in milestones:
            milestone_id = milestone.get("id", str(uuid.uuid4()))
            milestone_data = {
                "id": milestone_id,
                "project_id": project_id,
                "title": milestone["title"],
                "description": milestone["description"],
                "requirements": milestone["requirements"],
                "estimated_hours": milestone["estimated_hours"],
                "status": "PENDING",
                "created_at": now
            }
            self.milestones[milestone_id] = milestone_data
            self.projects[project_id]["milestones"].append(milestone_data)
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """Retrieve project with all milestones"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id].copy()
        project["milestones"] = []
        
        for milestone_id, milestone in self.milestones.items():
            if milestone["project_id"] == project_id:
                milestone_copy = milestone.copy()
                if milestone_id in self.inspection_results:
                    milestone_copy["inspection_result"] = self.inspection_results[milestone_id]
                project["milestones"].append(milestone_copy)
        
        return project
    
    def update_milestone_status(self, milestone_id: str, status: str) -> None:
        """Update milestone escrow status"""
        if milestone_id in self.milestones:
            self.milestones[milestone_id]["status"] = status
            if status == "LOCKED":
                self.milestones[milestone_id]["submitted_at"] = datetime.utcnow().isoformat()
    
    def get_milestone_status(self, milestone_id: str) -> Optional[str]:
        """Get current milestone status"""
        if milestone_id in self.milestones:
            return self.milestones[milestone_id]["status"]
        return None
    
    def delete_milestone(self, milestone_id: str) -> bool:
        """Delete milestone if not locked"""
        if milestone_id in self.milestones:
            status = self.milestones[milestone_id]["status"]
            if status != "PENDING":
                return False
            del self.milestones[milestone_id]
            return True
        return False
    
    def save_inspection_result(self, milestone_id: str, result: InspectionResult) -> None:
        """Save code inspection results"""
        self.inspection_results[milestone_id] = {
            "milestone_id": milestone_id,
            "passed": result.passed,
            "coverage_score": result.coverage_score,
            "feedback": result.feedback,
            "missing_requirements": result.missing_requirements,
            "analyzed_at": result.analyzed_at.isoformat(),
            "code_blob_hash": result.code_blob_hash
        }
    
    def update_user_reputation(self, user_id: str, pfi: float, snapshot: PFISnapshot) -> None:
        """Update user reputation score"""
        if user_id in self.user_reputation:
            current = self.user_reputation[user_id]
            history = current.get("reputation_history", [])
            history.append({
                "timestamp": snapshot.timestamp.isoformat(),
                "pfi_score": snapshot.pfi_score,
                "project_id": snapshot.project_id,
                "milestone_id": snapshot.milestone_id
            })
            current["current_pfi"] = pfi
            current["reputation_history"] = history
            current["updated_at"] = datetime.utcnow().isoformat()
        else:
            self.user_reputation[user_id] = {
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
            }
    
    def get_user_reputation(self, user_id: str) -> Optional[dict]:
        """Retrieve user reputation data"""
        return self.user_reputation.get(user_id)
    
    def increment_submission_counter(self, user_id: str, passed: bool) -> None:
        """Increment successful or failed submission counter"""
        if user_id not in self.user_reputation:
            self.user_reputation[user_id] = {
                "user_id": user_id,
                "current_pfi": 0,
                "total_projects": 0,
                "successful_submissions": 0,
                "failed_submissions": 0,
                "average_coverage": 0,
                "reputation_history": [],
                "updated_at": datetime.utcnow().isoformat()
            }
        
        field = "successful_submissions" if passed else "failed_submissions"
        self.user_reputation[user_id][field] += 1

    def get_projects_by_user(self, user_id: str) -> list:
        """Get all projects for a given user ID"""
        return [p for p in self.projects.values() if p.get("user_id") == user_id]

    def get_all_projects(self) -> list:
        """Get all projects with their milestones"""
        result = []
        for project_id, project in self.projects.items():
            p = project.copy()
            p["milestones"] = [
                m.copy() for m in self.milestones.values()
                if m["project_id"] == project_id
            ]
            result.append(p)
        # Sort newest first
        result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return result

    # ============================================
    # STUB METHODS FOR PAYOUT-REPUTATION-SYSTEM
    # ============================================

    def update_milestone_submission_time(self, milestone_id: str, submission_time: str) -> None:
        if milestone_id in self.milestones:
            self.milestones[milestone_id]["submission_time"] = submission_time

    def update_milestone_timeline_status(self, milestone_id: str, timeline_status: str) -> None:
        if milestone_id in self.milestones:
            self.milestones[milestone_id]["timeline_status"] = timeline_status

    def update_milestone_deadline(self, milestone_id: str, new_deadline: str) -> None:
        if milestone_id in self.milestones:
            self.milestones[milestone_id]["deadline"] = new_deadline

    def log_deadline_change(self, milestone_id: str, old_deadline, new_deadline: str,
                            changed_at: str, changed_by=None, reason=None) -> None:
        pass  # No-op in mock

    def get_milestone(self, milestone_id: str) -> Optional[dict]:
        return self.milestones.get(milestone_id)

    def update_user_reputation_score(self, user_id: str, new_score: float, events: list) -> None:
        if user_id not in self.user_reputation:
            self.user_reputation[user_id] = {
                "user_id": user_id, "reputation_score": new_score,
                "current_pfi": 0, "total_projects": 0,
                "successful_submissions": 0, "failed_submissions": 0,
                "average_coverage": 0, "total_on_time_deliveries": 0,
                "total_late_deliveries": 0, "reputation_history": [],
                "updated_at": datetime.utcnow().isoformat()
            }
        self.user_reputation[user_id]["reputation_score"] = new_score
        self.user_reputation[user_id].setdefault("reputation_history", []).extend(events)

    def increment_on_time_count(self, user_id: str) -> None:
        if user_id in self.user_reputation:
            self.user_reputation[user_id]["total_on_time_deliveries"] = \
                self.user_reputation[user_id].get("total_on_time_deliveries", 0) + 1

    def increment_late_count(self, user_id: str) -> None:
        if user_id in self.user_reputation:
            self.user_reputation[user_id]["total_late_deliveries"] = \
                self.user_reputation[user_id].get("total_late_deliveries", 0) + 1
