from apps.enums import (
    AlignmentMethod,
    DistanceMethod,
    FitMethod,
    TreeType,
    SimilarityMethod,
    PreprocessingToggle,
    StatisticalTest,
    MantelTestMethod,
    convert_settings_to_codes,
)
from apps.utils.i18n import t
import pytest


pytestmark = pytest.mark.unit


# --- AlignmentMethod ---

def test_get_code_returns_expected_code():
    assert AlignmentMethod.get_code("MUSCLE") == "2"


def test_get_code_falls_back_to_original_value():
    assert AlignmentMethod.get_code("UNKNOWN") == "UNKNOWN"


def test_alignment_method_all_codes():
    assert AlignmentMethod.get_code("NoAlignment") == "0"
    assert AlignmentMethod.get_code("PairwiseAlign") == "1"
    assert AlignmentMethod.get_code("MUSCLE") == "2"
    assert AlignmentMethod.get_code("CLUSTALW") == "3"
    assert AlignmentMethod.get_code("MAFFT") == "4"


def test_alignment_method_choices_have_label_and_value():
    for choice in AlignmentMethod.choices():
        assert "label" in choice
        assert "value" in choice


# --- DistanceMethod ---

def test_distance_method_choices_have_label_and_value():
    for choice in DistanceMethod.choices():
        assert "label" in choice
        assert "value" in choice


def test_distance_method_all_codes():
    assert DistanceMethod.get_code("All") == "0"
    assert DistanceMethod.get_code("LeastSquare") == "1"
    assert DistanceMethod.get_code("RobinsonFoulds") == "2"
    assert DistanceMethod.get_code("Bipartition") == "3"


def test_distance_method_choices_labels_are_descriptive():
    labels = {c["value"]: c["label"] for c in DistanceMethod.choices()}
    assert "Bipartition" in labels["Bipartition"]
    assert "Robinson" in labels["RobinsonFoulds"]


# --- FitMethod ---

def test_fit_method_all_codes():
    assert FitMethod.get_code("WiderFit") == "1"
    assert FitMethod.get_code("NarrowFit") == "2"


def test_fit_method_choices_have_label_and_value():
    for choice in FitMethod.choices():
        assert "label" in choice
        assert "value" in choice


# --- TreeType ---

def test_tree_type_all_codes():
    assert TreeType.get_code("BioPython") == "1"
    assert TreeType.get_code("Fast Tree") == "2"


def test_tree_type_choices_have_label_and_value():
    for choice in TreeType.choices():
        assert "label" in choice
        assert "value" in choice


# --- SimilarityMethod ---

def test_similarity_method_all_codes():
    assert SimilarityMethod.get_code("Hamming") == "1"
    assert SimilarityMethod.get_code("Levenshtein") == "2"
    assert SimilarityMethod.get_code("DamerauLevenshtein") == "3"
    assert SimilarityMethod.get_code("Jaro") == "4"
    assert SimilarityMethod.get_code("JaroWinkler") == "5"
    assert SimilarityMethod.get_code("SmithWaterman") == "6"
    assert SimilarityMethod.get_code("Jaccard") == "7"
    assert SimilarityMethod.get_code("SorensenDice") == "8"


def test_similarity_method_choices_have_label_and_value():
    for choice in SimilarityMethod.choices():
        assert "label" in choice
        assert "value" in choice


# --- PreprocessingToggle ---

def test_preprocessing_toggle_all_codes():
    assert PreprocessingToggle.get_code("Disabled") == "0"
    assert PreprocessingToggle.get_code("Enabled") == "1"


def test_preprocessing_toggle_choices_have_label_and_value():
    for choice in PreprocessingToggle.choices():
        assert "label" in choice
        assert "value" in choice


# --- StatisticalTest ---

def test_statistical_test_all_codes():
    assert StatisticalTest.get_code("Both") == "0"
    assert StatisticalTest.get_code("MantelTest") == "1"
    assert StatisticalTest.get_code("Procrustes") == "2"
    assert StatisticalTest.get_code("None") == "3"


def test_statistical_test_choices_have_label_and_value():
    for choice in StatisticalTest.choices():
        assert "label" in choice
        assert "value" in choice


# --- MantelTestMethod ---

def test_mantel_test_method_all_codes():
    assert MantelTestMethod.get_code("Pearson") == "pearson"
    assert MantelTestMethod.get_code("Spearman") == "spearman"
    assert MantelTestMethod.get_code("KendallTau") == "kendalltau"


def test_mantel_test_method_choices_have_label_and_value():
    for choice in MantelTestMethod.choices():
        assert "label" in choice
        assert "value" in choice


# --- convert_settings_to_codes ---

def test_convert_settings_to_codes_maps_known_values():
    settings = {
        "alignment_method": "MUSCLE",
        "distance_method": "Bipartition",
        "fit_method": "NarrowFit",
        "unrelated": "keep-me",
    }

    converted = convert_settings_to_codes(settings)

    assert converted["alignment_method"] == "2"
    assert converted["distance_method"] == "3"
    assert converted["fit_method"] == "2"
    assert converted["unrelated"] == "keep-me"


def test_convert_settings_to_codes_maps_all_keys():
    settings = {
        "alignment_method": "CLUSTALW",
        "distance_method": "LeastSquare",
        "fit_method": "WiderFit",
        "tree_type": "BioPython",
        "method_similarity": "Jaccard",
        "preprocessing_genetic": "Enabled",
        "preprocessing_climatic": "Disabled",
        "statistical_test": "MantelTest",
        "mantel_test_method": "Spearman",
    }

    converted = convert_settings_to_codes(settings)

    assert converted["alignment_method"] == "3"
    assert converted["distance_method"] == "1"
    assert converted["fit_method"] == "1"
    assert converted["tree_type"] == "1"
    assert converted["method_similarity"] == "7"
    assert converted["preprocessing_genetic"] == "1"
    assert converted["preprocessing_climatic"] == "0"
    assert converted["statistical_test"] == "1"
    assert converted["mantel_test_method"] == "spearman"


def test_convert_settings_to_codes_unknown_value_kept_as_is():
    settings = {"alignment_method": "UNKNOWN_METHOD"}
    converted = convert_settings_to_codes(settings)
    assert converted["alignment_method"] == "UNKNOWN_METHOD"


def test_convert_settings_to_codes_does_not_mutate_input():
    settings = {"alignment_method": "MUSCLE"}
    original = settings.copy()
    convert_settings_to_codes(settings)
    assert settings == original


def test_convert_settings_to_codes_empty_dict():
    assert convert_settings_to_codes({}) == {}


# --- Language / locale tests ---
# Verify that locale strings for each enum option exist in both EN and FR
# and that the English locale matches the expected label.

def test_alignment_method_locale_en():
    assert t("setting.options.alignment.no-alignment", "en") == "No alignment"
    assert t("setting.options.alignment.pairwise-align", "en") == "Pairwise alignment"
    assert t("setting.options.alignment.muscle", "en") == "MUSCLE"
    assert t("setting.options.alignment.clustalw", "en") == "CLUSTALW"
    assert t("setting.options.alignment.mafft", "en") == "MAFFT"


def test_alignment_method_locale_fr():
    assert t("setting.options.alignment.no-alignment", "fr") == "Sans alignement"
    assert t("setting.options.alignment.pairwise-align", "fr") == "Alignement pair à pair"
    assert t("setting.options.alignment.muscle", "fr") == "MUSCLE"
    assert t("setting.options.alignment.clustalw", "fr") == "CLUSTALW"
    assert t("setting.options.alignment.mafft", "fr") == "MAFFT"


def test_distance_method_locale_en():
    assert t("setting.options.distance.all", "en") == "All distance methods"
    assert t("setting.options.distance.least-square", "en") == "Least Square"
    assert t("setting.options.distance.robinson-foulds", "en") == "Robinson-Foulds (RF)"
    assert t("setting.options.distance.bipartition", "en") == "Bipartition (Dendropy)"


def test_distance_method_locale_fr():
    assert t("setting.options.distance.all", "fr") == "Toutes les méthodes de distance"
    assert t("setting.options.distance.least-square", "fr") == "Moindres carrés"
    assert t("setting.options.distance.robinson-foulds", "fr") == "Robinson-Foulds (RF)"
    assert t("setting.options.distance.bipartition", "fr") == "Bipartition (Dendropy)"


def test_fit_method_locale_en():
    assert t("setting.options.fit.wider-fit", "en") == "Wider fit (pad with gaps)"
    assert t("setting.options.fit.narrow-fit", "en") == "Narrow fit (avoid extra gaps)"


def test_fit_method_locale_fr():
    assert t("setting.options.fit.wider-fit", "fr") == "Ajustement large (ajout de gaps)"
    assert t("setting.options.fit.narrow-fit", "fr") == "Ajustement étroit (évite les gaps supplémentaires)"


def test_tree_type_locale_en():
    assert t("setting.options.tree.biopython", "en") == "BioPython consensus tree"
    assert t("setting.options.tree.fast-tree", "en") == "FastTree application"


def test_tree_type_locale_fr():
    assert t("setting.options.tree.biopython", "fr") == "Arbre consensus BioPython"
    assert t("setting.options.tree.fast-tree", "fr") == "Application FastTree"


def test_similarity_method_locale_en():
    assert t("setting.options.similarity.hamming", "en") == "Hamming distance"
    assert t("setting.options.similarity.levenshtein", "en") == "Levenshtein distance"
    assert t("setting.options.similarity.damerau-levenshtein", "en") == "Damerau-Levenshtein distance"
    assert t("setting.options.similarity.jaro", "en") == "Jaro similarity"
    assert t("setting.options.similarity.jaro-winkler", "en") == "Jaro-Winkler similarity"
    assert t("setting.options.similarity.smith-waterman", "en") == "Smith-Waterman similarity"
    assert t("setting.options.similarity.jaccard", "en") == "Jaccard similarity"
    assert t("setting.options.similarity.sorensen-dice", "en") == "Sørensen-Dice similarity"


def test_similarity_method_locale_fr():
    assert t("setting.options.similarity.hamming", "fr") == "Distance de Hamming"
    assert t("setting.options.similarity.levenshtein", "fr") == "Distance de Levenshtein"
    assert t("setting.options.similarity.damerau-levenshtein", "fr") == "Distance de Damerau-Levenshtein"
    assert t("setting.options.similarity.jaro", "fr") == "Similarité de Jaro"
    assert t("setting.options.similarity.jaro-winkler", "fr") == "Similarité de Jaro-Winkler"
    assert t("setting.options.similarity.smith-waterman", "fr") == "Similarité de Smith-Waterman"
    assert t("setting.options.similarity.jaccard", "fr") == "Similarité de Jaccard"
    assert t("setting.options.similarity.sorensen-dice", "fr") == "Similarité de Sørensen-Dice"


def test_preprocessing_toggle_locale_en():
    assert t("setting.options.preprocessing.disabled", "en") == "Disabled"
    assert t("setting.options.preprocessing.enabled", "en") == "Enabled"


def test_preprocessing_toggle_locale_fr():
    assert t("setting.options.preprocessing.disabled", "fr") == "Désactivé"
    assert t("setting.options.preprocessing.enabled", "fr") == "Activé"


def test_statistical_test_locale_en():
    assert t("setting.options.statistical.both", "en") == "Both (Mantel + PROTEST)"
    assert t("setting.options.statistical.mantel", "en") == "Mantel test only"
    assert t("setting.options.statistical.procrustes", "en") == "PROTEST only"
    assert t("setting.options.statistical.none", "en") == "None"


def test_statistical_test_locale_fr():
    assert t("setting.options.statistical.both", "fr") == "Les deux (Mantel + PROTEST)"
    assert t("setting.options.statistical.mantel", "fr") == "Test de Mantel uniquement"
    assert t("setting.options.statistical.procrustes", "fr") == "PROTEST uniquement"
    assert t("setting.options.statistical.none", "fr") == "Aucun"


def test_mantel_test_method_locale_en():
    assert t("setting.options.mantel.pearson", "en") == "Pearson correlation"
    assert t("setting.options.mantel.spearman", "en") == "Spearman correlation"
    assert t("setting.options.mantel.kendall-tau", "en") == "Kendall Tau correlation"


def test_mantel_test_method_locale_fr():
    assert t("setting.options.mantel.pearson", "fr") == "Corrélation de Pearson"
    assert t("setting.options.mantel.spearman", "fr") == "Corrélation de Spearman"
    assert t("setting.options.mantel.kendall-tau", "fr") == "Corrélation de Kendall Tau"
