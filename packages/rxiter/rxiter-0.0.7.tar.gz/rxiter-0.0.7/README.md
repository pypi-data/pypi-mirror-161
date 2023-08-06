# RxIter

RxIter brings observables to python in a bare bones way by using **async generators** and the *async* *await* syntax. In this paradigm **observables** are analogous to **async iterables**, and **observers** analogous to **async iterators**.


It implements 2 fundamental observable operations, which may be familar to those who know **rxpy**.

* [**share**](#Share)
* [**repeat**](#Repeat)

## Operations

### Share
`share` allows multiple "observers" to subscribe the same observable
```python
import asyncio
from rxiter import share

async def main():

    @share
    async def count():   # a counting "observable"
        v = 0
        while True:
            print(f"returning value {v}")
            yield v
            await asyncio.sleep(1)
            v += 1

    async def count_squared(obs):  # a counting "observer"
        async for v in obs: 
            print(f"{v} squared is {v**2}")

    square_task_subscription = asyncio.Task(count_squared(count()))  # subscribe

    async def count_cubed(obs):  # another counting "observer
        async for v in obs:
            print(f"{v} cubed is {v**3}")

    cube_task_subscription = asyncio.Task(count_cubed(count())) # subscribe

    await asyncio.gather(square_task_subscription, cube_task_subscription)

asyncio.run(main())
```
The output on this code would be:
```
returning value 0
0 squared is 0
0 cubed is 0
returning value 1
1 squared is 1
1 cubed is 1
returning value 2
2 squared is 4
2 cubed is 8
etc...
```
### Repeat
`repeat` takes a **iterator**, and "records" it's outputed values so that it is turned into an **iterable**, and can be "listened" back multiple times.

## Example
### Polling an API
Suppose we have a API endpoint that we would like to poll to get the most up to date weather in Toronto. We could set up an observable as follows:

```python
async get_toronto_weather():
  while True:
    yield await poll_my_api("api_enpoint")
    await asyncio.sleep(60 * 30)  # wait 30 minutes
```

If you want to "pipe" this to do further operations, like extract some specific content from the dict returned by `get_toronto_weather()`

```python
async get_temperature():
  async for v in poll_api():
    yield v["temperature"]
```

Now if we want to have multiple listeners, that is where the `share` comes into the picture. We can do

```python
@share
async get_toronto_weather():
  while True:
    yield await poll_my_api("api_enpoint")
    await asyncio.sleep(60 * 30)  # wait 30 minutes

async get_temperature():
  async for v in get_toronto_weather():
    yield v["temperature"]

async get_humidity():
  async for v in get_toronto_weather():
    yield v["humidity"]

asyncio.Task(get_temperature())
asyncio.Task(get_humidity())
```

and `get_toronto_weather()` will only run once for both `get_temperature()` and `get_humidity()`
### Realtime stdout on python subprocess
## Installation
```
pip install rxiter
```
