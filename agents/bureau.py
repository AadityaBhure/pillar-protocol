from backend.models import PFIMetrics, InspectionResult, PFISnapshot
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BureauAgent:
    def __init__(self, db_connection):
        """Initialize with database connection"""
        self.db = db_connection
    
    def calculate_pfi(
        self,
        project_id: str,
        user_id: str,
        inspection_result: InspectionResult
    ) -> PFIMetrics:
        """
        Calculate Performance/Financial Index.
        Triggered post-submission.
        """
        # Get project and user data
        project = self.db.get_project(project_id)
        user_reputation = self.db.get_user_reputation(user_id)
        
        # Calculate performance score (based on code quality)
        performance_score = inspection_result.coverage_score
        
        # Adjust for historical performance
        if user_reputation and user_reputation.get("total_projects", 0) > 0:
            historical_weight = 0.3
            avg_coverage = user_reputation.get("average_coverage", 0)
            performance_score = (
                performance_score * (1 - historical_weight) +
                avg_coverage * historical_weight
            )
        
        # Ensure bounds
        performance_score = max(0, min(100, performance_score))
        
        # Calculate financial score (based on completion rate)
        total_milestones = len(project.get("milestones", []))
        completed_milestones = sum(
            1 for m in project.get("milestones", []) if m.get("status") == "RELEASED"
        )
        
        if total_milestones > 0:
            completion_rate = completed_milestones / total_milestones
            financial_score = completion_rate * 100
        else:
            financial_score = 0
        
        # Adjust for success rate
        if user_reputation and user_reputation.get("total_projects", 0) > 0:
            successful = user_reputation.get("successful_submissions", 0)
            failed = user_reputation.get("failed_submissions", 0)
            total_submissions = successful + failed
            
            if total_submissions > 0:
                success_rate = successful / total_submissions
                financial_score = financial_score * 0.7 + success_rate * 100 * 0.3
        
        # Ensure bounds
        financial_score = max(0, min(100, financial_score))
        
        # Calculate combined PFI (weighted average)
        performance_weight = 0.6
        financial_weight = 0.4
        
        combined_pfi = (
            performance_score * performance_weight +
            financial_score * financial_weight
        )
        
        # Ensure bounds
        combined_pfi = max(0, min(100, combined_pfi))
        
        return PFIMetrics(
            performance_score=performance_score,
            financial_score=financial_score,
            combined_pfi=combined_pfi
        )
    
    def update_reputation(
        self,
        user_id: str,
        pfi: PFIMetrics,
        project_id: str,
        milestone_id: str
    ) -> None:
        """Update user reputation score in database"""
        # Create PFI snapshot
        snapshot = PFISnapshot(
            timestamp=datetime.utcnow(),
            pfi_score=pfi.combined_pfi,
            project_id=project_id,
            milestone_id=milestone_id
        )
        
        # Update reputation in database
        self.db.update_user_reputation(user_id, pfi.combined_pfi, snapshot)
        
        logger.info(f"Updated reputation for user {user_id}: PFI={pfi.combined_pfi:.2f}")
    
    def get_reputation_history(self, user_id: str) -> list[dict]:
        """Retrieve historical reputation data"""
        reputation = self.db.get_user_reputation(user_id)
        if reputation:
            return reputation.get("reputation_history", [])
        return []
