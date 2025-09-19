from .annotate import annotate_citations
from .clean import clean_text
from .find import get_citations
from .resolve import resolve_citations

# Import extended functionality
from . import models_extended
from . import tokenizers_extended
from .models_extended import (
    BaseCitation,
    ConstitutionCitation,
    RegulationCitation,
    CourtRuleCitation,
    LegislativeBillCitation,
    SessionLawCitation,
    JournalArticleCitation,
    ScientificIdentifierCitation,
    AttorneyGeneralCitation,
)
from .tokenizers_extended import (
    StateConstitutionTokenizer,
    JournalArticleTokenizer,
    FederalLegislationTokenizer,
    ScientificIdentifierTokenizer,
    ExtendedCitationTokenizer,
    default_extended_tokenizer,
    AttorneyGeneralOpinionsTokenizer,
)

__all__ = [
    "annotate_citations",
    "get_citations",
    "clean_text",
    "resolve_citations",
    # Extended functionality
    "models_extended",
    "tokenizers_extended",
    "BaseCitation",
    "ConstitutionCitation",
    "RegulationCitation",
    "CourtRuleCitation",
    "LegislativeBillCitation",
    "SessionLawCitation",
    "JournalArticleCitation",
    "ScientificIdentifierCitation",
    "StateConstitutionTokenizer",
    "JournalArticleTokenizer",
    "FederalLegislationTokenizer",
    "ScientificIdentifierTokenizer",
    "ExtendedCitationTokenizer",
    "default_extended_tokenizer",
]

# No need to create API documentation for these internal helper functions
__pdoc__ = {
    "annotate.SpanUpdater": False,
    "helpers": False,
    "regexes": False,
    "test_factories": False,
    "utils": False,
}
