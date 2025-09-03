from pydantic import BaseModel
from typing import Optional, Any

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    code: int
    def __init__(self, success: bool, message: str, data: Optional[Any], code: int):
        super().__init__(success=success, message=message, code=code, data=data)