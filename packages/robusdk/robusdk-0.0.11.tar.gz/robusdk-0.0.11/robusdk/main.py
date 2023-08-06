#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import ClientSession
from .lib.digest import DigestAuth
from .coroutine import Coroutine

def Client(url, username, password):
    class Client:
        Coroutine = Coroutine
        def __getattr__(self, prop):
            async def callable(**args):
                async with ClientSession() as session:
                    response = await DigestAuth(username, password, session).request('post', f'''{url}api/jsonrpc/{prop}''', json=args)
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 500:
                        result = await response.json()
                        response.reason = result.get('message')
                        return response.raise_for_status()
                    else:
                        return response.raise_for_status()
            return callable
    return Client()
