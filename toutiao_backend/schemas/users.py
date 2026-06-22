from pydantic import BaseModel, ConfigDict, Field

class UserRequest(BaseModel):
    username: str 
    password: str 


#user_info的数据类型   对应的类：基础类 + InFo类(id, 用户名)
class UserInfoBase(BaseModel):
    '''
    用户信息基础数据模型
    '''
    nickname: str | None = Field(None, max_length=50, description="用户昵称")
    avatar: str | None = Field(None, max_length=255, description="用户头像URL")
    gender: str | None = Field(None, max_length=10, description="用户性别")
    bio: str | None = Field(None, max_length=500, description="用户简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    role: str = "user"

    model_config = ConfigDict(
        from_attributes=True,  #允许从ORM对象创建模型实例
    )

#data的数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    #添加模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  #允许通过字段名称或别名进行赋值
        from_attributes=True,  #允许从ORM对象创建模型实例
    )


#更新用户信息请求体
class UserUpdateRequest(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="用户昵称")
    avatar: str | None = Field(None, max_length=255, description="用户头像URL")
    gender: str | None = Field(None, max_length=10, description="用户性别")
    bio: str | None = Field(None, max_length=500, description="用户简介")
    phone: str | None = Field(None, max_length=20, description="用户手机号")

#更新用户密码
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码",alias="oldPassword")
    new_password: str = Field(..., description="新密码", min_length=6, alias="newPassword")
