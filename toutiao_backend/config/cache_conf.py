import redis.asyncio as redis
import json
#创建redis连接对象
redis_client = redis.Redis(
    host="192.168.152.128",
    port=6379,
    db=0,
    password="xcl123456",
    decode_responses=True
) 

#设置 和 读取(字符串 和 列表或字典) "{[]}"
#读取：字符串
async def get_cache(key: str):
    try:
        value = await redis_client.get(key)
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None
    return value

#读取：列表或字典
async def get_cache_json(key: str):
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None

#设置缓存 setex(key, expire, value) 键 过期时间 值
async def set_cache(key: str, value, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            #转字符串再存
            value = json.dumps(value, ensure_ascii=False)    #中文正常显示
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False