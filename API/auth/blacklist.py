from typing import Set

# In-Memory Blacklist (für Production: Redis verwenden)
blacklisted_tokens: Set[str] = set()


def add_to_blacklist(token: str):
    """Add a token to the blacklist."""
    blacklisted_tokens.add(token)


def is_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    return token in blacklisted_tokens
