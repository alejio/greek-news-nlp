from datetime import datetime

from core.db.models import Article, Blogger, Category, StancePrediction


def test_blogger_creation(test_db):
    blogger = Blogger(name="Test Blogger", profile_url="https://example.com/blogger")
    test_db.add(blogger)
    test_db.commit()

    assert blogger.id is not None
    assert blogger.name == "Test Blogger"
    assert blogger.profile_url == "https://example.com/blogger"


def test_article_with_categories(test_db):
    blogger = Blogger(name="Test Blogger", profile_url="https://example.com/blogger")
    category = Category(name="Sports")

    article = Article(
        blogger=blogger,
        title="Test Article",
        content="Test content",
        article_url="https://example.com/article",
        published_date=datetime.utcnow(),
    )
    article.categories.append(category)

    test_db.add(article)
    test_db.commit()

    assert len(article.categories) == 1
    assert article.categories[0].name == "Sports"
    assert article.blogger.name == "Test Blogger"


def test_stance_prediction(test_db):
    article = Article(
        title="Test Article",
        content="Test content",
        article_url="https://example.com/article",
    )
    test_db.add(article)

    prediction = StancePrediction(
        article=article,
        target="Test Club",
        target_type="club",
        stance="θετική",
        justification="Test justification",
    )
    test_db.add(prediction)
    test_db.commit()

    assert prediction.article_id == article.id
    assert prediction.stance == "θετική"
    assert prediction.target == "Test Club"
    assert prediction.target_type == "club"
