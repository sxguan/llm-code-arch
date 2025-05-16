import os
import tempfile
import git
from pathlib import Path

def get_project_structure(github_link: str) -> str:
    """
    Clone a GitHub repository and return its directory structure as a string.
    
    Args:
        github_link: URL of the GitHub repository
        
    Returns:
        String representation of the project structure
    """
    try:
        print(f"Attempting to clone repository: {github_link}")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone the repository
            try:
                git.Repo.clone_from(github_link, tmpdir, depth=1)
            except git.exc.GitCommandError as e:
                error_message = str(e)
                if "not found" in error_message.lower() or "404" in error_message:
                    print(f"Repository does not exist or is not accessible: {github_link}")
                    return f"[Error: Repository not found or not accessible: {github_link}]"
                elif "authentication" in error_message.lower():
                    print(f"Unable to access private repository: {github_link}")
                    return f"[Error: Repository is private and requires authentication: {github_link}]"
                else:
                    print(f"Error cloning repository: {error_message}")
                    return f"[Error cloning repository]: {error_message}"
            
            # Generate directory structure
            structure = []
            root_path = Path(tmpdir)
            
            # Directories/files to ignore
            ignore_patterns = [
                '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
                '.DS_Store', '.env', 'venv', 'env', '.pytest_cache'
            ]
            
            def should_ignore(path):
                for pattern in ignore_patterns:
                    if pattern in path.parts:
                        return True
                return False
            
            # Generate tree structure
            for path in sorted(root_path.glob('**/*')):
                if should_ignore(path):
                    continue
                
                # Get relative path from the root
                rel_path = path.relative_to(root_path)
                depth = len(rel_path.parts) - 1
                
                # Format the entry
                prefix = '    ' * depth
                name = rel_path.parts[-1]
                
                if path.is_dir():
                    structure.append(f"{prefix}{name}/")
                else:
                    structure.append(f"{prefix}{name}")
            
            if not structure:
                print(f"Repository is empty or has no valid files: {github_link}")
                return f"[Warning: Repository appears to be empty: {github_link}]"
                
            return '\n'.join(structure)
            
    except git.exc.GitCommandError as e:
        error_msg = f"[Error cloning repository]: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"[Error analyzing repository]: {str(e)}"
        print(error_msg)
        return error_msg

def get_file_content(github_link: str, file_path: str) -> str:
    """
    Get the content of a specific file from a GitHub repository.
    
    Args:
        github_link: URL of the GitHub repository
        file_path: Path to the file within the repository
        
    Returns:
        Content of the file as a string
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone the repository
            git.Repo.clone_from(github_link, tmpdir, depth=1)
            
            # Read the file
            full_path = os.path.join(tmpdir, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            else:
                return f"[Error]: File {file_path} not found in repository"
            
    except Exception as e:
        return f"[Error reading file]: {str(e)}"
