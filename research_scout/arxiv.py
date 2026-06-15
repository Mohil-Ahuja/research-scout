import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

import httpx

from .models import Paper

ATOM = "http://www.w3.org/2005/Atom"
NS = {"a": ATOM}


class ArxivError(RuntimeError):
    pass


class ArxivClient:
    def __init__(self, timeout: float = 20.0, retries: int = 2, transport=None):
        self.timeout = timeout
        self.retries = retries
        self.transport = transport

    async def search(self, query: str, max_results: int = 20) -> list[Paper]:
        url = (
            "https://export.arxiv.org/api/query?search_query=all:%s&start=0&max_results=%d"
            % (quote_plus(query), max_results)
        )
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                return self._parse(response.text)
            except (httpx.HTTPError, ET.ParseError) as exc:
                last_error = exc
                if attempt < self.retries:
                    await asyncio.sleep(0.25 * (attempt + 1))
        raise ArxivError(f"Unable to retrieve arXiv papers: {last_error}")

    @staticmethod
    def _parse(xml: str) -> list[Paper]:
        root = ET.fromstring(xml)
        papers = []
        seen = set()
        for entry in root.findall("a:entry", NS):
            raw_id = (entry.findtext("a:id", "", NS)).strip()
            match = re.search(r"arxiv.org/abs/(.+)$", raw_id)
            arxiv_id = match.group(1) if match else raw_id.rsplit("/", 1)[-1]
            arxiv_id = arxiv_id.removesuffix(".pdf")
            if not arxiv_id or arxiv_id in seen:
                continue
            seen.add(arxiv_id)
            title = " ".join((entry.findtext("a:title", "", NS)).split())
            abstract = " ".join((entry.findtext("a:summary", "", NS)).split())
            authors = [a.findtext("a:name", "", NS).strip() for a in entry.findall("a:author", NS)]
            categories = [c.attrib.get("term", "") for c in entry.findall("a:category", NS)]
            papers.append(Paper(
                arxiv_id=arxiv_id, title=title, abstract=abstract, authors=authors,
                published=entry.findtext("a:published", None, NS),
                updated=entry.findtext("a:updated", None, NS), categories=categories,
                url=f"https://arxiv.org/abs/{arxiv_id}",
            ))
        return papers

