import time
import asyncio
import logging

logger = logging.getLogger()


class CoolDown:
    def __init__(self, limit, interval):
        self.limit = limit  # 1초에 허용되는 최대 호출 횟수
        self.interval = interval  # 쿨타임 기간 (초)
        self.call_times = []  # 호출 시간을 저장할 리스트

    async def call(self):
        current_time = time.time()

        # 현재 시간 기준으로 interval 이전의 호출 기록만 남김
        self.call_times = [t for t in self.call_times if current_time - t <= self.interval]

        # 호출 제한에 도달하지 않으면 호출을 허용하고 시간을 기록
        if len(self.call_times) < self.limit:
            self.call_times.append(current_time)
            logger.debug("Method called")
        else:  # 호출 제한에 도달하면 쿨타임 동안 블록
            remaining_time = self.interval - (current_time - self.call_times[0])
            await asyncio.sleep(remaining_time)
            self.call_times.append(time.time())
            logger.debug("Method called after cooldown")
