from duckduckgo_search import DDGS

def search_web_duckduckgo(query: str, max_results: int = 3) -> str:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title")
                href = r.get("href")
                body = r.get("body")
                results.append(f"- {title}\n{href}\n{body}\n")
        return "\n".join(results) if results else "No relevant results found."
    except Exception as e:
        return f"Error during DuckDuckGo search: {str(e)}"
