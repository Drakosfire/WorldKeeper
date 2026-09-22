"""World Keeper's narrowly authorized WK-2 read-only authority boundary."""

from .application.authority import (
    AuthorityIntegrityFailure,
    AuthorityUnavailable,
    ExactRevisionWitness,
    FinalizedPublicationWitness,
    GovernedWorldAuthority,
    SourceRevisionWitness,
    WorldHeadWitness,
)

__all__ = [
    "AuthorityIntegrityFailure",
    "AuthorityUnavailable",
    "ExactRevisionWitness",
    "FinalizedPublicationWitness",
    "GovernedWorldAuthority",
    "SourceRevisionWitness",
    "WorldHeadWitness",
]
