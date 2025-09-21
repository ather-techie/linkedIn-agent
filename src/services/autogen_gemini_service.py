"""Service for generating LinkedIn posts using AutoGen and Gemini."""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import re
from dotenv import load_dotenv
import autogen

# Load environment variables
load_dotenv()

@dataclass
class GeminiConfig:
    """Configuration class for Gemini API settings."""
    api_key: str
    model: str

    @classmethod
    def from_env(cls) -> 'GeminiConfig':
        """Create a GeminiConfig instance from environment variables.
        
        Returns:
            GeminiConfig: Configuration object with Gemini API settings.
            
        Raises:
            ValueError: If any required environment variable is missing.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        
        if not api_key or not model:
            missing = []
            if not api_key:
                missing.append("GEMINI_API_KEY")
            if not model:
                missing.append("GEMINI_MODEL")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
        return cls(api_key=api_key, model=model)

class LinkedInPostGenerator:
    """Class for generating LinkedIn posts using AutoGen and Gemini."""

    def __init__(self):
        """Initialize the LinkedIn post generator with configuration."""
        config = GeminiConfig.from_env()
        self.llm_config = {
            "model": config.model,
            "api_key": config.api_key,
            "api_type": "google",
        }
        
    def _create_linkedin_prompt(self, topic: str) -> str:
        """Create a prompt for generating LinkedIn posts.
        
        Args:
            topic (str): The topic to create a post about.
            
        Returns:
            str: Formatted prompt for the AI model.
        """
        return f'''Create an engaging LinkedIn post about {topic}. The post should:
        - Be optimized for LinkedIn's professional audience
        - Be between 150-200 words
        - Include line breaks for readability
        - Focus on providing value and insights
        - Include a short, relevant code snippet (3-5 lines max) that demonstrates a key concept
        - Format the code properly with ```c# ``` markdown syntax
        - End with an engaging question that encourages discussion
        - Add 3-4 relevant hashtags
        - Use a professional and approachable tone
        - Avoid using emojis
        - provide output in json format {{"title": "", "content": "", "code": "", "hashtags": [], "question": ""}}
        '''

    def _create_agents(self) -> tuple[autogen.AssistantAgent, autogen.AssistantAgent]:
        """Create technical writer and content optimizer agents for post generation.
        
        Returns:
            tuple[autogen.AssistantAgent, autogen.AssistantAgent]: Technical writer and content optimizer agents.
        """
        technical_writer = autogen.AssistantAgent(
            name="TechnicalWriter",
            system_message="""You are an expert technical content creator who specializes in crafting engaging 
                LinkedIn posts about programming concepts. Your writing process:
                1. Create an initial technical post that includes:
                   - A compelling technical headline/title
                   - Clear, technically accurate main content
                   - Relevant technical hashtags (3-5)
                   - An engaging technical question to drive discussion
                2. When receiving feedback from the optimizer, carefully analyze it
                3. Create an improved version incorporating the feedback
                4. Only return the final post content without any additional comments or explanations""",
            llm_config=self.llm_config,
        )

        content_optimizer = autogen.AssistantAgent(
            name="ContentOptimizer",
            llm_config=self.llm_config,
            system_message="""You are an expert LinkedIn content strategist and editor. Your role is to:
                1. Review the writer's LinkedIn posts for:
                   - Professional tone and clarity
                   - Engagement potential
                   - Appropriate length for LinkedIn
                   - Effective headline and hook
                   - Strategic use of hashtags
                2. Provide specific, actionable feedback on:
                   - What works well and should be kept
                   - What needs improvement and why
                   - Suggested changes or enhancements
                3. Keep feedback constructive and focused on improving viral potential and professional impact""",
        )
        
        return technical_writer, content_optimizer

    def generate_post(self, topic: str, add_ai_disclosure: bool = True) -> str:
        """Generate a LinkedIn post about the given topic.
        
        Args:
            topic (str): The topic to create a post about.
            add_ai_disclosure (bool): Whether to add AI disclosure to the post.
            
        Returns:
            str: The generated LinkedIn post.
            
        Raises:
            ValueError: If topic is empty or if post generation fails.
            json.JSONDecodeError: If the response cannot be parsed as JSON.
        """
        if not topic:
            raise ValueError("Topic is required")

        technical_writer, content_optimizer = self._create_agents()
        prompt = self._create_linkedin_prompt(topic)
        
        # Generate the post through agent interaction
        chat_result = content_optimizer.initiate_chat(
            recipient=technical_writer,
            message=prompt,
            max_turns=2,
            summary_method="last_msg"
        )

        # Process the result
        summary = chat_result.summary
        cleaned_summary = re.sub(r'```json\s*|\s*```', '', summary, flags=re.DOTALL)
        
        if add_ai_disclosure:
            cleaned_summary = self._add_ai_disclosure(cleaned_summary)
            
        return self._convert_to_linkedin_post(cleaned_summary)

    @staticmethod
    def _add_ai_disclosure(post_json: str) -> str:
        """Add AI disclosure to the post content.
        
        Args:
            post_json (str): JSON string containing the post content.
            
        Returns:
            str: Updated JSON string with AI disclosure.
            
        Raises:
            json.JSONDecodeError: If the input string is not valid JSON.
        """
        try:
            post_dict = json.loads(post_json)
            post_dict["content"] += "\n\n---\n🤖 This post was generated with the help of AI."
            
            # Add AI-related hashtags
            if isinstance(post_dict.get("hashtags"), list):
                post_dict["hashtags"].extend(["#AIGenerated", "#GeminiAI"])
            else:
                post_dict["hashtags"] = ["#AIGenerated", "#GeminiAI"]
                
            return json.dumps(post_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}") from e

    @staticmethod
    def _convert_to_linkedin_post(post_json: str) -> str:
        """Convert JSON format to LinkedIn post format.
        
        Args:
            post_json (str): JSON string containing the post content.
            
        Returns:
            str: Formatted LinkedIn post.
            
        Raises:
            ValueError: If the input JSON is invalid or missing required fields.
        """
        try:
            post_dict = json.loads(post_json)
            required_fields = ["title", "content", "hashtags", "question"]
            missing_fields = [field for field in required_fields if not post_dict.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Format the post
            post_parts = [
                post_dict["title"],
                "\n\n",
                post_dict["content"]
            ]
            
            # Add code snippet if present
            if post_dict.get("code"):
                post_parts.extend(["\n\n```c#\n", post_dict["code"], "\n```"])
            
            # Add question and hashtags
            post_parts.extend([
                "\n\n",
                post_dict["question"],
                "\n\n",
                " ".join(post_dict["hashtags"])
            ])
            
            return "".join(post_parts)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}") from e

def convert_json_to_linkedInPost(cleaned_summary:str) -> str:
     summary_dict = json.loads(cleaned_summary)

     # Extract the data
     post_title = summary_dict['title']
     post_content = summary_dict['content']
     #post_code = summary_dict['code']
     #post_question = summary_dict['question']
     post_hashtags = " ".join(summary_dict['hashtags'])


     # Combine and format into a single string
     #linkedin_post = f"""{post_title}\n\n{post_content}\n\n**Code Example:**\n```csharp\n{post_code}\n```\n\n{post_question}\n\n{post_hashtags}"""
     #linkedin_post = f"""{post_title}\n\n{post_content}\n\n{post_question}\n\n{post_hashtags}"""
     linkedin_post = f"""{post_title}\n\n{post_content}\n\n{post_hashtags}"""


     return linkedin_post
