"""
Spaced Repetition Service implementing SM-2 algorithm
"""
from datetime import datetime, timedelta
from app.models import Card
from app import db

class SpacedRepetitionService:
    """Service for managing spaced repetition logic"""
    
    @staticmethod
    def get_due_cards(user_id, limit=None):
        """Get cards due for review for a specific user"""
        query = Card.query.filter(
            Card.user_id == user_id,
            Card.next_review <= datetime.utcnow()
        ).order_by(Card.next_review.asc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    @staticmethod
    def get_user_stats(user_id):
        """Get learning statistics for a user"""
        total_cards = Card.query.filter_by(user_id=user_id).count()
        due_cards = Card.query.filter(
            Card.user_id == user_id,
            Card.next_review <= datetime.utcnow()
        ).count()
        
        # Cards by mastery level
        new_cards = Card.query.filter(
            Card.user_id == user_id,
            Card.repetition_count == 0
        ).count()
        
        learning_cards = Card.query.filter(
            Card.user_id == user_id,
            Card.repetition_count.between(1, 3)
        ).count()
        
        mature_cards = Card.query.filter(
            Card.user_id == user_id,
            Card.repetition_count > 3
        ).count()
        
        return {
            'total_cards': total_cards,
            'due_cards': due_cards,
            'new_cards': new_cards,
            'learning_cards': learning_cards,
            'mature_cards': mature_cards
        }
    
    @staticmethod
    def review_card(card_id, quality_rating):
        """Process a card review with quality rating (0-5)"""
        card = Card.query.get(card_id)
        if not card:
            return None
            
        card.update_spaced_repetition(quality_rating)
        db.session.commit()
        
        return card
    
    @staticmethod
    def get_next_review_batch(user_id, batch_size=5):
        """Get the next batch of cards for review session"""
        due_cards = SpacedRepetitionService.get_due_cards(user_id, batch_size)
        
        # If not enough due cards, add some new cards
        if len(due_cards) < batch_size:
            new_cards_needed = batch_size - len(due_cards)
            new_cards = Card.query.filter(
                Card.user_id == user_id,
                Card.repetition_count == 0,
                Card.next_review <= datetime.utcnow()
            ).limit(new_cards_needed).all()
            
            due_cards.extend(new_cards)
        
        return due_cards