"""LinkedIn API service module for authentication and posting functionality."""
import os
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException

load_dotenv()

@dataclass
class LinkedInConfig:
    """Configuration class for LinkedIn API settings."""
    api_url: str
    client_id: str
    client_secret: str
    redirect_uri: str

    @classmethod
    def from_env(cls) -> 'LinkedInConfig':
        """Create a LinkedInConfig instance from environment variables.
        
        Returns:
            LinkedInConfig: Configuration object with LinkedIn API settings.
            
        Raises:
            ValueError: If any required environment variable is missing.
        """
        required_vars = {
            "LINKEDIN_API_URL": os.getenv("LINKEDIN_API_URL"),
            "LINKEDIN_CLIENT_ID": os.getenv("LINKEDIN_CLIENT_ID"),
            "LINKEDIN_CLIENT_SECRET": os.getenv("LINKEDIN_CLIENT_SECRET"),
            "LINKEDIN_REDIRECT_URI": os.getenv("LINKEDIN_REDIRECT_URI")
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return cls(
            api_url=required_vars["LINKEDIN_API_URL"],
            client_id=required_vars["LINKEDIN_CLIENT_ID"],
            client_secret=required_vars["LINKEDIN_CLIENT_SECRET"],
            redirect_uri=required_vars["LINKEDIN_REDIRECT_URI"]
        )

class LinkedInAPIError(Exception):
    """Base exception for LinkedIn API errors."""
    pass

class LinkedInAuthError(LinkedInAPIError):
    """Exception raised for authentication errors."""
    pass

class LinkedInPostError(LinkedInAPIError):
    """Exception raised for post creation errors."""
    pass

def create_linkedin_ugc_post(access_token: str, author_id: str, text: str) -> Dict:
    """Create a LinkedIn UGC (User Generated Content) post.
    
    Args:
        access_token (str): Valid LinkedIn access token.
        author_id (str): LinkedIn user ID of the post author.
        text (str): Content of the post.
        
    Returns:
        Dict: Response from LinkedIn API containing post details.
        
    Raises:
        LinkedInPostError: If post creation fails.
        ValueError: If any required parameter is empty.
    """
    if not all([access_token, author_id, text]):
        raise ValueError("access_token, author_id, and text are all required")

    config = LinkedInConfig.from_env()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "author": f"urn:li:person:{author_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(
            f"{config.api_url}/v2/ugcPosts",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise LinkedInPostError(f"Failed to create UGC post: {str(e)}") from e

def get_linkedin_access_token(code: str) -> str:
    """Get LinkedIn access token using authorization code.
    
    Args:
        code (str): Authorization code from LinkedIn OAuth flow.
        
    Returns:
        str: LinkedIn access token.
        
    Raises:
        LinkedInAuthError: If token request fails.
        ValueError: If code is empty.
    """
    if not code:
        raise ValueError("Authorization code is required")

    config = LinkedInConfig.from_env()
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.redirect_uri,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
    }
    
    try:
        response = requests.post(f"{config.api_url}/oauth/v2/accessToken", data=payload)
        response.raise_for_status()
        token_data = response.json()
        if "access_token" not in token_data:
            raise LinkedInAuthError("Access token not found in response")
        return token_data["access_token"]
    except RequestException as e:
        raise LinkedInAuthError(f"Failed to get access token: {str(e)}") from e

def linkedin_auth(code: str) -> Dict[str, str]:
    """Authenticate with LinkedIn using authorization code.
    
    Args:
        code (str): Authorization code from LinkedIn OAuth flow.
        
    Returns:
        Dict[str, str]: Dictionary containing the access token.
        
    Raises:
        LinkedInAuthError: If authentication fails.
    """
    access_token = get_linkedin_access_token(code)
    return {"access_token": access_token}

def get_linkedin_userinfo(access_token: str) -> Dict[str, str]:
    """Fetch LinkedIn user information.
    
    Args:
        access_token (str): Valid LinkedIn access token.
        
    Returns:
        Dict[str, str]: User information from LinkedIn.
        
    Raises:
        LinkedInAuthError: If userinfo request fails.
        ValueError: If access_token is empty.
    """
    if not access_token:
        raise ValueError("Access token is required")

    config = LinkedInConfig.from_env()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{config.api_url}/v2/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise LinkedInAuthError(f"Failed to fetch userinfo: {str(e)}") from e
