from src.services.llm_client import normalize_base_url


def test_normalize_base_url() -> None:
    assert normalize_base_url("https://host") == "https://host/v1"
    assert normalize_base_url("https://host/v1") == "https://host/v1"
