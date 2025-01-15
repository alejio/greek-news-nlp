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

@pytest.mark.parametrize("response_content,expected", [
    ("θετική\nΕξήγηση", ("θετική", "Εξήγηση")),
    ("αρνητική\nΕξήγηση", ("αρνητική", "Εξήγηση")),
    ("ουδέτερη\nΕξήγηση", ("ουδέτερη", "Εξήγηση")),
    ("invalid\nΕξήγηση", ("ουδέτερη", "Εξήγηση")),  # Test invalid stance
])
def test_classify_article_variations(mock_openai_client, response_content, expected):
    mock_openai_client.chat.completions.create.return_value.choices[0].message.content = response_content
    
    stance, justification = classify_article_with_explanation(
        mock_openai_client,
        "Test article content",
        "Test Club"
    )
    
    assert (stance, justification) == expected 