def validate_user(name, email):
    if not name:
        return False

    if not email or "@" not in email:
        return False

    return True


def validate_task(title, description):
    if not title:
        return False

    if not description:
        return False

    return True