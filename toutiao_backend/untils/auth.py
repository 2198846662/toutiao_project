from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users
#根据token查询用户


async def get_current_user(authorization: str = Header(..., alias="Authorization"),
                            db: AsyncSession = Depends(get_db)):
    token = authorization.replace("Bearer ", "")  #提取token
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的token")
    return user