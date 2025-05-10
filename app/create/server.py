from app.utils.tools import (
    list_attractions_by_region, 
    search_attractions_by_keyword, 
    find_nearby_attractions
)

from mcp.server.fastmcp import FastMCP

MCP = FastMCP(name="create_itinerary_mcp_server", port=8070, host="localhost")
MCP.add_tool(list_attractions_by_region)
# MCP.add_tool(search_attractions_by_keyword)
MCP.add_tool(find_nearby_attractions)

if __name__ == "__main__":
    MCP.run(transport="sse")