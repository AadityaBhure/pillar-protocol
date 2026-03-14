from backend.models import EscrowStatus
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BankerAgent:
    def __init__(self, db_connection, reputation_manager=None):
        """
        Initialize with database connection and optional reputation manager
        
        Args:
            db_connection: DatabaseManager instance
            reputation_manager: ReputationManager instance (optional)
        """
        self.db = db_connection
        self.reputation_manager = reputation_manager
    
    def get_milestone_status(self, milestone_id: str) -> Optional[EscrowStatus]:
        """Query current escrow status from database"""
        status_str = self.db.get_milestone_status(milestone_id)
        if status_str:
            return EscrowStatus(status_str)
        return None
    
    def lock_milestone(self, milestone_id: str) -> bool:
        """
        Lock milestone, preventing deletion, and record submission time
        
        NEW: Records submission_time as ISO 8601 timestamp
        """
        try:
            current_status = self.get_milestone_status(milestone_id)
            if current_status != EscrowStatus.PENDING:
                logger.warning(f"Cannot lock milestone {milestone_id}: current status is {current_status}")
                return False
            
            # NEW: Record submission time
            submission_time = datetime.utcnow().isoformat() + 'Z'
            
            self.db.update_milestone_status(milestone_id, EscrowStatus.LOCKED.value)
            self.db.update_milestone_submission_time(milestone_id, submission_time)
            
            logger.info(f"Milestone {milestone_id} locked successfully at {submission_time}")
            return True
        except Exception as e:
            logger.error(f"Failed to lock milestone {milestone_id}: {e}")
            return False
    
    def _determine_timeline_status(
        self, 
        submission_time: Optional[str], 
        deadline: Optional[str]
    ) -> str:
        """
        Compare submission time against deadline
        
        Args:
            submission_time: ISO 8601 timestamp
            deadline: ISO 8601 timestamp or None
            
        Returns:
            "on-time" or "late"
        """
        if deadline is None:
            logger.info("No deadline set, treating as on-time (backward compatibility)")
            return "on-time"  # Backward compatibility
        
        if submission_time is None:
            logger.warning("No submission_time set, treating as on-time")
            return "on-time"
        
        try:
            submission_dt = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            
            is_on_time = submission_dt <= deadline_dt
            status = "on-time" if is_on_time else "late"
            
            logger.info(
                "Timeline status: %s (submitted: %s, deadline: %s)",
                status, submission_time, deadline
            )
            
            return status
        except (ValueError, AttributeError) as e:
            logger.error("Error parsing timestamps: %s, treating as on-time", e)
            return "on-time"
    
    def release_payment(
        self, 
        milestone_id: str, 
        user_id: Optional[str] = None, 
        pfi_score: Optional[float] = None
    ) -> dict:
        """
        Release payment and trigger reputation update
        
        NEW: Determines timeline_status and triggers reputation update
        
        Args:
            milestone_id: Milestone ID
            user_id: Developer user ID (required for reputation update)
            pfi_score: PFI score from Inspector (required for reputation update)
            
        Returns:
            dict with status, payment, timeline_status, reputation_change
        """
        try:
            current_status = self.get_milestone_status(milestone_id)
            if current_status != EscrowStatus.LOCKED:
                logger.warning(f"Cannot release payment for milestone {milestone_id}: current status is {current_status}")
                return {
                    'status': 'error',
                    'message': f'Milestone not locked (current status: {current_status})'
                }
            
            # Get milestone data
            milestone = self.db.get_milestone(milestone_id)
            if not milestone:
                return {'status': 'error', 'message': 'Milestone not found'}
            
            submission_time = milestone.get('submission_time')
            deadline = milestone.get('deadline')
            
            # Determine timeline status
            timeline_status = self._determine_timeline_status(submission_time, deadline)
            
            # Release payment (full amount regardless of timeline)
            self.db.update_milestone_status(milestone_id, EscrowStatus.RELEASED.value)
            self.db.update_milestone_timeline_status(milestone_id, timeline_status)
            
            escrow_amount = milestone.get('escrow_amount', 100.0)
            payment_result = self.simulate_x402_payment(escrow_amount, user_id or "developer-wallet")
            
            logger.info(f"Payment released for milestone {milestone_id}: {payment_result}")
            
            # Trigger reputation update if reputation_manager is available
            reputation_change = None
            if self.reputation_manager and user_id and pfi_score is not None:
                try:
                    reputation_change = self.reputation_manager.update_reputation(
                        user_id=user_id,
                        milestone_id=milestone_id,
                        timeline_status=timeline_status,
                        pfi_score=pfi_score
                    )
                    logger.info(f"Reputation updated for user {user_id}: {reputation_change}")
                except Exception as e:
                    logger.error(f"Failed to update reputation: {e}")
                    reputation_change = {'error': str(e)}
            
            return {
                'status': 'success',
                'payment': payment_result,
                'timeline_status': timeline_status,
                'reputation_change': reputation_change
            }
            
        except Exception as e:
            logger.error(f"Failed to release payment for milestone {milestone_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def can_delete_milestone(self, milestone_id: str) -> bool:
        """Check if milestone can be deleted (not LOCKED)"""
        status = self.get_milestone_status(milestone_id)
        return status == EscrowStatus.PENDING
    
    def simulate_x402_payment(self, amount: float, recipient: str) -> dict:
        """Simulate x402 payment protocol"""
        return {
            "status": "success",
            "amount": amount,
            "recipient": recipient,
            "transaction_id": f"x402-{amount}-{recipient}",
            "protocol": "x402"
        }
