import aiohttp
import requests

from typing import Optional
from .exceptions import RateLimitedException, ServerErrorException, JokeNotFoundException

def getDadJoke(joke_id: str = None) -> Optional[str]:
    resp = requests.get(f"https://icanhazdadjoke.com/{f'j/{joke_id}' if joke_id is not None else ''}", headers={"Accept": "text/plain"})

    if resp.status_code == 429:
        raise RateLimitedException("Ratelimited for one minute.")
    elif resp.status_code == 404:
        raise JokeNotFoundException(resp.text)
    elif resp.status_code != 200:
        raise ServerErrorException(f"Server returned {resp.status_code}.\n\nServer response: {resp.text}")

    joke = resp.json()["joke"]

    return joke

def searchDadJokes(query: str = "") -> Optional[list]:
    resp = requests.get("https://icanhazdadjoke.com/search", {"term": query}, headers={"Accept": "application/json"})

    if resp.status_code == 429:
        raise RateLimitedException("Ratelimited for one minute.")
    elif resp.status_code != 200:
        raise ServerErrorException(f"Server returned {resp.status_code}.\n\nServer response:{resp.text}")

    jokes = resp.json()["result"]

    return [ joke for joke in jokes ]

async def getDadJokeAsync(
    joke_id: str = None, 
    http: Optional[aiohttp.ClientSession] = None
) -> Optional[str]:
    if http is None:
        http = aiohttp.ClientSession()

    async with http.get(f"https://icanhazdadjoke.com/{f'j/{joke_id}' if joke_id is not None else ''}", headers={"Accept": "application/json"}) as resp:
        if resp.status == 429:
            raise RateLimitedException("Ratelimited for one minute.")
        elif resp.status == 404:
            raise JokeNotFoundException(await resp.text())
        elif resp.status != 200:
            raise ServerErrorException(f"Server returned {resp.status}.\n\nServer response:{await resp.text()}")

        joke = (await resp.json())["joke"]

    return joke

async def searchDadJokesAsync(
    query: str = "", 
    http: Optional[aiohttp.ClientSession] = None
) -> Optional[list]:
    if http is None:
        http = aiohttp.ClientSession()

    async with http.get("https://icanhazdadjoke.com/search", params={"term": query}, headers={"Accept": "text/plain"}) as resp:
        if resp.status == 429:
            raise RateLimitedException("Ratelimited for one minute.")
        elif resp.status != 200:
            raise ServerErrorException(f"Server returned {resp.status}.\n\nServer response:{await resp.text()}")

        jokes = (await resp.json())["results"]

    return [ joke for joke in jokes ]