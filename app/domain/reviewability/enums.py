from enum import StrEnum


class ReviewabilityState(StrEnum):
    NOT_REVIEWABLE = "not_reviewable"
    REVIEWABLE = "reviewable"


class ReviewabilityRequirement(StrEnum):
    DESIGN_PRESENT = "design present"
    CANDIDATE_PRESENT = "candidate present"
    CHALLENGE_PRESENT = "challenge present"
    VERIFICATION_PRESENT = "verification present"
    NON_AUTHORITATIVE_NOTICE_PRESENT = "non-authoritative notice present"
    EXPLICIT_SCOPE_BOUNDARY_PRESENT = "explicit scope boundary statement present"
    PARENT_REFS_VALID = "parent refs valid"
    NO_UNRESOLVED_SCOPE_ESCAPE = "no unresolved scope escape"
    NO_BROKEN_LINEAGE_CONDITION = "no broken lineage condition"


class NotReviewableReason(StrEnum):
    MISSING_CHALLENGE_ARTIFACT = "missing challenge artifact"
    MISSING_VERIFICATION_ARTIFACT = "missing verification artifact"
    MISSING_SOURCE_REFS = "missing source refs"
    SCOPE_ESCAPE_DETECTED = "scope escape detected"
    INVALID_PARENT_EVIDENCE_REFS = "invalid parent evidence refs"
    MISSING_DOWNGRADE_FACTORS = "confidence summary missing downgrade factors"
    MISSING_REQUIRED_ROLLBACK_CLASS = "rollback class required but absent"


class ProposalLifecycleState(StrEnum):
    DRAFT = "draft"
    PACKAGED = "packaged"
    QUEUED_FOR_OPERATOR_REVIEW = "queued_for_operator_review"
    UNDER_OPERATOR_REVIEW = "under_operator_review"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class OperatorDecisionState(StrEnum):
    NO_DECISION = "no_decision"
    ACCEPTED_BY_OPERATOR = "accepted_by_operator"
    REJECTED_BY_OPERATOR = "rejected_by_operator"
    CHANGES_REQUESTED_BY_OPERATOR = "changes_requested_by_operator"
    DEFERRED_BY_OPERATOR = "deferred_by_operator"


class AllowedLanguageToken(StrEnum):
    PROPOSE = "propose"
    HYPOTHESIZE = "hypothesize"
    SUGGEST = "suggest"
    INDICATE = "indicate"
    CANDIDATE = "candidate"
    CHALLENGE = "challenge"
    OBSERVED_CANDIDATE_GAIN = "observed candidate gain"
    REVIEWABILITY_STATE = "reviewability state"
    RESIDUAL_CONCERN = "residual concern"


class ProhibitedLanguageToken(StrEnum):
    APPROVED = "approved"
    CONFIRMED_FIX = "confirmed fix"
    PROVEN_TRUTH = "proven truth"
    AUTHORITATIVE_STATE = "authoritative state"
    MUST_APPLY = "must apply"
    MERGE_NOW = "merge now"


def contains_non_authoritative_language(text: str) -> bool:
    lowered = text.casefold()
    return any(token.value in lowered for token in AllowedLanguageToken)


def contains_prohibited_authoritative_language(text: str) -> bool:
    lowered = text.casefold()
    return any(token.value in lowered for token in ProhibitedLanguageToken)
