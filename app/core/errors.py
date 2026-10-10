from exception import CustomException
from logger import get_logger

logger = get_logger(__name__)

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def raise_custom(message: str, exc: Exception | None = None):
    logger.error(message, exc_info=exc is not None)
    raise CustomException(message, exc)
