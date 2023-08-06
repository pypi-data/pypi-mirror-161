#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import wait, sleep, ensure_future

class Runner:
    def __init__(self, task, repeat = 1, delay = 0):
        self.task = task
        self.repeat = repeat
        self.delay = delay
        self.results = []
    def __await__(self):
        async def __await__():
            async def futures():
                for i in range(self.repeat):
                    await sleep(self.delay)
                    result = await self.task()
                    self.results.append(result)
                return self.results
            return await ensure_future(futures())
        return __await__().__await__()

class Coroutine:
    def __init__(self, tasks):
        self.tasks = tasks

    def __await__(self):
        async def __await__():
            finished, _ = await wait([Runner(*i) for i in self.tasks])
            return [i.result() for i in finished]
        return __await__().__await__()
