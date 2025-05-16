# LLM Code Architecture Analyzer

This project uses LLM (Claude) to analyze GitHub repositories and generate architecture diagrams. It provides a ChatGPT-like interface where users can input a GitHub repository link and ask questions about the codebase.

## Features

- **GitHub Repository Analysis**: Automatically clones and analyzes the structure of GitHub repositories
- **Architecture Diagram Generation**: Creates visual diagrams showing the components and relationships in the codebase
- **Interactive Q&A**: Chat with the LLM about the codebase to understand its architecture
- **File Content Retrieval**: View the content of specific files in the repository
- **Web UI**: Simple and intuitive interface similar to ChatGPT

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Install Graphviz (required for diagram generation):
   - **macOS**: `brew install graphviz`
   - **Ubuntu/Debian**: `apt-get install graphviz`
   - **Windows**: Download from [Graphviz website](https://graphviz.org/download/)

## Running the Application

1. Start the backend server:
   ```
   uvicorn main:app --reload
   ```
2. Start your frontend application (pointing to `http://localhost:8000` for the API)

## API Endpoints

- **POST /analyze**: Main endpoint for analyzing repositories and asking questions
  - Request body:
    ```json
    {
      "github_link": "https://github.com/username/repository",
      "history": [
        {
          "role": "user",
          "content": "What is the main architecture of this project?"
        }
      ]
    }
    ```
  - Response:
    ```json
    {
      "text": "LLM analysis of the codebase...",
      "svg": "<svg>...</svg>"
    }
    ```

- **POST /file**: Endpoint for retrieving file content from the repository
  - Request body:
    ```json
    {
      "github_link": "https://github.com/username/repository",
      "file_path": "path/to/file.py"
    }
    ```
  - Response:
    ```json
    {
      "content": "file content as string..."
    }
    ```

## Architecture

- **main.py**: FastAPI application entry point
- **service/github_analyzer.py**: Handles GitHub repository cloning and structure analysis
- **service/graph_builder.py**: Generates architecture diagrams based on codebase structure
- **service/llm_client.py**: Interfaces with Claude API for code analysis
- **schema.py**: Pydantic models for request/response validation

## License

MIT 