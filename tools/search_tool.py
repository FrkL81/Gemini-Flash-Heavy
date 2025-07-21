from .base_tool import BaseTool
from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import json

class SearchTool(BaseTool):
    def __init__(self, config: dict):
        self.config = config
    
    @property
    def name(self) -> str:
        return "search_web"
    
    @property
    def description(self) -> str:
        return "Search the web using DuckDuckGo for current information"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find information on the web"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (default: 5)"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, max_results: int = 5) -> list:
        """Search the web using DuckDuckGo and fetch page content"""
        try:
            # Use ddgs library with proper error handling
            ddgs = DDGS()
            
            # Ensure max_results is an integer and within reasonable bounds
            max_results = int(max_results) if max_results else 5
            max_results = min(max_results, 10)  # Limit to prevent overload
            
            # Get search results
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return [{"error": "No search results found"}]
            
            simplified_results = []
            
            for i, result in enumerate(results):
                try:
                    # Validate result structure
                    if not isinstance(result, dict):
                        continue
                    
                    title = result.get('title', f'Result {i+1}')
                    url = result.get('href', '')
                    snippet = result.get('body', '')
                    
                    # Try to fetch content with better error handling
                    content = "Content not available"
                    try:
                        if url:
                            response = requests.get(
                                url, 
                                headers={'User-Agent': self.config.get('search', {}).get('user_agent', 'Mozilla/5.0')},
                                timeout=5  # Reduced timeout
                            )
                            response.raise_for_status()
                            
                            # Parse HTML with BeautifulSoup
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Remove script and style elements
                            for script in soup(["script", "style"]):
                                script.decompose()
                            
                            # Get text content
                            text = soup.get_text()
                            # Clean up whitespace
                            text = ' '.join(text.split())
                            
                            # Limit content length
                            content = text[:800] + "..." if len(text) > 800 else text
                    
                    except Exception as fetch_error:
                        content = f"Could not fetch content: {str(fetch_error)}"
                    
                    simplified_results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "content": content
                    })
                
                except Exception as result_error:
                    # Skip problematic results but continue processing
                    simplified_results.append({
                        "title": f"Result {i+1} (Error)",
                        "url": "",
                        "snippet": f"Error processing result: {str(result_error)}",
                        "content": "Content not available due to processing error"
                    })
            
            return simplified_results if simplified_results else [{"error": "No valid results could be processed"}]
        
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]