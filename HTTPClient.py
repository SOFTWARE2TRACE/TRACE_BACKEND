import requests
from typing import Any, Dict, Optional

# Update HttpResponse to include headers.
class HttpRequest:
    def __init__(self, method: str, url: str, headers: Dict[str, str], payload: Any):
        self.method = method
        self.url = url
        self.headers = headers
        self.payload = payload

class HttpResponse:
    def __init__(self, status_code: int, body: str, headers: Dict[str, str]):
        self.status_code = status_code
        self.body = body
        self.headers = headers

class RequestManager:
    def create_request(self, method: str, url: str, headers: Dict[str, str],
                       params: Dict[str, str], payload: Any) -> HttpRequest:
        # Here you could merge parameters into the payload if needed.
        # For GET requests, `params` can be used instead of payload.
        # For simplicity, we'll assume payload holds all necessary data.
        return HttpRequest(method, url, headers, payload)

class ProxyServer:
    def forward_request(self, request: HttpRequest) -> None:
        print(f"[Proxy] Forwarding {request.method} request to {request.url}")

    def handle_forwarding_error(self, error: Exception) -> None:
        print(f"[Proxy] Error during request forwarding: {error}")

class HTTPClient:
    """
    HTTPClient: Responsible for sending HTTP requests and receiving responses.
    
    Process Pipeline:
      1. Request Manager crafts a request (e.g., a RequestModel instance).
      2. HTTPClient accepts that request via send_request_from_model(),
         sends it to the target server, and receives the response.
      3. The client then passes the response to the response manager.
    """
    
    def __init__(self, request_manager: RequestManager, proxy_server: Optional[ProxyServer] = None):
        self.request_manager = request_manager
        self.proxy_server = proxy_server
        self.last_response: Optional[HttpResponse] = None

    def send_request(self, url: str, data: Any, req_type: str, headers: Dict[str, str]) -> None:
        # Original method that constructs the request using primitive parameters.
        request = self.request_manager.create_request(req_type, url, headers, params={}, payload=data)
        
        if self.proxy_server is not None:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                return
        
        self.last_response = self._send_http(request)
    
    def send_request_from_model(self, request_model: 'RequestModel') -> None:
        """
        Accepts a request crafted by the request manager (i.e. a RequestModel)
        and sends it using the HTTPClient.
        
        Assumes that the RequestModel has at least the following fields:
          - url: str
          - method: str
          - headers: dict
          - parameters: dict (for query parameters, if any)
          - payload: any (body for POST/PUT, etc.)
        """
        request = self.request_manager.create_request(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            params=request_model.parameters,  # Use stored parameters if provided.
            payload=request_model.payload
        )
        
        if self.proxy_server is not None:
            try:
                self.proxy_server.forward_request(request)
            except Exception as e:
                self.proxy_server.handle_forwarding_error(e)
                raise Exception("Proxy forwarding failed")
        
        self.last_response = self._send_http(request)
    
    def receive_response(self) -> Optional[HttpResponse]:
        return self.last_response

    def get_status_code(self) -> int:
        if self.last_response is not None:
            return self.last_response.status_code
        raise RuntimeError("No response available. Send a request first.")

    def get_response_body(self) -> str:
        if self.last_response is not None:
            return self.last_response.body
        raise RuntimeError("No response available. Send a request first.")

    def _send_http(self, request: HttpRequest) -> HttpResponse:
        try:
            if request.method.upper() == "GET":
                response = requests.get(request.url, headers=request.headers, params=request.payload)
            else:
                response = requests.request(request.method, request.url, headers=request.headers, json=request.payload)
            return HttpResponse(response.status_code, response.text, dict(response.headers))
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")

# --- Example usage ---
if __name__ == "__main__":
    # For demonstration purposes, we define a dummy RequestModel.
    # In your application, this will be your actual RequestModel class.
    from dataclasses import dataclass

    @dataclass
    class RequestModel:
        id: int
        url: str
        method: str
        headers: Dict[str, str]
        parameters: Dict[str, str]
        payload: Any

    # Create a dummy request (this would be created by your request manager in practice).
    dummy_request = RequestModel(
        id=1,
        url="https://httpbin.org/post",
        method="POST",
        headers={"Content-Type": "application/json"},
        parameters={},  # Query parameters if any; for GET requests.
        payload={"key": "value"}
    )
    
    req_manager = RequestManager()
    proxy_server = ProxyServer()
    client = HTTPClient(request_manager=req_manager, proxy_server=proxy_server)
    
    # Use the new method to send a request crafted by the request manager.
    client.send_request_from_model(dummy_request)
    
    response = client.receive_response()
    if response:
        print("Status Code:", client.get_status_code())
        print("Headers:", response.headers)
        print("Response Body:", client.get_response_body())
