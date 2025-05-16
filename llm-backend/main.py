from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from schema import AnalyzeRequest, AnalyzeResponse, FileRequest, FileResponse
from service.llm_client import analyze_with_claude
from service.graph_builder import generate_architecture_svg, create_error_svg
from service.github_analyzer import get_project_structure, get_file_content
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI(
    title="LLM Code Architecture Analyzer API",
    description="API for analyzing GitHub repositories and generating architecture diagrams using LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080", "http://localhost:8081"],  
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Function to validate GitHub links
def is_valid_github_link(link):
    """Validate if the GitHub link format is correct"""
    if not link:
        return False
    return link.startswith("https://github.com/") or link.startswith("http://github.com/")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>LLM Code Architecture Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
                .endpoint { margin-bottom: 30px; }
            </style>
        </head>
        <body>
            <h1>LLM Code Architecture Analyzer API</h1>
            <p>This API allows you to analyze GitHub repositories and generate architecture diagrams using LLM.</p>
            
            <div class="endpoint">
                <h2>POST /analyze</h2>
                <p>Analyze a GitHub repository and generate an architecture diagram.</p>
                <h3>Request:</h3>
                <pre>
{
  "github_link": "https://github.com/username/repository",
  "history": [
    {
      "role": "user",
      "content": "What is the main architecture of this project?"
    }
  ]
}
                </pre>
                <h3>Response:</h3>
                <pre>
{
  "text": "LLM analysis of the codebase...",
  "svg": "&lt;svg&gt;...&lt;/svg&gt;"
}
                </pre>
            </div>
            
            <div class="endpoint">
                <h2>POST /file</h2>
                <p>Retrieve the content of a specific file from a GitHub repository.</p>
                <h3>Request:</h3>
                <pre>
{
  "github_link": "https://github.com/username/repository",
  "file_path": "path/to/file.py"
}
                </pre>
                <h3>Response:</h3>
                <pre>
{
  "content": "file content as string..."
}
                </pre>
            </div>
        </body>
    </html>
    """

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        print(f"\n======== Start Processing Request ========")
        print(f"Received request for GitHub link: {request.github_link}")
        print(f"Has history: {len(request.history) > 0}")
        print(f"Force initial: {request.force_initial}")
        
        # If force_initial is True or history is empty, treat as initial request
        is_initial_request = request.force_initial or len(request.history) == 0
        print(f"Is initial request: {is_initial_request}")
        
        repository_error = None
        
        # For non-initial requests, don't strictly validate GitHub link
        if not is_initial_request:
            # No need to strictly validate GitHub link for follow-up conversations
            print(f"Follow-up conversation, skipping GitHub link validation")
            pass
        else:
            # Validate GitHub link
            if not is_valid_github_link(request.github_link):
                print(f"Invalid GitHub link: {request.github_link}")
                raise HTTPException(status_code=400, detail="Invalid GitHub link")
            
            print(f"Valid GitHub link: {request.github_link}")

        # Get project structure
        project_structure = ""
        if is_initial_request:
            try:
                # For initial requests, get project structure
                print(f"Getting project structure...")
                project_structure = get_project_structure(request.github_link)
                print(f"Project structure length: {len(project_structure)}")
                
                # Check if there's an error message
                if project_structure.startswith("[Error"):
                    repository_error = project_structure
                    print(f"Project structure contains error: {repository_error}")
                else:
                    print(f"Project structure retrieved successfully, preview: {project_structure[:100]}...")
                
            except Exception as e:
                error_msg = f"Failed to analyze repository: {str(e)}"
                print(f"Error getting project structure: {error_msg}")
                repository_error = error_msg
                # Create an empty project structure instead of failing
                project_structure = ""
        else:
            # For follow-up requests, no need to get project structure
            print(f"Follow-up conversation, not retrieving project structure")
            project_structure = ""
        
        # Use Claude for analysis - fixed parameter order
        print(f"Calling Claude for analysis...")
        response_text = analyze_with_claude(request.history, request.github_link, project_structure)
        print(f"Claude analysis complete, response length: {len(response_text)}")
        
        # For initial requests, generate architecture diagram; for follow-up requests, return empty SVG
        svg_content = ""
        if is_initial_request:
            try:
                print(f"Starting architecture diagram generation...")
                # Try to generate a minimal architecture diagram even if repo is inaccessible
                if repository_error:
                    # Create a simple error architecture diagram
                    print(f"Generating error architecture diagram with error info: {repository_error}")
                    svg_content = create_error_svg(request.github_link, repository_error)
                    print(f"Error architecture diagram generation complete, length: {len(svg_content)}")
                else:
                    # Correctly pass project_structure as the second parameter
                    print(f"Generating architecture diagram using project structure...")
                    svg_content = generate_architecture_svg(request.github_link, project_structure)
                    print(f"Architecture diagram generation complete, length: {len(svg_content)}")
                
                if svg_content:
                    print(f"SVG preview: {svg_content[:100]}...")
                else:
                    print(f"Warning: Generated SVG content is empty")
            except Exception as e:
                print(f"Error generating architecture diagram: {str(e)}")
                print(f"Attempting to generate error architecture diagram...")
                svg_content = create_error_svg(request.github_link, str(e))
                print(f"Error architecture diagram generation complete, length: {len(svg_content)}")
        else:
            print(f"Follow-up conversation, not generating architecture diagram")
        
        # Construct and return response
        response = AnalyzeResponse(text=response_text, svg=svg_content)
        print(f"Returning response, SVG length: {len(svg_content)}")
        print(f"======== Request Processing Complete ========\n")
        return response
        
    except Exception as e:
        print(f"Unexpected error in request processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/file", response_model=FileResponse)
async def get_file(request: FileRequest):
    try:
        # Validate GitHub link
        if not request.github_link or not (request.github_link.startswith("https://github.com/") or 
                                         request.github_link.startswith("http://github.com/")):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository link")
            
        # Validate file path
        if not request.file_path or len(request.file_path.strip()) == 0:
            raise HTTPException(status_code=400, detail="File path cannot be empty")
            
        # Get file content from GitHub repository
        content = get_file_content(request.github_link, request.file_path)
        
        # Check if there was an error getting the file content
        if content.startswith("[Error"):
            raise HTTPException(status_code=404, detail=content)
            
        return FileResponse(content=content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
