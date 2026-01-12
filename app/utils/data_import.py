"""
Data import utilities for Active Recall
Supports importing from CSV, Anki, and other formats
"""
import csv
import json
from typing import List, Dict, Any
from app.models import Card, User
from app import db

class DataImporter:
    """Utility class for importing cards from various formats"""
    
    @staticmethod
    def import_from_csv(user_id: int, csv_content: str, delimiter: str = ',') -> Dict[str, Any]:
        """
        Import cards from CSV format
        Expected format: front,back,subject,tags
        """
        imported_cards = []
        errors = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(csv_content.splitlines(), delimiter=delimiter)
            
            for row_num, row in enumerate(csv_reader, start=1):
                try:
                    # Validate required fields
                    if 'front' not in row or not row['front'].strip():
                        errors.append(f"Row {row_num}: Missing 'front' field")
                        continue
                    
                    # Determine content type
                    content_type = 'flashcard' if row.get('back', '').strip() else 'information'
                    
                    # Create card
                    card = Card(
                        user_id=user_id,
                        content_type=content_type,
                        front=row['front'].strip(),
                        back=row.get('back', '').strip() if content_type == 'flashcard' else None,
                        subject=row.get('subject', '').strip() or None,
                        tags=row.get('tags', '').strip() or None
                    )
                    
                    db.session.add(card)
                    imported_cards.append(card)
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Commit all cards
            db.session.commit()
            
            return {
                'success': True,
                'imported_count': len(imported_cards),
                'errors': errors,
                'cards': [card.to_dict() for card in imported_cards]
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"Failed to import CSV: {str(e)}",
                'imported_count': 0,
                'errors': errors
            }
    
    @staticmethod
    def import_from_anki_json(user_id: int, json_content: str) -> Dict[str, Any]:
        """
        Import cards from Anki JSON export format
        """
        imported_cards = []
        errors = []
        
        try:
            data = json.loads(json_content)
            
            # Handle different Anki export formats
            cards_data = data.get('cards', data.get('notes', []))
            
            for card_num, card_data in enumerate(cards_data, start=1):
                try:
                    # Extract fields based on Anki format
                    if 'fields' in card_data:
                        # Standard Anki format
                        fields = card_data['fields']
                        front = fields.get('Front', fields.get('Question', ''))
                        back = fields.get('Back', fields.get('Answer', ''))
                    else:
                        # Simple format
                        front = card_data.get('front', card_data.get('question', ''))
                        back = card_data.get('back', card_data.get('answer', ''))
                    
                    if not front.strip():
                        errors.append(f"Card {card_num}: Missing front/question field")
                        continue
                    
                    # Determine content type
                    content_type = 'flashcard' if back.strip() else 'information'
                    
                    # Extract metadata
                    subject = card_data.get('deck', card_data.get('subject', ''))
                    tags = card_data.get('tags', [])
                    if isinstance(tags, list):
                        tags = ','.join(tags)
                    
                    # Create card
                    card = Card(
                        user_id=user_id,
                        content_type=content_type,
                        front=front.strip(),
                        back=back.strip() if content_type == 'flashcard' else None,
                        subject=subject.strip() or None,
                        tags=tags.strip() or None
                    )
                    
                    db.session.add(card)
                    imported_cards.append(card)
                    
                except Exception as e:
                    errors.append(f"Card {card_num}: {str(e)}")
            
            # Commit all cards
            db.session.commit()
            
            return {
                'success': True,
                'imported_count': len(imported_cards),
                'errors': errors,
                'cards': [card.to_dict() for card in imported_cards]
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Invalid JSON format: {str(e)}",
                'imported_count': 0,
                'errors': []
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"Failed to import Anki data: {str(e)}",
                'imported_count': 0,
                'errors': errors
            }
    
    @staticmethod
    def export_to_csv(user_id: int) -> str:
        """Export user's cards to CSV format"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get all user cards
        cards = Card.query.filter_by(user_id=user_id).all()
        
        # Create CSV content
        csv_lines = ['front,back,subject,tags,content_type,created_at']
        
        for card in cards:
            row = [
                f'"{card.front}"',
                f'"{card.back or ""}"',
                f'"{card.subject or ""}"',
                f'"{card.tags or ""}"',
                card.content_type,
                card.created_at.isoformat()
            ]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    @staticmethod
    def get_import_template() -> str:
        """Get CSV template for importing cards"""
        return """front,back,subject,tags
"What is the capital of France?","Paris","Geography","capitals,europe"
"Python list comprehension syntax","[expression for item in iterable]","Programming","python,syntax"
"E=mc²","","Physics","formula,einstein"
"Photosynthesis definition","Process by which plants convert light energy into chemical energy","Biology","plants,energy"
"""