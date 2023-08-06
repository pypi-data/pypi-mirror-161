from fastapi import HTTPException
from starlette import status


class UnauthorizedHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": 'Bearer'}
        )


class NotEnoughPermissionsHTTPException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": 'Bearer'},
        )


class NotFoundHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


class BadRequestHTTPException(HTTPException):
    def __init__(self, error_code: int, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail={"error_code": error_code, "message": detail})


class ForbiddenHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permissions to perform this action"
        )


class InternalErrorHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")


class NotImplementedHTTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not Implemented")
