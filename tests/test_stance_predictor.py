import pytest
from unittest.mock import Mock, patch
from data_collection.nlp.stance_predictor import classify_article_with_explanation

@pytest.fixture
def mock_openai_client():
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="θετική\nΘετική αναφορά στην ομάδα"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client

def test_classify_article_positive(mock_openai_client):
    article_text = "Η ομάδα έπαιξε εξαιρετικά και κέρδισε δίκαια."
    stance, justification = classify_article_with_explanation(
        mock_openai_client,
        article_text,
        "Ολυμπιακός"
    )
    
    assert stance == "θετική"
    assert justification == "Θετική αναφορά στην ομάδα"
    assert mock_openai_client.chat.completions.create.called

@pytest.mark.parametrize("target_type,article_text,expected_stance", [
    ("club", "Η ομάδα έπαιξε εξαιρετικά.", "θετική"),
    ("referee", "Ο διαιτητής έκανε σοβαρά λάθη.", "αρνητική"),
    ("referee", "Ο διαιτητής διηύθυνε σωστά τον αγώνα.", "θετική"),
])
def test_classify_article_variations(mock_openai_client, target_type, article_text, expected_stance):
    mock_openai_client.chat.completions.create.return_value.choices[0].message.content = f"{expected_stance}\nTest explanation"
    
    stance, justification = classify_article_with_explanation(
        mock_openai_client,
        article_text,
        "Test Target",
        target_type
    )
    
    assert stance == expected_stance
    assert justification == "Test explanation" 