### dadjokeAPI - A simple API for your dad joke needs.

Non-asynchronous usage:
```python
from dadjokeAPI import searchDadJokes
from dadjokeAPI import getDadJoke

# Prints a dad joke with a random or specified ID.
# Raises JokeNotFoundException if the joke was not found.
print(getDadJoke("0189hNRf2g"))

# Prints a list of dad jokes with a random or provided term.
# Raises JokeNotFoundException if no jokes were found.
print(searchDadJokes("fish"))
```

Asynchronous usage:
```python
from dadjokeAPI import searchDadJokesAsync
from dadjokeAPI import getDadJokeAsync

# Prints a dad joke with a random or specified ID.
# Raises JokeNotFoundException if the joke was not found.
# Has an optional aiohttp.ClientSession argument called http
# in case you want to provide your session.
print(await getDadJokeAsync("0189hNRf2g"))

# Prints a list of dad jokes with a random or provided term.
# Raises JokeNotFoundException if no jokes were found.
# Has an optional aiohttp.ClientSession argument called http
# in case you want to provide your session.
print(await searchDadJokesAsync("fish"))
```