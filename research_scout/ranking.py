from typing import Protocol

from .models import Paper


class Embedder(Protocol):
    def encode(self, texts: list[str]): ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]):
        return self.model.encode(texts, normalize_embeddings=True)


def rank_papers(query: str, papers: list[Paper], embedder: Embedder, top_k: int) -> list[Paper]:
    if not papers:
        return []
    vectors = embedder.encode([query] + [f"{p.title}\n{p.abstract}" for p in papers])
    query_vector = vectors[0]
    scored = []
    for paper, vector in zip(papers, vectors[1:]):
        score = float(sum(a * b for a, b in zip(query_vector, vector)))
        scored.append(paper.model_copy(update={"similarity": round(score, 6)}))
    return sorted(scored, key=lambda p: p.similarity or 0, reverse=True)[:top_k]

