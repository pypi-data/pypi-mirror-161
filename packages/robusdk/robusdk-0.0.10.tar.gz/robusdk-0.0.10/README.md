```js
(async () => {
  const client = require('robusdk')({
    url: 'http://localhost/',
    username: 'username',
    password: 'password'
  })
  const result = await new client.Coroutine([
    [() => client.methodA(paramsA)],
    [() => client.methodB(paramsB)]
  ])
  console.info(result)
})()
```

```python
async def future():
  from robusdk import Client
  client = Client(
    url='http://localhost/',
    username='username',
    password='password',
  )
  result = client.Coroutine([
      (lambda: client.methodA(paramsA)),
      (lambda: client.methodB(paramsB)),
  ])
  print(result)

from asyncio import get_event_loop
loop = get_event_loop()
loop.run_until_complete(future())
loop.close()
```
