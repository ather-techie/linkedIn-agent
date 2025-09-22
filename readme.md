# LinkedIn Content Generation Agent

An automated system for generating and publishing professional content to LinkedIn using Google's Gemini AI and LinkedIn's API. The system creates engaging, technical posts with code examples and handles the complete workflow from content generation to publication.

## Features

- AI-powered content generation using Google's Gemini model
- Professional post creation with code examples
- Automated LinkedIn publishing
- Error handling and validation
- Type-safe implementation
- Environment-based configuration

## Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account and API credentials
- Google Cloud Account with Gemini API access

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd linkedin-agent
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following variables:

```env
# LinkedIn API Configuration
LINKEDIN_API_URL=https://api.linkedin.com
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=your_redirect_uri
LINKEDIN_ACCESS_TOKEN=your_access_token

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro
```

## Usage

Run the main script to generate and post content:

```bash
python main.py
```

The script will:
1. Generate a LinkedIn post about the specified topic
2. Validate the content
3. Add AI disclosure if configured
4. Post to LinkedIn using the provided credentials

## Project Structure

```
linkedin-agent/
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
├── src/
│   ├── services/
│   │   ├── linkedin_service.py       # LinkedIn API integration
│   │   └── autogen_gemini_service.py # Content generation with Gemini
│   ├── agents/            # AI agent implementations
│   ├── utils/             # Utility functions
│   └── workflows/         # Business logic workflows
└── tests/                 # Test suite
```

## Content Generation Process

1. **Topic Selection**
   - Predefined topics (e.g., ["C# Generics", "LINQ Basics", "Async/Await"])
   - Option to integrate with trending topics from GitHub/Stack Overflow

2. **Content Generation Pipeline**
   - Writer Agent creates initial content
   - Critic Agent reviews and suggests improvements
   - Final post includes:
     - Professional title
     - Engaging content
     - Code examples
     - Discussion question
     - Relevant hashtags
     - AI disclosure (optional)

3. **Publishing**
   - Content validation
   - LinkedIn API authentication
   - Post creation with proper formatting
   - Error handling and reporting

## Error Handling

The system includes comprehensive error handling for:
- LinkedIn API issues
- Content generation failures
- Authentication problems
- Configuration errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini AI
- LinkedIn API
- AutoGen framework
