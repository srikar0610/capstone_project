"""Search the supplied documentation and return passages that can be cited.

Requirement FR-RET-1. A score under the relevance threshold returns nothing.
Returning nothing is preferable to returning a plausible but unrelated article.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_passages(content: str, size: int = 800, overlap: int = 120) -> list[str]:
    """Split on character windows. Each passage is an exact slice of the article."""
    text = content.replace("\r\n", "\n").strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    passages: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        passages.append(text[start:end])
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return passages


class Retriever:
    def __init__(self, documentation_path: Path, top_k: int, threshold: float) -> None:
        self.top_k = top_k
        self.threshold = threshold
        self.documentation_path = documentation_path
        if not documentation_path.exists():
            raise FileNotFoundError(
                f"Documentation corpus was not found at {documentation_path}."
            )
        documents = json.loads(documentation_path.read_text(encoding="utf-8"))
        self.chunks: list[dict] = []
        for document in documents:
            doc_id = document["doc_id"]
            title = document.get("title", doc_id)
            content = document.get("content", "")
            for index, passage in enumerate(split_passages(content)):
                self.chunks.append(
                    {
                        "passage_id": f"{doc_id}#c{index}",
                        "doc_id": doc_id,
                        "title": title,
                        "text": passage,
                    }
                )
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.matrix = self.vectorizer.fit_transform(chunk["text"] for chunk in self.chunks)

    def search(self, query: str) -> list[dict]:
        cleaned = (query or "").strip()
        if len(cleaned) < 3 or not self.chunks:
            return []
        query_vector = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        if scores.size == 0:
            return []
        # One passage per article, then keep the strongest articles. This stops
        # three windows of the same page crowding out a second source.
        best_by_doc: dict[str, int] = {}
        for index in np.argsort(scores)[::-1]:
            doc_id = self.chunks[int(index)]["doc_id"]
            if doc_id not in best_by_doc:
                best_by_doc[doc_id] = int(index)
            if len(best_by_doc) >= self.top_k:
                break
        hits: list[dict] = []
        for index in best_by_doc.values():
            score = float(scores[index])
            if score < self.threshold:
                continue
            chunk = self.chunks[index]
            hits.append(
                {
                    "passage_id": chunk["passage_id"],
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "text": chunk["text"],
                    "score": round(score, 4),
                }
            )
        hits.sort(key=lambda item: item["score"], reverse=True)
        return hits
