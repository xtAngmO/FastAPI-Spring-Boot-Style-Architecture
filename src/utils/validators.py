from email_validator import EmailNotValidError, validate_email

from src.exceptions.badrequest_error import BadRequestError


def validate_email_format(email: str | None) -> str | None:
    if not email:
        return None
    try:
        return validate_email(email).email
    except EmailNotValidError as e:
        raise BadRequestError(f"Invalid email format: {e!s}") from e
