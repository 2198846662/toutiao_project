import redis.asyncio as redis
import json
import os
from pathlib import Path


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.152.128")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "xcl123456") or None
REDIS_TIMEOUT = float(os.getenv("REDIS_TIMEOUT", "1"))


#创建redis连接对象
redis_client = None
if REDIS_ENABLED:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=REDIS_TIMEOUT,
        socket_timeout=REDIS_TIMEOUT,
        retry_on_timeout=False,
    )

#设置 和 读取(字符串 和 列表或字典) "{[]}"
#读取：字符串
async def get_cache(key: str):
    if not redis_client:
        return None
    try:
        value = await redis_client.get(key)
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None
    return value

#读取：列表或字典
async def get_cache_json(key: str):
    if not redis_client:
        return None
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
    if not redis_client:
        return False
    try:
        if isinstance(value, (dict, list)):
            #转字符串再存
            value = json.dumps(value, ensure_ascii=False)    #中文正常显示
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False


async def delete_cache_pattern(pattern: str):
    if not redis_client:
        return True
    try:
        keys = [key async for key in redis_client.scan_iter(match=pattern)]
        if keys:
            await redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"删除缓存失败: {e}")
        return False
