import asyncio

import numpy as np

from research_scout.models import Digest, Paper, ResearchRequest
from research_scout.pipeline import ResearchScout


class FakeArxiv:
    async def search(self, query, max_results):
        return [Paper(arxiv_id="1", title="Relevant", abstract="query topic", url="https://arxiv.org/abs/1"),
                Paper(arxiv_id="2", title="Other", abstract="different", url="https://arxiv.org/abs/2")]


class FakeEmbedder:
    def encode(self, texts):
        return np.array([[1, 0], [1, 0], [0, 1]])


class FakeSynth:
    async def synthesize(self, query, papers):
        return Digest(overview="ok", key_findings=["finding"], themes=[], limitations=[], paper_summaries=["summary"])


def test_pipeline_reranks_and_renders():
    result = asyncio.run(ResearchScout(FakeArxiv(), FakeEmbedder(), FakeSynth()).research(
        ResearchRequest(query="query topic", top_k=1)))
    assert result.retrieved_count == 2
    assert result.papers[0].arxiv_id == "1"
    assert "Relevant" in result.markdown
