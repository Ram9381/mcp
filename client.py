import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MCP_SERVER_URL = "http://localhost:8000/mcp/"

def call_ollama(prompt, model="llama3"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"]

def call_mcp(tool_name, arguments):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    response = requests.post(MCP_SERVER_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Example: ask Ollama to generate a tool call for weather in London
    user_question = "What's the weather in London?"
    system_prompt = (
        "You are an AI assistant. When the user asks a question, respond with a JSON object in this format:\n"
        "{\n"
        "  \"action\": \"use_tool\",\n"
        "  \"tool\": \"tool_name\",\n"
        "  \"parameters\": {\"param1\": \"value1\", ...}\n"
        "}\n"
        "If the user's request doesn't require a tool, just answer normally.\n"
        f"User: {user_question}"
    )
    ollama_response = call_ollama(system_prompt)
    print("[Ollama response]:", ollama_response)

    # Try to parse Ollama's response as a tool call
    import json
    try:
        tool_call = json.loads(ollama_response)
        if tool_call.get("action") == "use_tool":
            tool_name = tool_call["tool"]
            arguments = tool_call["parameters"]
            mcp_result = call_mcp(tool_name, arguments)
            print("[MCP result]:", json.dumps(mcp_result, indent=2))
        else:
            print("[Direct answer]:", ollama_response)
    except Exception as e:
        print("[Error parsing Ollama response]:", e)
        print("[Raw Ollama response]:", ollama_response)
