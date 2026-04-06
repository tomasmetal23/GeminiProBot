"""
search.py — Brave Search API wrapper (async).
Get your free API key at: https://brave.com/search/api/
Free tier: 2000 queries/month.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


async def brave_search(query: str, max_results: int = 4) -> str:
    """
    Search using Brave Search API.
    Returns a formatted string with results ready to inject as context.
    """
    if not BRAVE_API_KEY:
        return "⚠️ BRAVE_API_KEY no configurada. Añádela al .env para usar búsqueda web."

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }
    params = {
        "q": query,
        "count": max_results,
        "search_lang": "es",
        "country": "ES",
        "text_decorations": False,
        "spellcheck": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(BRAVE_SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("web", {}).get("results", [])
        if not results:
            return f"No se encontraron resultados para: {query}"

        lines = [f"🔍 Resultados de búsqueda para: **{query}**\n"]
        for i, r in enumerate(results[:max_results], 1):
            title = r.get("title", "Sin título")
            url = r.get("url", "")
            desc = r.get("description", "Sin descripción")
            lines.append(f"{i}. **{title}**\n   {desc}\n   🔗 {url}")

        return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        logger.error("Brave Search HTTP error: %s", e)
        if e.response.status_code == 401:
            return "❌ BRAVE_API_KEY inválida. Revisa tu clave en search.brave.com."
        return f"❌ Error en búsqueda ({e.response.status_code}): {e}"
    except Exception as e:
        logger.error("Brave Search error: %s", e)
        return f"❌ Error al buscar: {e}"
