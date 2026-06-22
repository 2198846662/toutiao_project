from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users
from crud.users import create_user, get_user_by_username
from models.users import User
from schemas.users import UserAuthResponse, UserChangePasswordRequest, UserInfoResponse, UserRequest, UserUpdateRequest
from untils.response import success_response
from untils.auth import get_current_user
router = APIRouter(prefix="/api/user", tags=["users"]) 

@router.post("/register")
async def register_user(user_data: UserRequest, db: AsyncSession = Depends(get_db)):  #db和用户信息(pydantic数据校验)
    #注册逻辑：验证用户是否存在 -> 创建新用户 -> 生成token -> 返回响应
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    #创建新用户
    user = await create_user(db, user_data)
    #生成token
    token = await users.create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "msg": "用户注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #                     }
    #             }
    #         }
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户注册成功", data=response_data)

@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    #登录逻辑 -> 验证用户是否存在 -> 验证密码 -> 生成token -> 返回响应
    user = await users.authenticate_user(db, user_data.username, user_data.password)  #验证用户存在和密码正确
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    #生成token
    token = await users.create_token(db, user.id)
    #返回响应
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户登录成功", data=response_data)


#查token查用户 -> 封装crud -> 功能整合成一个工具函数 -> 路由导入使用：依赖注入
@router.get("/info")
async def get_user_info(user : User= Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))
    

#修改用户信息(验证用户身份token -> 更新用户信息 -> 请求体参数(定义pydantic模型) -> 返回响应)
#参数：用户输入 + 验证token + 数据库依赖
@router.put("/update")
async def update_user_info(
    user_info: UserUpdateRequest, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
    ):
    try:
        user = await users.update_user_info(db, user.username, user_info)  #调用crud封装好的方法，更新数据
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


#修改用户密码
@router.put("/password")
async def update_user_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        res_change_pwd = await users.update_user_password(db, user, password_data.old_password, password_data.new_password)  #调用crud封装好的方法，更新密码
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not res_change_pwd:
        raise HTTPException(status_code=400, detail="旧密码错误，修改密码失败")
    return success_response(message="修改用户密码成功")
