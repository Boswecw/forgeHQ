"""GENERATED from code_fix_taxonomy.v1.json — DO NOT EDIT.

Regenerate with: python -m app.domain.taxonomy.generate
Edits belong in the canonical JSON source, then regenerate.
"""
from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import Final, Mapping

TAXONOMY_VERSION: Final[str] = 'code-fix-taxonomy.v1'

class Family(StrEnum):
    CODE_FIX = 'code_fix'
    CODE_GENERATION = 'code_generation'
    CODE_REVIEW = 'code_review'
    PLANNING = 'planning'
    RESEARCH = 'research'
    ANALYSIS = 'analysis'
    LITERARY = 'literary'
    MARKET = 'market'
    GENERAL = 'general'


class FixKind(StrEnum):
    HYGIENE = 'hygiene'
    FORMAT = 'format'
    IMPORTS = 'imports'
    LINT = 'lint'
    TYPO_NAMING = 'typo_naming'
    TYPE_ANNOTATION = 'type_annotation'
    SIGNATURE = 'signature'
    REFACTOR_MECHANICAL = 'refactor_mechanical'
    BUGFIX_LOGIC = 'bugfix_logic'
    BUGFIX_EDGECASE = 'bugfix_edgecase'
    ERROR_HANDLING = 'error_handling'
    CONCURRENCY = 'concurrency'
    SECURITY = 'security'
    PERFORMANCE = 'performance'
    DATA_MIGRATION = 'data_migration'
    DEPENDENCY = 'dependency'
    API_CONTRACT = 'api_contract'
    CONFIG_BUILD = 'config_build'
    TEST_FIX = 'test_fix'
    TEST_ADD = 'test_add'
    DOCS = 'docs'
    I18N_LOCALIZATION = 'i18n_localization'
    UNKNOWN = 'unknown'


class Language(StrEnum):
    PYTHON = 'python'
    RUST = 'rust'
    TYPESCRIPT = 'typescript'
    JAVASCRIPT = 'javascript'
    GO = 'go'
    JAVA = 'java'
    CSHARP = 'csharp'
    SQL = 'sql'
    SHELL = 'shell'
    CONFIG = 'config'
    WEB = 'web'
    MARKDOWN = 'markdown'
    DOCKERFILE = 'dockerfile'
    OTHER = 'other'


class Complexity(StrEnum):
    TRIVIAL = 'trivial'
    LOCAL = 'local'
    BOUNDED = 'bounded'
    BROAD = 'broad'


class Risk(StrEnum):
    STANDARD = 'standard'
    GOVERNANCE_CRITICAL = 'governance_critical'


COMPLEXITY_ORDER: Final[tuple[str, ...]] = ('trivial', 'local', 'bounded', 'broad')
RISK_ORDER: Final[tuple[str, ...]] = ('standard', 'governance_critical')

KIND_GROUP: Final[Mapping[str, str]] = MappingProxyType({'hygiene': 'trivial_mechanical', 'format': 'trivial_mechanical', 'imports': 'trivial_mechanical', 'lint': 'trivial_mechanical', 'typo_naming': 'trivial_mechanical', 'type_annotation': 'structural', 'signature': 'structural', 'refactor_mechanical': 'structural', 'bugfix_logic': 'behavioral', 'bugfix_edgecase': 'behavioral', 'error_handling': 'behavioral', 'concurrency': 'hard_specialized', 'security': 'hard_specialized', 'performance': 'hard_specialized', 'data_migration': 'hard_specialized', 'dependency': 'integration', 'api_contract': 'integration', 'config_build': 'integration', 'test_fix': 'auxiliary', 'test_add': 'auxiliary', 'docs': 'auxiliary', 'i18n_localization': 'auxiliary', 'unknown': 'auxiliary'})
KIND_RISK_FLOOR: Final[Mapping[str, str]] = MappingProxyType({'hygiene': 'standard', 'format': 'standard', 'imports': 'standard', 'lint': 'standard', 'typo_naming': 'standard', 'type_annotation': 'standard', 'signature': 'standard', 'refactor_mechanical': 'standard', 'bugfix_logic': 'standard', 'bugfix_edgecase': 'standard', 'error_handling': 'standard', 'concurrency': 'governance_critical', 'security': 'governance_critical', 'performance': 'standard', 'data_migration': 'governance_critical', 'dependency': 'standard', 'api_contract': 'standard', 'config_build': 'standard', 'test_fix': 'standard', 'test_add': 'standard', 'docs': 'standard', 'i18n_localization': 'standard', 'unknown': 'standard'})
KIND_TYPICAL_COMPLEXITY: Final[Mapping[str, str]] = MappingProxyType({'hygiene': 'trivial', 'format': 'trivial', 'imports': 'trivial', 'lint': 'trivial', 'typo_naming': 'trivial', 'type_annotation': 'local', 'signature': 'bounded', 'refactor_mechanical': 'bounded', 'bugfix_logic': 'local', 'bugfix_edgecase': 'local', 'error_handling': 'local', 'concurrency': 'bounded', 'security': 'bounded', 'performance': 'bounded', 'data_migration': 'broad', 'dependency': 'bounded', 'api_contract': 'bounded', 'config_build': 'local', 'test_fix': 'local', 'test_add': 'local', 'docs': 'trivial', 'i18n_localization': 'local', 'unknown': 'bounded'})
RISK_MIN_TIER: Final[Mapping[str, str | None]] = MappingProxyType({'standard': None, 'governance_critical': 'PREMIUM'})

