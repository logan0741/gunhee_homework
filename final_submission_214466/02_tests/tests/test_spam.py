from app.spam import check_spam, check_spam_keyword, get_model_version


def test_check_spam_returns_tuple():
    label, score = check_spam("hello world")
    assert isinstance(label, str)
    assert isinstance(score, float)
    assert label in ("ham", "spam")
    assert 0.0 <= score <= 1.0


def test_check_spam_ham():
    label, _ = check_spam("let's grab coffee tomorrow morning")
    assert label == "ham"


def test_check_spam_spam():
    label, score = check_spam("free prize click win money bonus")
    assert label == "spam"
    assert score > 0.0


def test_check_spam_empty():
    label, score = check_spam("")
    assert label == "ham"
    assert score == 0.0


def test_keyword_baseline():
    assert check_spam_keyword("hello")[0] == "ham"
    assert check_spam_keyword("free prize click win money")[0] == "spam"


def test_model_version_string():
    version = get_model_version()
    assert version in ("keyword-v1", "ml-v2")
