#!/usr/bin/env python
"""
Test script for content moderation system
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from social.content_moderation import ContentModerationService

def test_moderation():
    """Test the content moderation system"""
    print("🤖 Testing Content Moderation System")
    print("=" * 50)
    
    try:
        moderation_service = ContentModerationService()
        print("✅ Content moderation service initialized successfully")
        
        # Test cases
        test_cases = [
            {
                "title": "Room for rent",
                "content": "Looking for a roommate to share a 2-bedroom apartment near ESPRIT. Rent is 300 TND per month.",
                "section": "colocation",
                "expected": True
            },
            {
                "title": "Lost my phone",
                "content": "I lost my iPhone 12 in the cafeteria yesterday. If found, please contact me at 12345678.",
                "section": "lost_and_found",
                "expected": True
            },
            {
                "title": "Random thoughts",
                "content": "Just had a great day at the beach! The weather was amazing and I met some cool people.",
                "section": "colocation",
                "expected": False
            },
            {
                "title": "Club meeting",
                "content": "Join us for the programming club meeting this Friday at 2 PM in room 101. We'll discuss web development projects.",
                "section": "club",
                "expected": True
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test_case['title']}")
            print(f"Section: {test_case['section']}")
            print(f"Content: {test_case['content'][:50]}...")
            
            try:
                is_approved, reason = moderation_service.moderate_content(
                    test_case['title'],
                    test_case['content'],
                    test_case['section']
                )
                
                result_emoji = "✅" if is_approved else "❌"
                expected_emoji = "✅" if test_case['expected'] else "❌"
                
                print(f"Result: {result_emoji} {'APPROVED' if is_approved else 'REJECTED'}")
                print(f"Expected: {expected_emoji} {'APPROVED' if test_case['expected'] else 'REJECTED'}")
                print(f"Reason: {reason}")
                
                if is_approved == test_case['expected']:
                    print("🎉 Test PASSED")
                else:
                    print("⚠️  Test FAILED - Unexpected result")
                    
            except Exception as e:
                print(f"❌ Error during moderation: {str(e)}")
        
        print("\n" + "=" * 50)
        print("🏁 Content moderation testing completed!")
        
    except Exception as e:
        print(f"❌ Failed to initialize moderation service: {str(e)}")
        print("Make sure GEMINI_API_KEY is set in your environment or .env file")

if __name__ == "__main__":
    test_moderation()
