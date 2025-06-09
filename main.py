import httpx
from fastmcp import FastMCP

from config import REST_API_KEY

mcp = FastMCP("KAKAO MAP MCP")

API_ENDPOINT = "https://dapi.kakao.com/v2"
api_headers = {
    "Authorization": f"KakaoAK {REST_API_KEY}"
}

@mcp.tool(name="search location", description="search location")
async def search_location(query:str, page=1, size=15, sort="accuracy"):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_ENDPOINT}/search/keyword",
            params={
                "query": query,
                "page":page,
                "size":size,
                "sort":sort,
            },
            headers=api_headers,
        )
        response.raise_for_status()  # Raise an error for bad responses
        return response.text

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')