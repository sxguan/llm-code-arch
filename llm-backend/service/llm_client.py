import os
from anthropic import Anthropic
from schema import Message
from dotenv import load_dotenv
from service.github_analyzer import get_file_content

load_dotenv()
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_with_claude(history: list[Message], github_link: str, structure: str, drill_down_module: str = None, file_content: dict = None) -> str:
    # Convert historical messages to Anthropic Messages API format
    messages = []
    
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Prepare system message
    system_content = f"""You are analyzing a GitHub repository at {github_link}."""
    
    # Check if project structure contains error information
    if structure and structure.startswith("[Error"):
        system_content += f"""
        
There was an issue accessing the repository: {structure}
        
Please inform the user about this issue and offer suggestions for next steps.
If the repository is private, suggest they provide a public repository link.
If the repository doesn't exist, suggest they check the URL and try again.
"""
    else:
        # Normal project structure analysis
        system_content += f"""
        
Project Structure:
```
{structure}
```"""

    # If there is file content, add it to the system message
    if file_content:
        for file_path, content in file_content.items():
            system_content += f"""

File: {file_path}
```
{content}
```"""
    
    # If there are no historical messages, add initial user message
    if not history:
        if drill_down_module:
            system_content += f"""
Please provide a detailed analysis of the "{drill_down_module}" module specifically:
1. Internal architecture and subcomponents
2. Key functions and responsibilities
3. Dependencies and relationships within the module
4. File organization and structure
5. Data flow within the module
6. Key design patterns used

Focus specifically on the {drill_down_module} module and its internal architecture."""
            
            messages = [
                {"role": "user", "content": f"Please analyze the {drill_down_module} module in detail from this GitHub repository: {github_link}"}
            ]
        else:
            system_content += """
Please provide:
1. A high-level overview of the project architecture
2. The key components and their responsibilities
3. How data flows between components
4. The design patterns used (if identifiable)
5. The technologies/frameworks used
6. Any architectural strengths or potential improvements

Be concise but thorough in your analysis."""
            
            messages = [
                {"role": "user", "content": f"Please analyze this GitHub repository: {github_link}"}
            ]

    # Use Messages API with system message as a top-level parameter
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        system=system_content,
        messages=messages,
        max_tokens=2000,
        temperature=0.5
    )

    return response.content[0].text


# def analyze_with_claude(history: list[Message], github_link: str, structure: str) -> str:
#     # Mock Claude analysis response
#     return f"""
# This GitHub repository at {github_link} appears to be a blockchain-based education system.

# 📁 Project Structure:
# {structure}

# 🧠 Key Components:
# - `main.py`: Application entry point.
# - `service/`: Business logic and API handling.
# - `chaincode/`: Smart contract logic.
# - `sdk/`: Interface to Hyperledger Fabric.

# ➡️ Data likely flows from Web UI → Service Layer → Fabric SDK → Chaincode.

# 📝 Note: This is a mock response. Replace with real Claude output later.
# """