def validate_user(name, email):
    if not name:
        return False

    if not email or "@" not in email:
        return False

    return True


def validate_priority(priority):
    return priority in {"low", "medium", "high"}


def validate_task(title, description, priority="medium"):
    if not title:
        return False

    if not description:
        return False

    if not validate_priority(priority):
        return False

    return True