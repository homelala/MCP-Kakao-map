from fastmcp import FastMCP

mcp = FastMCP("KAKAO MAP")

# @mcp.resource()
# def get_location():

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')