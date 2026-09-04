import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("http://localhost:8008/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call execute_method to get customers
            # arguments should be a dict
            arguments = {
                "model": "res.partner",
                "method": "search_read",
                "args_json": "[[['customer_rank', '>', 0]]]",
                "kwargs_json": "{\"fields\": [\"name\", \"email\"], \"limit\": 5}"
            }
            
            print("Calling execute_method for customers...")
            result = await session.call_tool("execute_method", arguments)
            
            # result is a CallToolResult
            for content in result.content:
                if content.type == "text":
                    print("Result:")
                    print(content.text)

if __name__ == "__main__":
    asyncio.run(main())
