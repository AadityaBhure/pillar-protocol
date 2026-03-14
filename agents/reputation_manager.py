"""
Reputation Manager - Handles developer reputation scoring and tracking
Feature: payout-reputation-system
"""

import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class ReputationManager:
    """Manages developer reputation based on delivery timeliness and code quality"""
    
    def __init__(self, db_connection):
        """
        Initialize Reputation Manager
        
        Args:
            db_connection: DatabaseManager instance
        """
        self.db = db_connection
        self.config = self._load_config()
        logger.info("ReputationManager initialized with config: %s", self.config)
    
    def _load_config(self) -> dict:
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
    
    def _calculate_timeline_delta(self, timeline_status: str) -> int:
        """
        Calculate reputation change from timeline status
        
        Args:
            timeline_status: "on-time" or "late"
            
        Returns:
            int: +2 for on-time, -5 for late
        """
        weights = self.config['reputation_weights']
        if timeline_status == 'on-time':
            return weights['on_time_bonus']
        else:
            return -weights['late_penalty']
    
    def _calculate_quality_delta(self, pfi_score: float) -> int:
        """
        Calculate reputation change from PFI score
        
        Args:
            pfi_score: PFI score from Inspector (0-100)
            
        Returns:
            int: +1 for PFI>80, -2 for PFI<50, 0 otherwise
        """
        weights = self.config['reputation_weights']
        if pfi_score > 80:
            return weights['high_quality_bonus']
        elif pfi_score < 50:
            return -weights['low_quality_penalty']
        else:
            return 0
    
    def update_reputation(
        self,
        user_id: str,
        milestone_id: str,
        timeline_status: str,
        pfi_score: float
    ) -> dict:
        """
        Update user reputation based on timeline and quality
        
        Args:
            user_id: Developer user ID
            milestone_id: Completed milestone ID
            timeline_status: "on-time" or "late"
            pfi_score: PFI score from Inspector (0-100)
            
        Returns:
            dict with score_delta, new_score, events, reason
        """
        logger.info(
            "Updating reputation for user %s, milestone %s, status %s, PFI %.2f",
            user_id, milestone_id, timeline_status, pfi_score
        )
        
        # Get current reputation
        current_reputation = self.db.get_user_reputation(user_id)
        current_score = current_reputation['reputation_score'] if current_reputation else 50.0
        
        # Calculate score changes
        timeline_delta = self._calculate_timeline_delta(timeline_status)
        quality_delta = self._calculate_quality_delta(pfi_score)
        total_delta = timeline_delta + quality_delta
        
        # Apply changes (clamp to 0-100)
        new_score = max(0, min(100, current_score + total_delta))
        
        # Create history events
        events = []
        reason_parts = []
        
        if timeline_delta != 0:
            event_type = 'on_time_delivery' if timeline_status == 'on-time' else 'late_delivery'
            events.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'event_type': event_type,
                'score_change': timeline_delta,
                'milestone_id': milestone_id,
                'resulting_score': new_score
            })
            
            if timeline_status == 'on-time':
                reason_parts.append(f"On-time delivery bonus (+{timeline_delta})")
            else:
                reason_parts.append(f"Late delivery penalty ({timeline_delta})")
        
        if quality_delta != 0:
            event_type = 'high_quality' if pfi_score > 80 else 'low_quality'
            events.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'event_type': event_type,
                'score_change': quality_delta,
                'milestone_id': milestone_id,
                'resulting_score': new_score
            })
            
            if pfi_score > 80:
                reason_parts.append(f"High quality bonus (+{quality_delta})")
            else:
                reason_parts.append(f"Low quality penalty ({quality_delta})")
        
        # Persist to database
        self.db.update_user_reputation_score(user_id, new_score, events)
        
        # Update timeline counters
        if timeline_status == 'on-time':
            self.db.increment_on_time_count(user_id)
        else:
            self.db.increment_late_count(user_id)
        
        reason = " and ".join(reason_parts) if reason_parts else "No reputation change"
        
        logger.info(
            "Reputation updated: user %s, delta %d, new score %.2f, reason: %s",
            user_id, total_delta, new_score, reason
        )
        
        return {
            'score_delta': total_delta,
            'new_score': new_score,
            'events': events,
            'reason': reason
        }
    
    def get_reputation(self, user_id: str) -> dict:
        """
        Retrieve complete reputation data for user
        
        Args:
            user_id: Developer user ID
            
        Returns:
            dict with reputation_score, total_milestones_completed,
            on_time_count, late_count, on_time_percentage, 
            average_pfi_score, reputation_history
        """
        reputation = self.db.get_user_reputation(user_id)
        
        if not reputation:
            # Return default values for new users
            return {
                'user_id': user_id,
                'reputation_score': 50.0,
                'total_milestones_completed': 0,
                'on_time_count': 0,
                'late_count': 0,
                'on_time_percentage': 0.0,
                'average_pfi_score': 0.0,
                'reputation_history': []
            }
        
        # Calculate metrics
        on_time_count = reputation.get('total_on_time_deliveries', 0)
        late_count = reputation.get('total_late_deliveries', 0)
        total = on_time_count + late_count
        on_time_pct = (on_time_count / total * 100) if total > 0 else 0.0
        
        return {
            'user_id': user_id,
            'reputation_score': float(reputation.get('reputation_score', 50.0)),
            'total_milestones_completed': total,
            'on_time_count': on_time_count,
            'late_count': late_count,
            'on_time_percentage': round(on_time_pct, 2),
            'average_pfi_score': float(reputation.get('current_pfi', 0.0)),
            'reputation_history': reputation.get('reputation_history', [])
        }
