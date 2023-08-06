import uuid


def is_valid_uuid(v) -> bool:
    try:
        uuid.UUID(v, version=4)
    except ValueError:
        return False
    return True
