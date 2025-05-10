from app.utils.tools import (
    list_attractions_by_region, 
    search_attractions_by_keyword, 
)

from mcp.server.fastmcp import FastMCP

MCP = FastMCP(name="triplet_mcp_server", port=8071, host="localhost")
MCP.add_tool(list_attractions_by_region)
MCP.add_tool(search_attractions_by_keyword)


if __name__ == "__main__":
    MCP.run(transport="sse")