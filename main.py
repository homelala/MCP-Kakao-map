import httpx
from fastmcp import FastMCP

from config import REST_API_KEY
from hosts.category import Category

mcp = FastMCP("KAKAO MAP MCP")

API_ENDPOINT = "https://dapi.kakao.com/v2/local"
api_headers = {
    "Authorization": f"KakaoAK {REST_API_KEY}"
}

@mcp.tool(name="search_location", description="search_location")
async def search_location(query:str, x,y,page=1, size=15, sort="accuracy"):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_ENDPOINT}/search/keyword.json",
            params={
                "query": query,
                "x":x,
                "y":y,
                "page": page,
                "size": size,
                "sort": sort,
            },
            headers=api_headers,
        )
        response.raise_for_status()  # Raise an error for bad responses
        return response.text

@mcp.tool(name="search_keyword", description="search_keyword")
async def search_location(category_name:str, x,y,radius=10, page=1, size=15, sort="accuracy"):
    async with httpx.AsyncClient() as client:
        category_code = Category.get_category_code(category_name)

        response = await client.get(
            f"{API_ENDPOINT}/search/category.json",
            params={
                "category_group_code": category_code,
                "x":x,
                "y":y,
                "radius":radius,
                "page": page,
                "size": size,
                "sort": sort,
            },
            headers=api_headers,
        )
        response.raise_for_status()  # Raise an error for bad responses
        return response.text


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()