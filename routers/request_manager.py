# request_manager.py
from fastapi import APIRouter, HTTPException
from models.models import RequestModel

router = APIRouter()

# In-memory store of requests (mock DB)
request_store: dict[int, RequestModel] = {}

@router.post("/create_request", response_model=RequestModel)
async def create_request(request: RequestModel):
    if request.id in request_store:
        raise HTTPException(status_code=400, detail="Request ID already exists")
    request_store[request.id] = request
    return request

@router.patch("/add_headers/{request_id}")
async def add_headers(request_id: int, headers: dict):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_store[request_id].headers.update(headers)
    return {"message": "Headers added", "headers": request_store[request_id].headers}

@router.patch("/set_payload/{request_id}")
async def set_payload(request_id: int, payload: dict):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_store[request_id].payload = payload
    return {"message": "Payload set", "payload": payload}

@router.patch("/update_headers/{request_id}")
async def update_headers(request_id: int, headers: dict):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_store[request_id].headers = headers
    return {"message": "Headers updated", "headers": headers}

@router.patch("/update_parameters/{request_id}")
async def update_parameters(request_id: int, parameters: dict):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_store[request_id].parameters = parameters
    return {"message": "Parameters updated", "parameters": parameters}

@router.patch("/update_payload/{request_id}")
async def update_payload(request_id: int, payload: dict):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_store[request_id].payload = payload
    return {"message": "Payload updated", "payload": payload}

# New endpoint: Send the stored request using the HTTPClient
@router.post("/send/{request_id}")
async def send_stored_request(request_id: int):
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail="Request not found")
    request_model = request_store[request_id]
    
    # Import the necessary HTTP client classes from Tools.py.
    # Adjust the import path if your Tools.py is located elsewhere.
    from routers.tools import HTTPClient, RequestManager as ToolsRequestManager, ProxyServer

    client = HTTPClient(ToolsRequestManager(), ProxyServer())
    try:
        client.send_request_from_model(request_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    response = client.receive_response()
    return {
        "status": response.status_code,
        "headers": response.headers,
        "body": response.body
    }
