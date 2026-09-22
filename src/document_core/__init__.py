"""Deterministic document-core adapters for governed canonical inputs."""

from .canonical_requirements_adapter import (
    CanonicalRequirementsError,
    adapt_canonical_requirements,
    load_canonical_requirements,
)

__all__ = [
    "CanonicalRequirementsError",
    "adapt_canonical_requirements",
    "load_canonical_requirements",
    "RequirementLocalValidationError",
    "validate_requirement_rules",
]

from .requirement_local_validator import (
    RequirementLocalValidationError,
    validate_requirement_rules,
)
