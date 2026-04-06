"""
search.py — DuckDuckGo search wrapper (async, no API key needed).
Uses the duckduckgo-search library which is free and doesn't require registration.
Note: may get rate-limited with very heavy usage, but fine for personal bots.
"""
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


async def web_search(query: str, max_results: int = 4) -> str:
    """
    Search using DuckDuckGo (no API key required).
    Returns a formatted string with results ready to inject as LLM context.
    Runs the blocking DDGS call in a thread to not block the async event loop.
    """
    import asyncio

    def _search() -> list[dict]:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))

    try:
        results = await asyncio.to_thread(_search)

        if not results:
            return f"No se encontraron resultados para: {query}"

        lines = [f"🔍 Resultados de búsqueda para: **{query}**\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "Sin título")
            url = r.get("href", "")
            desc = r.get("body", "Sin descripción")
            lines.append(f"{i}. **{title}**\n   {desc}\n   🔗 {url}")

        return "\n".join(lines)

    except Exception as e:
        logger.error("DuckDuckGo search error: %s", e)
        return f"❌ Error al buscar en DuckDuckGo: {e}"
