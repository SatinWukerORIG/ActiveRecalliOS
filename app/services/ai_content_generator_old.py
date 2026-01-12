"""
AI Content Generation Service using OpenAI gpt-5-nano
"""
from openai import OpenAI
import re
import base64
import PyPDF2
import io
from PIL import Image
from typing import List, Dict, Any, Optional
from app.config import Config

class AIContentGenerator:
    """Service for generating flashcards and information pieces using AI"""
    
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    def is_available(self):
        """Check if AI generation is available"""
        return bool(self.api_key and self.client)
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            # If PDF parsing fails, try to decode as text (fallback for invalid PDFs)
            try:
                # Try to decode as UTF-8 text
                text_content = pdf_content.decode('utf-8', errors='ignore')
                if text_content.strip():
                    return text_content.strip()
            except:
                pass
            
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def encode_image(self, image_content: bytes) -> str:
        """Encode image to base64 for OpenAI API"""
        try:
            # Validate and potentially resize image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 2048x2048 for GPT-4 Vision)
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # Encode to base64
            return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")
    
    def generate_flashcards(self, source_material: str, subject: str = None, 
                          max_cards: int = 10, focus_areas: List[str] = None,
                          images: List[bytes] = None, pdf_content: bytes = None) -> List[Dict[str, Any]]:
        """Generate flashcards from source material with optional images and PDF"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        # Process additional content
        full_content = source_material
        
        # Extract PDF text if provided
        if pdf_content:
            pdf_text = self.extract_text_from_pdf(pdf_content)
            full_content += f"\n\nPDF Content:\n{pdf_text}"
        
        prompt = self._build_flashcard_prompt(full_content, subject, max_cards, focus_areas)
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are an expert educational content creator specializing in active recall and spaced repetition learning techniques."},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
            
            # Add images if provided
            if images:
                for image_content in images[:5]:  # Limit to 5 images
                    try:
                        encoded_image = self.encode_image(image_content)
                        messages[1]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        })
                    except Exception as e:
                        print(f"Warning: Failed to process image: {e}")
            
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_flashcards(content)
            
        except Exception as e:
            raise Exception(f"Failed to generate flashcards: {str(e)}")
    
    def generate_information_pieces(self, source_material: str, subject: str = None,
                                  max_items: int = 10, focus_areas: List[str] = None,
                                  images: List[bytes] = None, pdf_content: bytes = None) -> List[Dict[str, Any]]:
        """Generate information pieces from source material with optional images and PDF"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        # Process additional content
        full_content = source_material
        
        # Extract PDF text if provided
        if pdf_content:
            pdf_text = self.extract_text_from_pdf(pdf_content)
            full_content += f"\n\nPDF Content:\n{pdf_text}"
        
        prompt = self._build_information_prompt(full_content, subject, max_items, focus_areas)
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are an expert educational content creator specializing in information retention and micro-learning."},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
            
            # Add images if provided
            if images:
                for image_content in images[:5]:  # Limit to 5 images
                    try:
                        encoded_image = self.encode_image(image_content)
                        messages[1]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        })
                    except Exception as e:
                        print(f"Warning: Failed to process image: {e}")
            
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_information_pieces(content)
            
        except Exception as e:
            raise Exception(f"Failed to generate information pieces: {str(e)}")
    
    def generate_mixed_content(self, source_material: str, subject: str = None,
                             max_items: int = 10, focus_areas: List[str] = None,
                             images: List[bytes] = None, pdf_content: bytes = None) -> List[Dict[str, Any]]:
        """Generate mixed flashcards and information pieces in a single API call"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        # Process additional content
        full_content = source_material
        
        # Extract PDF text if provided
        if pdf_content:
            pdf_text = self.extract_text_from_pdf(pdf_content)
            full_content += f"\n\nPDF Content:\n{pdf_text}"
        
        prompt = self._build_mixed_prompt(full_content, subject, max_items, focus_areas)
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are an expert educational content creator specializing in active recall and spaced repetition learning techniques."},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
            
            # Add images if provided
            if images:
                for image_content in images[:5]:  # Limit to 5 images
                    try:
                        encoded_image = self.encode_image(image_content)
                        messages[1]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}",
                                "detail": "high"
                            }
                        })
                    except Exception as e:
                        print(f"Warning: Failed to process image: {e}")
            
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_mixed_content(content, max_items)
            
        except Exception as e:
            raise Exception(f"Failed to generate mixed content: {str(e)}")
    
    def _build_flashcard_prompt(self, source_material: str, subject: str, max_cards: int, focus_areas: List[str]) -> str:
        """Build prompt for flashcard generation"""
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\n- Focus specifically on these areas: {', '.join(focus_areas)}"
        
        subject_instruction = f"\n- Subject context: {subject}" if subject else ""
        
        prompt = f"""You are an expert educational content creator. Create exactly {max_cards} high-quality flashcards from the provided study material.

CRITICAL FORMATTING REQUIREMENTS:
- Use EXACTLY this format for each flashcard
- Start each question with "Q[number]:" (e.g., Q1:, Q2:, Q3:)
- Start each answer with "A[number]:" (e.g., A1:, A2:, A3:)
- Put each Q/A pair on separate lines
- Do not include any other text, explanations, or formatting
- Generate exactly {max_cards} flashcards, no more, no less

CONTENT GUIDELINES:{subject_instruction}{focus_instruction}
- Make questions specific, clear, and testable
- Keep answers concise but complete (1-3 sentences)
- Focus on the most important concepts for active recall
- Vary question types: definitions, applications, comparisons, cause-effect
- Ensure questions test understanding, not just memorization
- If images are provided, reference visual elements when relevant
- Extract key information from any PDF content provided
- Prioritize information that benefits from spaced repetition

EXAMPLE FORMAT:
Q1: What is the primary function of mitochondria in cells?
A1: Mitochondria produce ATP (energy) for cellular processes through cellular respiration.

Q2: Which organelle is known as the "powerhouse of the cell"?
A2: The mitochondria, because it generates most of the cell's energy in the form of ATP.

NOW CREATE {max_cards} FLASHCARDS FROM THIS MATERIAL:

{source_material}

REMEMBER: Use the exact Q[number]: and A[number]: format. Generate exactly {max_cards} flashcards."""
        return prompt
    
    def _build_mixed_prompt(self, source_material: str, subject: str, max_items: int, focus_areas: List[str]) -> str:
        """Build prompt for mixed content generation"""
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\n- Focus specifically on these areas: {', '.join(focus_areas)}"
        
        subject_instruction = f"\n- Subject context: {subject}" if subject else ""
        
        flashcard_count = max_items // 2
        info_count = max_items - flashcard_count
        
        prompt = f"""You are an expert educational content creator. Create exactly {max_items} learning items from the provided study material: {flashcard_count} flashcards and {info_count} information pieces.

CRITICAL FORMATTING REQUIREMENTS:
- Use EXACTLY these formats:
  * Flashcards: "Q[number]:" followed by "A[number]:" (e.g., Q1:, A1:)
  * Information: "INFO[number]:" (e.g., INFO1:, INFO2:)
- Put each item on a separate line
- Do not include any other text, explanations, or formatting
- Generate exactly {flashcard_count} Q/A pairs and {info_count} INFO items
- Total items must equal exactly {max_items}

CONTENT GUIDELINES:{subject_instruction}{focus_instruction}
- For flashcards: Create specific, testable questions with concise answers
- For information: Extract key facts, formulas, definitions, or concepts
- Focus on the most important concepts for active recall
- Vary question types: definitions, applications, comparisons, cause-effect
- Make information pieces standalone and memorable (1-2 sentences max)
- Prioritize content that benefits from spaced repetition
- Reference visual elements from images when relevant
- Extract key information from any PDF content provided

EXAMPLE FORMAT:
Q1: What is the primary function of mitochondria in cells?
A1: Mitochondria produce ATP (energy) for cellular processes through cellular respiration.

Q2: Which organelle is known as the "powerhouse of the cell"?
A2: The mitochondria, because it generates most of the cell's energy in the form of ATP.

INFO1: The speed of light in a vacuum is 299,792,458 meters per second.
INFO2: DNA stands for Deoxyribonucleic Acid and contains genetic instructions.

NOW CREATE EXACTLY {flashcard_count} FLASHCARDS AND {info_count} INFORMATION PIECES FROM THIS MATERIAL:

{source_material}

REMEMBER: 
- Use exact Q[number]:, A[number]:, and INFO[number]: formats
- Generate exactly {flashcard_count} flashcards and {info_count} information pieces
- Total output must be exactly {max_items} items"""
        return prompt
    
    def _build_information_prompt(self, source_material: str, subject: str, max_items: int, focus_areas: List[str]) -> str:
        """Build prompt for information piece generation"""
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\n- Focus specifically on these areas: {', '.join(focus_areas)}"
        
        subject_instruction = f"\n- Subject context: {subject}" if subject else ""
        
        prompt = f"""You are an expert educational content creator. Extract exactly {max_items} key information pieces from the provided study material.

CRITICAL FORMATTING REQUIREMENTS:
- Use EXACTLY this format for each information piece
- Start each item with "INFO[number]:" (e.g., INFO1:, INFO2:, INFO3:)
- Put each information piece on a separate line
- Do not include any other text, explanations, or formatting
- Generate exactly {max_items} information pieces, no more, no less

CONTENT GUIDELINES:{subject_instruction}{focus_instruction}
- Extract the most important facts, formulas, definitions, or key concepts
- Make each piece standalone and memorable
- Keep each piece concise (1-2 sentences maximum)
- Focus on information that benefits from repetition and recall
- Include formulas, dates, definitions, key principles, important statistics
- Prioritize factual information over explanatory content
- Reference visual elements from images when relevant
- Include important details from any PDF content provided

EXAMPLE FORMAT:
INFO1: The speed of light in a vacuum is 299,792,458 meters per second.
INFO2: DNA stands for Deoxyribonucleic Acid and contains genetic instructions.
INFO3: The mitochondria is known as the "powerhouse of the cell" because it produces ATP.

NOW EXTRACT {max_items} INFORMATION PIECES FROM THIS MATERIAL:

{source_material}

REMEMBER: Use the exact INFO[number]: format. Generate exactly {max_items} information pieces."""
        return prompt
    
    def _parse_flashcards(self, content: str) -> List[Dict[str, Any]]:
        """Parse generated flashcards from LLM response"""
        flashcards = []
        lines = content.strip().split('\n')
        
        current_question = None
        current_answer = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match question pattern (Q1:, Q2:, etc.)
            q_match = re.match(r'^Q\d+:\s*(.+)$', line)
            if q_match:
                current_question = q_match.group(1).strip()
                continue
            
            # Match answer pattern (A1:, A2:, etc.)
            a_match = re.match(r'^A\d+:\s*(.+)$', line)
            if a_match and current_question:
                current_answer = a_match.group(1).strip()
                
                flashcards.append({
                    'content_type': 'flashcard',
                    'front': current_question,
                    'back': current_answer
                })
                
                current_question = None
                current_answer = None
        
        return flashcards
    
    def _parse_information_pieces(self, content: str) -> List[Dict[str, Any]]:
        """Parse generated information pieces from LLM response"""
        info_pieces = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match info pattern (INFO1:, INFO2:, etc.)
            info_match = re.match(r'^INFO\d+:\s*(.+)$', line)
            if info_match:
                info_content = info_match.group(1).strip()
                
                info_pieces.append({
                    'content_type': 'information',
                    'front': info_content,
                    'back': None
                })
        
        return info_pieces
    
    def _parse_mixed_content(self, content: str, max_items: int) -> List[Dict[str, Any]]:
        """Parse mixed content (flashcards and information pieces) from LLM response"""
        items = []
        lines = content.strip().split('\n')
        
        current_question = None
        current_answer = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match question pattern (Q1:, Q2:, etc.)
            q_match = re.match(r'^Q\d+:\s*(.+)$', line)
            if q_match:
                current_question = q_match.group(1).strip()
                continue
            
            # Match answer pattern (A1:, A2:, etc.)
            a_match = re.match(r'^A\d+:\s*(.+)$', line)
            if a_match and current_question:
                current_answer = a_match.group(1).strip()
                
                items.append({
                    'content_type': 'flashcard',
                    'front': current_question,
                    'back': current_answer
                })
                
                current_question = None
                current_answer = None
                continue
            
            # Match information pattern (INFO1:, INFO2:, etc.)
            info_match = re.match(r'^INFO\d+:\s*(.+)$', line)
            if info_match:
                info_text = info_match.group(1).strip()
                items.append({
                    'content_type': 'information',
                    'front': info_text,
                    'back': None
                })
        
        # Limit to requested number of items
        return items[:max_items]