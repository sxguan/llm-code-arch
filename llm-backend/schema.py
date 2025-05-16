from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    svg: Optional[str] = None

class AnalyzeRequest(BaseModel):
    github_link: str
    history: List[Message]
    force_initial: Optional[bool] = False

class AnalyzeResponse(BaseModel):
    text: str
    svg: str

class FileRequest(BaseModel):
    github_link: str
    file_path: str

class FileResponse(BaseModel):
    content: str
