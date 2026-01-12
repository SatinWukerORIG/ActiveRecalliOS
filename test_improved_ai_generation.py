#!/usr/bin/env python3
"""
Test script for improved AI content generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_content_generator import AIContentGenerator

def test_improved_ai_generation():
    """Test the improved AI content generation with better prompts"""
    print("🧪 Testing Improved AI Content Generation")
    print("=" * 60)
    
    # Initialize the generator
    generator = AIContentGenerator()
    
    if not generator.is_available():
        print("❌ AI generation not available - OpenAI API key not configured")
        return
    
    print("✅ AI generation service available")
    
    # Test material
    test_material = """
    Photosynthesis is the process by which plants convert light energy into chemical energy.
    The process occurs in chloroplasts and involves two main stages:
    1. Light-dependent reactions (occur in thylakoids)
    2. Light-independent reactions (Calvin cycle, occurs in stroma)
    
    The overall equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2
    
    Key facts:
    - Chlorophyll absorbs light energy
    - Oxygen is released as a byproduct
    - Glucose is the main product
    - Process is essential for life on Earth
    """
    
    try:
        # Test 1: Generate flashcards
        print("\n1. Testing flashcard generation...")
        flashcards = generator.generate_flashcards(
            source_material=test_material,
            subject="Biology",
            max_cards=5,
            focus_areas=["photosynthesis process", "chemical equations"]
        )
        
        print(f"Generated {len(flashcards)} flashcards:")
        for i, card in enumerate(flashcards, 1):
            print(f"  Q{i}: {card['front']}")
            print(f"  A{i}: {card['back']}")
            print()
        
        # Test 2: Generate information pieces
        print("\n2. Testing information piece generation...")
        info_pieces = generator.generate_information_pieces(
            source_material=test_material,
            subject="Biology",
            max_items=4,
            focus_areas=["key facts", "equations"]
        )
        
        print(f"Generated {len(info_pieces)} information pieces:")
        for i, piece in enumerate(info_pieces, 1):
            print(f"  INFO{i}: {piece['front']}")
        
        # Test 3: Generate mixed content
        print("\n3. Testing mixed content generation...")
        mixed_content = generator.generate_mixed_content(
            source_material=test_material,
            subject="Biology",
            max_items=6,
            focus_areas=["photosynthesis"]
        )
        
        print(f"Generated {len(mixed_content)} mixed items:")
        flashcard_count = sum(1 for item in mixed_content if item['content_type'] == 'flashcard')
        info_count = sum(1 for item in mixed_content if item['content_type'] == 'information')
        print(f"  - {flashcard_count} flashcards")
        print(f"  - {info_count} information pieces")
        
        for i, item in enumerate(mixed_content, 1):
            if item['content_type'] == 'flashcard':
                print(f"  Q: {item['front']}")
                print(f"  A: {item['back']}")
            else:
                print(f"  INFO: {item['front']}")
            print()
        
        # Test 4: Validate output quality
        print("\n4. Validating output quality...")
        
        # Check flashcard structure
        valid_flashcards = all(
            card.get('content_type') == 'flashcard' and 
            card.get('front') and 
            card.get('back')
            for card in flashcards
        )
        print(f"Flashcard structure: {'✅ Valid' if valid_flashcards else '❌ Invalid'}")
        
        # Check information piece structure
        valid_info = all(
            piece.get('content_type') == 'information' and 
            piece.get('front') and 
            piece.get('back') is None
            for piece in info_pieces
        )
        print(f"Information structure: {'✅ Valid' if valid_info else '❌ Invalid'}")
        
        # Check mixed content structure
        valid_mixed = all(
            item.get('content_type') in ['flashcard', 'information'] and
            item.get('front')
            for item in mixed_content
        )
        print(f"Mixed content structure: {'✅ Valid' if valid_mixed else '❌ Invalid'}")
        
        # Check content limits
        print(f"Flashcard count limit: {'✅ Respected' if len(flashcards) <= 5 else '❌ Exceeded'}")
        print(f"Information count limit: {'✅ Respected' if len(info_pieces) <= 4 else '❌ Exceeded'}")
        print(f"Mixed content count limit: {'✅ Respected' if len(mixed_content) <= 6 else '❌ Exceeded'}")
        
        print("\n✅ Improved AI generation testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_ai_generation()