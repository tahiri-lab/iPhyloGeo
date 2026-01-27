"""
Enums for genetic pipeline settings.
These are used in settings.py, getStarted.py, and stored in the database.
Each enum has a 'value' (readable name for DB) and 'code' (numeric code for aphylogeo).
"""
from enum import Enum


class BaseEnum(str, Enum):
    """Base class for enums with code support."""
    
    def __new__(cls, value: str, code: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.code = code
        return obj
    
    @classmethod
    def choices(cls):
        """Return list of choices for Dash dropdown."""
        return [{"label": e.value, "value": e.value} for e in cls]
    
    @classmethod
    def get_code(cls, value: str) -> str:
        """Get the numeric code for a given value."""
        for e in cls:
            if e.value == value:
                return e.code
        return value  # fallback


class AlignmentMethod(BaseEnum):
    """Methods available for sequence alignment."""
    NO_ALIGNMENT = ("NoAlignment", "0")
    PAIRWISE_ALIGNER = ("PairwiseAligner", "1")
    MUSCLE = ("MUSCLE", "2")
    CLUSTALW = ("CLUSTALW", "3")
    MAFFT = ("MAFFT", "4")


class DistanceMethod(BaseEnum):
    """Methods available for tree distance calculation."""
    ALL = ("All", "0")
    LEAST_SQUARE = ("LeastSquare", "1")
    ROBINSON_FOULDS = ("RobinsonFoulds", "2")
    BIPARTITION = ("Bipartition", "3")

    @classmethod
    def choices(cls):
        """Return list of choices for Dash dropdown with descriptive labels."""
        labels = {
            "All": "All distance method",
            "LeastSquare": "Least Square",
            "RobinsonFoulds": "Robinson-Foulds (RF)",
            "Bipartition": "Bipartition (Dendropy)",
        }
        return [{"label": labels.get(e.value, e.value), "value": e.value} for e in cls]


class FitMethod(BaseEnum):
    """Methods available for alignment fitting."""
    WIDER_FIT = ("WiderFit", "1")
    NARROW_FIT = ("NarrowFit", "2")

    @classmethod
    def choices(cls):
        """Return list of choices for Dash dropdown with descriptive labels."""
        labels = {
            "WiderFit": "Wider Fit by elongating with Gap (starAlignment)",
            "NarrowFit": "Narrow-fit prevent elongation with gap when possible",
        }
        return [{"label": labels.get(e.value, e.value), "value": e.value} for e in cls]


class TreeType(BaseEnum):
    """Types of phylogenetic tree construction."""
    BIOPYTHON = ("BioPython", "1")
    FASTTREE = ("FastTree", "2")

    @classmethod
    def choices(cls):
        """Return list of choices for Dash dropdown with descriptive labels."""
        labels = {
            "BioPython": "BioPython consensus tree",
            "FastTree": "FastTree application",
        }
        return [{"label": labels.get(e.value, e.value), "value": e.value} for e in cls]


class SimilarityMethod(BaseEnum):
    """Methods available for sequence similarity calculation."""
    HAMMING = ("Hamming", "1")
    LEVENSHTEIN = ("Levenshtein", "2")
    DAMERAU_LEVENSHTEIN = ("DamerauLevenshtein", "3")
    JARO = ("Jaro", "4")
    JARO_WINKLER = ("JaroWinkler", "5")
    SMITH_WATERMAN = ("SmithWaterman", "6")
    JACCARD = ("Jaccard", "7")
    SORENSEN_DICE = ("SorensenDice", "8")

    @classmethod
    def choices(cls):
        """Return list of choices for Dash dropdown with descriptive labels."""
        labels = {
            "Hamming": "Hamming distance",
            "Levenshtein": "Levenshtein distance",
            "DamerauLevenshtein": "Damerau-Levenshtein distance",
            "Jaro": "Jaro similarity",
            "JaroWinkler": "Jaro-Winkler similarity",
            "SmithWaterman": "Smith-Waterman similarity",
            "Jaccard": "Jaccard similarity",
            "SorensenDice": "Sørensen-Dice similarity",
        }
        return [{"label": labels.get(e.value, e.value), "value": e.value} for e in cls]


def convert_settings_to_codes(settings: dict) -> dict:
    """
    Convert readable enum values to numeric codes for aphylogeo.
    
    Args:
        settings: Dict with readable values like {"alignment_method": "PairwiseAligner"}
    
    Returns:
        Dict with numeric codes like {"alignment_method": "1"}
    """
    mapping = {
        "alignment_method": AlignmentMethod,
        "distance_method": DistanceMethod,
        "fit_method": FitMethod,
        "tree_type": TreeType,
        "method_similarity": SimilarityMethod,
    }
    
    result = settings.copy()
    for key, enum_class in mapping.items():
        if key in result:
            result[key] = enum_class.get_code(result[key])
    
    return result
