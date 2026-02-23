"""Logging setup and sensitive data masking."""
import logging
import sys


def setup_logging(verbose: int = 0) -> None:
    """Configure logging level based on verbosity flag.
    verbose=0 → WARNING, verbose=1 → INFO, verbose=2+ → DEBUG
    """
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


def mask_sensitive(token: str, keep_chars: int = 4) -> str:
    """Mask a sensitive token, keeping only the last keep_chars characters."""
    if len(token) <= keep_chars:
        return "****"
    return f"****{token[-keep_chars:]}"
