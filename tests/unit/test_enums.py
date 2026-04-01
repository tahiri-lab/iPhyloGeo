from apps.enums import AlignmentMethod, DistanceMethod, convert_settings_to_codes
import pytest


pytestmark = pytest.mark.unit


def test_get_code_returns_expected_code():
    assert AlignmentMethod.get_code("MUSCLE") == "2"


def test_get_code_falls_back_to_original_value():
    assert AlignmentMethod.get_code("UNKNOWN") == "UNKNOWN"


def test_distance_method_choices_have_label_and_value():
    first_choice = DistanceMethod.choices()[0]
    assert "label" in first_choice
    assert "value" in first_choice


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
