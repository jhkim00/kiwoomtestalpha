import time
import asyncio
import logging

logger = logging.getLogger()

class CoolDown:
    def __init__(self, limit):
        self.limit = limit  # 1초 동안 허용되는 최대 호출 횟수
        self.call_count = 0  # 현재 1초 내 호출된 횟수
        self.last_reset_time = time.time()  # 마지막 호출 제한 리셋 시간
        self.lock = asyncio.Lock()  # 동시 실행 방지용 Lock

    async def call(self):
        """1초에 `limit` 회 호출을 허용하는 메서드"""
        async with self.lock:
            current_time = time.time()

            # 1초마다 호출 카운트를 초기화
            if current_time - self.last_reset_time >= 1:
                self.call_count = 0
                self.last_reset_time = current_time

            # 호출 횟수가 limit을 초과하면 대기
            if self.call_count >= self.limit:
                logger.debug(f"Rate limit exceeded. Cooling down for 1 seconds")
                await asyncio.sleep(1)

                # 대기 후 호출 횟수 초기화
                self.call_count = 0
                self.last_reset_time = time.time()

            # 호출 성공
            self.call_count += 1
            logger.debug(f"Method called. Call count: {self.call_count}")
