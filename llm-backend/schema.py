from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    svg: Optional[str] = None

class AnalyzeRequest(BaseModel):
    github_link: str
    history: List[Message]
    force_initial: Optional[bool] = False
    drill_down_module: Optional[str] = None  # For drilling into specific module
    current_path: Optional[List[str]] = None  # Navigation breadcrumb

class AnalyzeResponse(BaseModel):
    text: str
    svg: str
    level: Optional[str] = "overview"  # "overview" or "module"
    current_module: Optional[str] = None
    navigation_path: Optional[List[str]] = None

class FileRequest(BaseModel):
    github_link: str
    file_path: str

class FileResponse(BaseModel):
    content: str
