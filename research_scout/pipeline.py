from .arxiv import ArxivClient
from .config import Settings
from .models import Digest, ResearchRequest, ResearchResponse
from .ranking import SentenceTransformerEmbedder, rank_papers
from .synthesis import GrokSynthesizer, render_markdown


class ResearchScout:
    def __init__(self, arxiv=None, embedder=None, synthesizer=None, settings=None):
        self.settings = settings or Settings()
        self.arxiv = arxiv or ArxivClient(self.settings.arxiv_timeout_seconds, self.settings.arxiv_retries)
        self.embedder = embedder or SentenceTransformerEmbedder(self.settings.embedding_model)
        self.synthesizer = synthesizer or self._default_synthesizer()

    def _default_synthesizer(self):
        if not self.settings.xai_api_key:
            raise ValueError("XAI_API_KEY is required for synthesis")
        return GrokSynthesizer(self.settings.xai_api_key, self.settings.grok_model)

    async def research(self, request: ResearchRequest) -> ResearchResponse:
        papers = await self.arxiv.search(request.query, request.max_results)
        selected = rank_papers(request.query, papers, self.embedder, request.top_k)
        digest = await self.synthesizer.synthesize(request.query, selected) if selected else Digest(
            overview="No papers matched the query.", key_findings=[], themes=[], limitations=[], paper_summaries=[])
        return ResearchResponse(query=request.query, retrieved_count=len(papers), papers=selected,
                                digest=digest, markdown=render_markdown(request.query, selected, digest))

