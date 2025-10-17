# utils/responses.py
from fastapi.responses import JSONResponse

def success_response(data, message="OK"):
    return JSONResponse(content={"status": "success", "message": message, "data": data} )

def error_response(message="Error", status_code=400):
    return JSONResponse(content={"status": "error", "message": message}, status_code=status_code)

def existence_response_dict(exists: bool, message_if_exists="Exists", message_if_not_exists="Does not exist"):
    if exists:
        return {"status": "success", "message": message_if_exists, "exists": True}
    else:
        return {"status": "success", "message": message_if_not_exists, "exists": False}