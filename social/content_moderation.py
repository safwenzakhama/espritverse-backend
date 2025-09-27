"""
Content moderation service using Google Gemini AI
"""
import google.generativeai as genai
from django.conf import settings
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ContentModerationService:
    def __init__(self):
        self.api_key = "AIzaSyAIARelwgiXosedZJk2OldrjM7hC5jp4zA"
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    def get_section_guidelines(self, section: str) -> str:
        """Get content guidelines for each section"""
        guidelines = {
            'esprit_committee': """
            ESPRIT Committee posts should be:
            - Official announcements from ESPRIT administration
            - Academic updates, exam schedules, or institutional news
            - Professional and formal in tone
            - Related to ESPRIT school policies, events, or official communications
            - NOT personal opinions, complaints, or informal discussions
            """,
            'club': """
            Club posts should be:
            - Related to student clubs, organizations, or extracurricular activities
            - Event announcements, club meetings, or club-related activities
            - Community building and student engagement content
            - NOT personal posts, academic complaints, or unrelated content
            """,
            'lost_and_found': """
            Lost and Found posts should be:
            - About lost items (descriptions, locations, contact info)
            - About found items (descriptions, where found, how to claim)
            - Clear descriptions of items and relevant details
            - NOT general discussions, personal items for sale, or unrelated content
            """,
             'colocation': """
             Colocation posts should be:
             - About room sharing, apartment hunting, or housing needs
             - Roommate searches, housing availability, or rental information
             - Practical housing-related information
             - NOT general social posts, personal discussions, or unrelated content
             """,
             'profile': """
             Profile posts should be:
             - Personal messages or posts on someone's profile wall
             - Birthday wishes, congratulations, or personal interactions
             - Appropriate for a personal profile context
             - NOT spam, inappropriate content, or unrelated to the person
             """
         }
        return guidelines.get(section, "General content guidelines apply.")
    
    def moderate_content(self, title: str, content: str, section: str) -> Tuple[bool, str]:
        """
        Moderate content using Gemini AI
        
        Returns:
            Tuple[bool, str]: (is_approved, reason)
        """
        try:
            guidelines = self.get_section_guidelines(section)
            
            prompt = f"""
            You are a content moderator for a university social platform. 
            
            Section: {section}
            Guidelines for this section: {guidelines}
            
            Post Title: "{title}"
            Post Content: "{content}"
            
            Please analyze if this post is appropriate for the "{section}" section.
            
            Consider:
            1. Does the content match the section's purpose and guidelines?
            2. Is the tone appropriate for the section?
            3. Is the content relevant to the section's theme?
            4. Are there any inappropriate elements (spam, harassment, etc.)?
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "approved": true/false,
                "reason": "Brief explanation of your decision"
            }}
            
            Be strict but fair. If the content doesn't clearly belong to this section, reject it.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            import json
            try:
                # Clean up response text to extract JSON
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0]
                
                result = json.loads(response_text)
                return result.get('approved', False), result.get('reason', 'No reason provided')
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini response: {response_text}")
                # Fallback: if we can't parse, be conservative and reject
                return False, "Content moderation system error - post rejected for safety"
                
        except Exception as e:
            logger.error(f"Content moderation error: {str(e)}")
            # Fallback: if moderation fails, be conservative and reject
            return False, "Content moderation system temporarily unavailable - post rejected for safety"
    
    def get_moderation_feedback(self, title: str, content: str, section: str, reason: str) -> str:
        """Generate helpful feedback for rejected posts"""
        guidelines = self.get_section_guidelines(section)
        
        return f"""
        Your post was not approved for the "{section}" section.
        
        Reason: {reason}
        
        Guidelines for "{section}" section:
        {guidelines}
        
        Please review your content and try posting in the appropriate section, or modify your content to better fit this section's guidelines.
        """
