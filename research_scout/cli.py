import asyncio

import typer

from .config import Settings
from .models import ResearchRequest
from .pipeline import ResearchScout

app = typer.Typer(add_completion=False, help="Retrieve and synthesize arXiv research.")


@app.command()
def research(query: str, max_results: int = 20, top_k: int = 5, json_output: bool = False):
    """Run a research query and print a digest."""
    result = asyncio.run(ResearchScout().research(ResearchRequest(query=query, max_results=max_results, top_k=top_k)))
    if json_output:
        typer.echo(result.model_dump_json(indent=2))
    else:
        typer.echo(result.markdown)

