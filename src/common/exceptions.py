class MalformedPrompt(Exception):
    """Raised when a prompt file is malformed or cannot be read."""

    pass


class FacetInferenceError(Exception):
    """Base exception for facet inference errors."""
    pass


class PredictionError(FacetInferenceError):
    """Raised when prediction fails."""
    pass
