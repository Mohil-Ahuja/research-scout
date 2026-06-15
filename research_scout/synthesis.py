import json
from typing import Protocol

import httpx

from .models import Digest, Paper


class Synthesizer(Protocol):
    async def synthesize(self, query: str, papers: list[Paper]) -> Digest: ...


class GrokSynthesizer:
    def __init__(self, api_key: str, model: str = "grok-3-mini", client=None):
        self.api_key, self.model = api_key, model
        self.client = client

    async def synthesize(self, query: str, papers: list[Paper]) -> Digest:
        context = "\n\n".join(
            f"[{i}] {p.title}\nAuthors: {', '.join(p.authors)}\nAbstract: {p.abstract}\nURL: {p.url}"
            for i, p in enumerate(papers, 1)
        )
        prompt = f"""Research query: {query}
Using only the papers below, produce a JSON object with exactly these fields:
overview (string), key_findings (array of strings), themes (array of strings),
limitations (array of strings), paper_summaries (array of strings).
Do not invent findings not supported by the abstracts. Mention uncertainty.

Papers:
{context}"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "temperature": 0.2, "messages": [
            {"role": "system", "content": "You are a careful literature review assistant. Return JSON only."},
            {"role": "user", "content": prompt},
        ]}
        async with httpx.AsyncClient(timeout=60, transport=self.client) as client:
            response = await client.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        content = content.removeprefix("```json").removesuffix("```").strip()
        return Digest.model_validate(json.loads(content))


def render_markdown(query: str, papers: list[Paper], digest: Digest) -> str:
    lines = [f"# Research Scout Digest\n\n**Query:** {query}\n", "## Overview\n", digest.overview, ""]
    for heading, items in (("Key findings", digest.key_findings), ("Themes", digest.themes), ("Limitations", digest.limitations)):
        lines += [f"## {heading}\n"] + [f"- {item}" for item in items] + [""]
    lines += ["## Selected papers\n"]
    for paper, summary in zip(papers, digest.paper_summaries):
        score = f" — similarity {paper.similarity:.4f}" if paper.similarity is not None else ""
        lines += [f"### {paper.title}{score}", f"{summary}", f"[arXiv:{paper.arxiv_id}]({paper.url})", ""]
    return "\n".join(lines)

