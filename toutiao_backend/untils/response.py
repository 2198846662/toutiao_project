from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#封装响应格式
def success_response(message: str = "success", data: Any = None):
    content = {
        "code": 200,
        "message": message,
        "data": data    #重点是data的类型
    }
#目标:把任何FastAPI、pydantic、orm对象都要正常响应 -> code，message，data
    return JSONResponse(
        content=jsonable_encoder(content)  #把content转换成JSON可序列化的格式
    )
 