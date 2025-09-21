import os
import sys
from typing import Dict, Optional
from src.services.linkedin_service import LinkedInConfig, linkedin_auth, get_linkedin_userinfo, create_linkedin_ugc_post, LinkedInAPIError, LinkedInAuthError
from src.services.autogen_gemini_service import LinkedInPostGenerator

def authenticate_linkedin(code: str) -> Dict[str, str]:
    """Authenticate with LinkedIn and get access token.
    
    Args:
        code (str): The authorization code from LinkedIn OAuth flow.
        
    Returns:
        Dict[str, str]: Dictionary containing the access token.
        
    Raises:
        LinkedInAuthError: If authentication fails.
    """
    try:
        response = linkedin_auth(code)
        if not response or 'access_token' not in response:
            raise LinkedInAuthError("Failed to get access token from LinkedIn")
        return response
    except Exception as e:
        raise LinkedInAuthError(f"LinkedIn authentication failed: {str(e)}")

def fetch_linkedin_userinfo(access_token: str) -> Dict[str, str]:
    """Fetch LinkedIn userinfo using access token.
    
    Args:
        access_token (str): The LinkedIn access token.
        
    Returns:
        Dict[str, str]: User information from LinkedIn.
        
    Raises:
        ValueError: If the access token is invalid or request fails.
    """
    if not access_token:
        raise ValueError("Access token is required")
    try:
        user_info = get_linkedin_userinfo(access_token)
        if not user_info or 'sub' not in user_info:
            raise ValueError("Invalid user info response from LinkedIn")
        return user_info
    except Exception as e:
        raise ValueError(f"Failed to fetch LinkedIn user info: {str(e)}")

def post_linkedin_ugc(access_token: str, author_id: str, text: str) -> Dict:
    """Create a LinkedIn UGC post.
    
    Args:
        access_token (str): The LinkedIn access token.
        author_id (str): The LinkedIn user ID of the post author.
        text (str): The content of the post.
        
    Returns:
        Dict: Response from LinkedIn API containing post details.
        
    Raises:
        ValueError: If any required parameter is missing or post creation fails.
    """
    if not all([access_token, author_id, text]):
        raise ValueError("Access token, author ID, and text are all required")
    
    try:
        post_response = create_linkedin_ugc_post(access_token, author_id, text)
        return post_response
    except Exception as e:
        raise ValueError(f"Failed to create LinkedIn post: {str(e)}")    
	


def main() -> None:
    """Main function to run the LinkedIn post generation and publishing process."""
    try:
        # Initialize services and validate configurations
        _ = LinkedInConfig.from_env()  # Validate LinkedIn config
        post_generator = LinkedInPostGenerator()  # Initialize post generator
        
        # Check for required environment variable
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN environment variable is not set")

        # Generate post content
        print("Generating LinkedIn post about C# generics...")
        post_content = post_generator.generate_post(topic="C# generics", add_ai_disclosure=True)
        print("Generated Post:\n", post_content)

        # Fetch user info and post to LinkedIn
        print("Fetching LinkedIn user info...")
        user_info = fetch_linkedin_userinfo(access_token)
        if not user_info:
            raise ValueError("Failed to fetch LinkedIn user info")
        print("User Info:", user_info)

        print("Creating LinkedIn post...")
        post_response = post_linkedin_ugc(access_token, user_info["sub"], post_content)
        print("Post successfully created:", post_response)

    except LinkedInAuthError as e:
        print(f"Authentication Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except LinkedInAPIError as e:
        print(f"LinkedIn API Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()