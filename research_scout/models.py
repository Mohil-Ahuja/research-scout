from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    max_results: int = Field(default=20, ge=1, le=100)
    top_k: int = Field(default=5, ge=1, le=20)


class Paper(BaseModel):
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str] = []
    published: str | None = None
    updated: str | None = None
    categories: list[str] = []
    url: HttpUrl
    similarity: float | None = None


class Digest(BaseModel):
    overview: str
    key_findings: list[str]
    themes: list[str]
    limitations: list[str]
    paper_summaries: list[str]


class ResearchResponse(BaseModel):
    query: str
    retrieved_count: int
    papers: list[Paper]
    digest: Digest
    markdown: str

