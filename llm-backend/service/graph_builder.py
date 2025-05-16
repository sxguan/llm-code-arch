import graphviz
import os
import re
import json
from anthropic import Anthropic
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_architecture_svg(github_link: str, project_structure: str) -> str:
    """
    Generate architecture SVG based on project structure
    """
    try:
        print(f"Generating SVG for {github_link}")
        print(f"Project structure size: {len(project_structure)} characters")
        
        # Use LLM to filter and analyze important components
        filtered_components = analyze_project_with_llm(github_link, project_structure)
        
        dot = graphviz.Digraph()
        # Use LR (left to right) for better wide diagram handling
        dot.attr(rankdir="LR")
        
        # Extract repository name from GitHub link
        repo_name = github_link.split("/")[-1].replace(".git", "")
        dot.attr(label=f"Architecture of {repo_name}", fontsize="20")
        
        if filtered_components:
            # Use the LLM-filtered components
            print(f"Using {len(filtered_components)} components identified by LLM")
            
            # Add nodes for each major component
            for component in filtered_components:
                label = f"{component['name']}\n{component['description']}"
                dot.node(component['name'], label, shape="box", style="rounded,filled", fillcolor="lightskyblue")
            
            # Add relationships
            for component in filtered_components:
                for dependency in component.get('dependencies', []):
                    dot.edge(component['name'], dependency, 
                             label=component.get('dependency_details', {}).get(dependency, ''))
        else:
            # Fallback to traditional parsing if LLM analysis fails
            print("Falling back to traditional project structure parsing")
            components = parse_project_structure(project_structure)
            print(f"Parsed {len(components)} components from project structure")
            
            # Add nodes for each major component
            for component, details in components.items():
                if component == "root":
                    continue
                
                # Create node with component name and file count
                label = f"{component}\n({len(details['files'])} files)"
                dot.node(component, label)
                
                # Add edges for dependencies
                for dependency in details.get('dependencies', []):
                    if dependency in components and dependency != component:
                        dot.edge(component, dependency)
            
            # Add relationships based on imports and references
            add_relationships(dot, components)
        
        # Ensure the result is a valid SVG
        svg_result = dot.pipe(format='svg').decode("utf-8")
        print(f"Generated SVG of length: {len(svg_result)}")
        
        # Validate basic SVG format
        if not svg_result.startswith('<svg') and not '<!DOCTYPE svg' in svg_result:
            print("Warning: Generated SVG doesn't have expected format")
            # If graphviz output is not a valid SVG, return a simple default SVG
            return create_default_svg(github_link, components if 'components' in locals() else {})
            
        return svg_result
    except Exception as e:
        print(f"Error in generate_architecture_svg: {str(e)}")
        # Return a simple error SVG instead of throwing an exception
        return create_error_svg(github_link, str(e))

def analyze_project_with_llm(github_link: str, project_structure: str) -> List[Dict]:
    """
    Use LLM to analyze project structure and identify important components.
    
    Returns a list of component dictionaries with:
    - name: Component name
    - description: Brief description of the component's purpose
    - dependencies: List of other components this depends on
    - dependency_details: Dict mapping dependency names to relationship descriptions
    """
    try:
        # Skip for empty project structures or error messages
        if not project_structure or project_structure.startswith("[Error"):
            print("Project structure is empty or contains errors - skipping LLM analysis")
            return []
            
        print("Analyzing project structure with LLM...")
        
        system_prompt = """You are an expert software architect analyzing a GitHub repository.
Your task is to identify the main architectural components and their relationships.
For complex repositories with many files, focus only on the most important 5-8 core components.
Provide a clear, concise analysis that highlights the key architectural relationships.

The output must be valid JSON in this format:
[
  {
    "name": "ComponentName",
    "description": "Brief description of component purpose (1-2 lines)",
    "dependencies": ["OtherComponent1", "OtherComponent2"],
    "dependency_details": {
      "OtherComponent1": "Brief description of relationship",
      "OtherComponent2": "Brief description of relationship"
    }
  }
]

Important rules:
1. Focus on major architectural components, not individual files
2. Group related files and directories into logical components
3. Keep component names concise but descriptive
4. Identify clear dependencies between components
5. Limit to 5-8 core components for better diagram readability
6. Ensure all dependency names match exactly with component names
7. If you're not confident about a relationship, don't include it
"""
        
        repo_name = github_link.split("/")[-1].replace(".git", "")
        user_message = f"""Analyze this GitHub repository: {github_link}

Project structure:
```
{project_structure}
```

Identify the 5-8 most important architectural components and their relationships.
Return ONLY JSON without any additional text."""

        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=2000,
            temperature=0.2
        )
        
        # Extract JSON from response
        response_text = response.content[0].text
        
        # Find JSON content (may be wrapped in ```json blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response_text
            
        # Parse the JSON response
        try:
            components = json.loads(json_str)
            print(f"Successfully parsed {len(components)} components from LLM")
            return components
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {response_text}")
            return []
            
    except Exception as e:
        print(f"Error in analyze_project_with_llm: {str(e)}")
        return []

def create_default_svg(github_link: str, components: dict) -> str:
    """Create a simple default SVG as a fallback option"""
    repo_name = github_link.split("/")[-1].replace(".git", "")
    
    # Remove root key
    if "root" in components:
        del components["root"]
    
    component_list = "\n".join([f'<text x="50" y="{50 + i*20}" font-size="14">{comp} ({len(details["files"])} files)</text>' 
                               for i, (comp, details) in enumerate(components.items())])
    
    if not component_list:
        component_list = '<text x="50" y="50" font-size="14">No major components identified</text>'
    
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="{max(300, 50 + len(components) * 20 + 50)}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#f0f0f0"></rect>
  <text x="50" y="30" font-size="18" font-weight="bold">Architecture of {repo_name}</text>
  {component_list}
  <text x="50" y="{50 + max(1, len(components)) * 20 + 30}" font-size="14" fill="#666">Note: This is a simplified diagram showing important components only</text>
</svg>'''
    return svg

def create_error_svg(github_link: str, error_message: str) -> str:
    """Create an error message SVG"""
    repo_name = github_link.split("/")[-1].replace(".git", "")
    
    # Escape XML special characters in error message
    error_message = error_message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="250" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#fff0f0"></rect>
  <text x="50" y="30" font-size="18" font-weight="bold">Architecture of {repo_name}</text>
  <text x="50" y="70" font-size="14" fill="#cc0000">Error generating architecture:</text>
  <text x="50" y="100" font-size="12" fill="#666">{error_message}</text>
  <text x="50" y="150" font-size="14">Please try another repository or check the logs</text>
  <text x="50" y="180" font-size="14">For large projects, the architecture diagram shows only key components</text>
</svg>'''
    return svg

def parse_project_structure(structure: str) -> dict:
    """
    Parse project structure string into components dictionary
    """
    components = {
        "root": {"files": [], "dependencies": []}
    }
    
    # Common component patterns to identify
    patterns = {
        "frontend": ["web", "ui", "frontend", "client", "react", "vue", "angular", "html"],
        "backend": ["api", "server", "backend", "service", "controller"],
        "database": ["db", "database", "model", "entity", "repository"],
        "utils": ["util", "helper", "common", "lib"],
        "tests": ["test", "spec", "mock"],
        "config": ["config", "settings", "env"],
        "docs": ["doc", "documentation", "readme", "wiki"]
    }
    
    lines = structure.split("\n")
    current_dir = "root"
    dir_stack = []
    indent_level = 0
    
    for line in lines:
        if not line.strip():
            continue
            
        # Calculate current indent level
        current_indent = len(line) - len(line.lstrip())
        
        # Handle directory changes based on indentation
        if current_indent < indent_level:
            # Going back up in the directory tree
            levels_up = (indent_level - current_indent) // 4
            for _ in range(levels_up):
                if dir_stack:
                    dir_stack.pop()
            current_dir = dir_stack[-1] if dir_stack else "root"
            indent_level = current_indent
        
        # Extract file or directory name
        name = line.strip().rstrip('/')
        
        if line.strip().endswith('/'):
            # This is a directory
            dir_name = name.lower()
            
            # Identify component type based on directory name
            component_type = None
            for ctype, keywords in patterns.items():
                if any(keyword in dir_name for keyword in keywords):
                    component_type = ctype
                    break
            
            # If no specific type found, use directory name
            if not component_type:
                component_type = dir_name
                
            # Skip node_modules, .git and other common non-essential directories
            if dir_name in ["node_modules", ".git", "__pycache__", "venv", "env", ".vscode", ".idea"]:
                continue
                
            # Add component if it doesn't exist
            if component_type not in components:
                components[component_type] = {"files": [], "dependencies": []}
            
            # Update directory tracking
            current_dir = component_type
            dir_stack.append(current_dir)
            indent_level = current_indent
        else:
            # This is a file
            components[current_dir]["files"].append(name)
            
            # Add dependencies based on file type
            file_ext = os.path.splitext(name)[1].lower()
            if file_ext in ['.py', '.js', '.ts', '.java', '.go', '.rb']:
                if "database" not in components[current_dir]["dependencies"] and any(db_term in name.lower() for db_term in ["db", "dao", "repository", "model"]):
                    components[current_dir]["dependencies"].append("database")
    
    # Clean up components with no files
    return {k: v for k, v in components.items() if v["files"] or k == "root"}

def add_relationships(dot, components):
    """
    Add relationships between components based on common patterns
    """
    # Common relationships in applications
    if "frontend" in components and "backend" in components:
        dot.edge("frontend", "backend")
    
    if "backend" in components and "database" in components:
        dot.edge("backend", "database")
    
    if "api" in components and "service" in components:
        dot.edge("api", "service")
        
    if "service" in components and "database" in components:
        dot.edge("service", "database")
    
    if "controller" in components and "service" in components:
        dot.edge("controller", "service")
        
    # Add utils as dependency for most components
    if "utils" in components:
        for component in components:
            if component not in ["utils", "root", "docs", "tests"]:
                dot.edge(component, "utils", style="dashed")
