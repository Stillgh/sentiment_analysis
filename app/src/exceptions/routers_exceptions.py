from fastapi import HTTPException
from starlette import status

admin_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="To access that page you should be admin."
)

