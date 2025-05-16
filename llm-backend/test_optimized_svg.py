#!/usr/bin/env python3
"""
Test optimized SVG generation for large repositories
"""
import sys
from service.github_analyzer import get_project_structure
from service.graph_builder import generate_architecture_svg

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_optimized_svg.py <github_repository_url>")
        print("Example: python test_optimized_svg.py https://github.com/fastapi-users/fastapi-users")
        sys.exit(1)
        
    github_link = sys.argv[1]
    print(f"Analyzing repository: {github_link}")
    
    # Get project structure
    print("Getting project structure...")
    structure = get_project_structure(github_link)
    
    if structure.startswith("[Error"):
        print(f"Error: {structure}")
        sys.exit(1)
        
    print(f"Project structure size: {len(structure)} characters")
    
    # Generate SVG
    print("Generating optimized architecture diagram...")
    svg = generate_architecture_svg(github_link, structure)
    
    # Save SVG to file
    filename = f"optimized_{github_link.split('/')[-1]}.svg"
    with open(filename, "w") as f:
        f.write(svg)
        
    print(f"SVG saved to {filename}")
    
    # Also save HTML for viewing
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Optimized Architecture Diagram</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .diagram {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
        .note {{ font-style: italic; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Optimized Architecture Diagram for {github_link.split('/')[-1]}</h1>
    <p>LLM-assisted diagram showing only key architectural components</p>
    <div class="diagram">
        {svg}
    </div>
    <p class="note">For large projects, only the most important components are shown to improve readability.</p>
</body>
</html>"""
    
    html_filename = f"optimized_{github_link.split('/')[-1]}.html"
    with open(html_filename, "w") as f:
        f.write(html)
        
    print(f"HTML view saved to {html_filename}")
    print(f"Open {html_filename} in a browser to view the diagram")
    
if __name__ == "__main__":
    main() 