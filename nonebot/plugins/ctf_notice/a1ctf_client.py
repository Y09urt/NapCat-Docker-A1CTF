import asyncio
import aiohttp
import json
import hashlib
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_401(func):
    @wraps(func)
    async def wrapper(client, *args, **kwargs):
        try:
            return await func(client, *args, **kwargs)
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                logger.warning("🚨 Received 401 Unauthorized. Attempting to re-login...")
                await client.login()
                logger.info("🔁 Re-attempting the request after re-login...")
                return await func(client, *args, **kwargs)
            else:
                raise
    return wrapper

class A1CTFClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = aiohttp.ClientSession(headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        })
        self.token = None

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def _fnv1a_32(self, data):
        FNV_OFFSET_BASIS_32 = 0x811c9dc5
        FNV_PRIME_32 = 0x01000193
        hash_value = FNV_OFFSET_BASIS_32
        for byte in data.encode('utf-8'):
            hash_value ^= byte
            hash_value = (hash_value * FNV_PRIME_32) & 0xffffffff
        return hash_value

    def _prng(self, seed, length):
        state = self._fnv1a_32(seed)
        result = ""
        while len(result) < length:
            state ^= (state << 13) & 0xffffffff
            state ^= (state >> 17) & 0xffffffff  
            state ^= (state << 5) & 0xffffffff
            result += f"{state:08x}"
        return result[:length]

    async def _solve_captcha(self):
        logger.info("🔐 Starting captcha challenge...")
        try:
            challenge_url = f"{self.base_url}/api/cap/challenge"
            async with self.session.post(challenge_url, json={}) as resp:
                resp.raise_for_status()
                challenge_data = await resp.json()
            
            challenge_token = challenge_data.get("token")
            challenge_info = challenge_data.get("challenge", {})
            count = challenge_info.get("c")
            difficulty = challenge_info.get("d") 
            size = challenge_info.get("s")
            
            if not all([challenge_token, count, difficulty, size]):
                logger.error("❌ Failed to get valid captcha challenge parameters.")
                return None
                
            logger.info(f"   Challenge: count={count}, difficulty={difficulty}, size={size}")
            
            solutions = []
            start_time = time.time()
            
            for i in range(count):
                salt_seed = challenge_token + str(i + 1)
                target_seed = challenge_token + str(i + 1) + "d"
                salt = self._prng(salt_seed, size)
                target = self._prng(target_seed, difficulty)
                
                solution = 0
                while True:
                    test_input = salt + str(solution)
                    hash_result = hashlib.sha256(test_input.encode()).hexdigest()
                    if hash_result.startswith(target):
                        solutions.append(solution)
                        break
                    solution += 1
            
            end_time = time.time()
            logger.info(f"   ✅ Challenge solved in {end_time - start_time:.2f} seconds")
            
            redeem_url = f"{self.base_url}/api/cap/redeem"
            redeem_payload = {"token": challenge_token, "solutions": solutions}
            async with self.session.post(redeem_url, json=redeem_payload) as resp:
                resp.raise_for_status()
                redeem_data = await resp.json()
            
            if redeem_data.get("success"):
                final_token = redeem_data.get("token")
                logger.info("   ✅ Captcha token redeemed successfully")
                return final_token
            else:
                logger.error(f"❌ Failed to redeem captcha: {redeem_data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during captcha process: {e}")
            return None

    async def login(self):
        logger.info("🚀 Attempting to login...")
        captcha_token = await self._solve_captcha()
        if not captcha_token:
            logger.error("❌ Could not solve captcha, login aborted")
            return False
        
        login_url = f"{self.base_url}/api/auth/login"
        payload = {"username": self.username, "password": self.password, "captcha": captcha_token}
        
        try:
            async with self.session.post(login_url, json=payload) as response:
                response.raise_for_status()
                if 'a1token' in response.cookies:
                    self.token = response.cookies['a1token'].value
                    logger.info("✅ Login successful!")
                    return True
                else:
                    logger.error(f"❌ Login failed: Token not found. Response: {await response.text()}")
                    return False
        except aiohttp.ClientResponseError as e:
            if e.status == 401:
                logger.error("❌ Login failed: 401 Unauthorized. Check credentials.")
            else:
                logger.error(f"❌ HTTP error during login: {e}. Response: {e.message}")
            return False
        except Exception as e:
            logger.error(f"❌ Network error during login: {e}")
            return False

    @retry_on_401
    async def request(self, method, url, **kwargs):
        """封装请求，自动处理401并重试"""
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

# 全局客户端实例
a1ctf_client = None

async def initialize_a1ctf_client(base_url, username, password):
    """初始化并登录A1CTF客户端"""
    global a1ctf_client
    if not a1ctf_client:
        logger.info("Initializing A1CTF client...")
        client = A1CTFClient(base_url=base_url, username=username, password=password)
        if await client.login():
            a1ctf_client = client
            logger.info("A1CTF client initialized and logged in successfully.")
        else:
            logger.error("Failed to initialize A1CTF client.")
            await client.close_session()
    return a1ctf_client

def get_a1ctf_client():
    """获取全局A1CTF客户端实例"""
    return a1ctf_client

async def close_a1ctf_client():
    """关闭全局客户端会话"""
    global a1ctf_client
    if a1ctf_client:
        await a1ctf_client.close_session()
        a1ctf_client = None
        logger.info("A1CTF client session closed.")