from fastapi import APIRouter, HTTPException, Query, Body
from typing import Any
import requests
from pydantic import BaseModel

from .Crawler import crawl_site  # Ensure this is an async function
from routers.treestructuremanager import TreeStructureManager
from .state import tree_data, init_tree_manager
import asyncio
router = APIRouter()

@router.post("/run-crawler")
async def run_crawler(url: str = Query(..., description="URL to crawl"), depth: int = 1):
    try:
        crawled_data = await crawl_site(url, depth=depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")
    
    manager = init_tree_manager()
    for record in crawled_data:
        record_url = record.get('url')
        if record_url:
            manager.add_url(record_url)
    
    # Update the global tree_data
    from .state import tree_data  # already imported; tree_data can be a mutable variable
    tree_data.clear()
    tree_data.extend(manager.get_tree_nodes())
    return {"success": True, "tree": tree_data}

# --- HTTP Client Integration for Response Manager ---

class HttpRequest:
    def __init__(self, method: str, url: str, headers: dict, payload: Any):
        self.method = method
        self.url = url
        self.headers = headers
        self.payload = payload

class HttpResponse:
    def __init__(self, status_code: int, body: str, headers: dict):
        self.status_code = status_code
        self.body = body
        self.headers = headers

class RequestManager:
    def create_request(self, method: str, url: str, headers: dict, params: dict, payload: Any) -> HttpRequest:
        print("RequestManager: Creating request")
        print("  Method:", method)
        print("  URL:", url)
        print("  Headers:", headers)
        print("  Payload:", payload)
        return HttpRequest(method, url, headers, payload)

class ProxyServer:
    def forward_request(self, request: HttpRequest) -> None:
        print(f"[Proxy] Forwarding {request.method} request to {request.url}")
    def handle_forwarding_error(self, error: Exception) -> None:
        print(f"[Proxy] Error during request forwarding: {error}")

class HTTPClient:
    """
    HTTPClient: Responsible for sending HTTP requests and receiving responses.
    """
    def __init__(self, request_manager: RequestManager, proxy_server: ProxyServer = None):
        self.request_manager = request_manager
        self.proxy_server = proxy_server
        self.last_response: HttpResponse = None

    def send_request(self, url: str, data: Any, req_type: str, headers: dict) -> None:
        print("HTTPClient: Preparing to send request")
        print("  URL:", url)
        print("  Method:", req_type)
        print("  Headers:", headers)
        print("  Data:", data)
        # Create the HTTP request.
        request = self.request_manager.create_request(req_type, url, headers, params={}, payload=data)
        # Optionally forward the request.
        if self.proxy_server is not None:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                raise HTTPException(status_code=500, detail="Proxy forwarding failed")
        # Send the HTTP request.
        self.last_response = self._send_http(request)
    
    def receive_response(self) -> HttpResponse:
        return self.last_response

    def _send_http(self, request: HttpRequest) -> HttpResponse:
        try:
            if request.method.upper() == "GET":
                response = requests.get(request.url, headers=request.headers, params=request.payload)
            else:
                response = requests.request(request.method, request.url, headers=request.headers, json=request.payload)
            print("HTTPClient: Received response")
            print("  Status:", response.status_code)
            print("  Response Headers:", dict(response.headers))
            print("  Response Body:", response.text)
            return HttpResponse(response.status_code, response.text, dict(response.headers))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HTTP request failed: {e}")

# --- Pydantic model for the client request ---
class ClientRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict = {}
    parameters: dict = {}   # For GET query parameters.
    payload: Any = None      # For POST/PUT/PATCH payload.

@router.post("/send")
async def send_client_request(client_request: ClientRequest):
    print("Endpoint /tools/send received client_request:")
    print(client_request.dict())
    
    req_manager = RequestManager()
    proxy_server = ProxyServer()  # Set to None if proxy is not needed.
    client = HTTPClient(req_manager, proxy_server)
    
    # For GET requests, use the provided query parameters.
    if client_request.method.upper() == "GET":
        data = client_request.parameters
    else:
        data = client_request.payload
    
    try:
        client.send_request(client_request.url, data, client_request.method, client_request.headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    response = client.receive_response()
    print("Endpoint /tools/send sending final response:")
    print("  Status:", response.status_code)
    print("  Headers:", response.headers)
    print("  Body:", response.body)
    
    # Return the formatted response.
    return {
        "status": response.status_code,
        "headers": response.headers,
        "body": response.body
    }
