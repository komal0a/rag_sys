import pytest

from app.services.embeddings import OllamaEmbeddingProvider


class MockResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.ok = status_code < 400
        self.text = str(payload)

    def json(self):
        return self._payload


def test_ollama_embedding_provider_uses_batch_api(monkeypatch):
    calls = []

    def post(url, json, timeout):
        calls.append((url, json, timeout))
        return MockResponse(200, {"embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]})

    monkeypatch.setattr("app.services.embeddings.requests.post", post)
    provider = OllamaEmbeddingProvider(base_url="http://ollama:11434", model="nomic-embed-text", expected_dim=3)
    assert provider.embed_texts(["first", "second"]) == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    assert calls == [("http://ollama:11434/api/embed", {"model": "nomic-embed-text", "input": ["first", "second"]}, 120)]


def test_ollama_embedding_provider_fails_on_dimension_mismatch(monkeypatch):
    monkeypatch.setattr("app.services.embeddings.requests.post", lambda *args, **kwargs: MockResponse(200, {"embeddings": [[0.1, 0.2]]}))
    with pytest.raises(RuntimeError, match="returned 2 dimensions"):
        OllamaEmbeddingProvider(expected_dim=3).embed_texts(["text"])


def test_ollama_embedding_provider_reports_missing_model(monkeypatch):
    monkeypatch.setattr("app.services.embeddings.requests.post", lambda *args, **kwargs: MockResponse(404, {"error": "model not found"}))
    with pytest.raises(RuntimeError, match="ollama pull nomic-embed-text"):
        OllamaEmbeddingProvider().embed_texts(["text"])
