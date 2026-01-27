from models.response_models import UserResponse


def user_label(u: UserResponse) -> str:
    first = (getattr(u, "first_name", "") or "").strip()
    last = (getattr(u, "last_name", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    username = (getattr(u, "username", "") or "").strip()
    full = f"{first} {last}".strip()
    return full or username or email or f"User {u.id}"
