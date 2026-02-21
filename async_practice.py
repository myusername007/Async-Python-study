import asyncio
import time

async def fetch_data(name: str, delay: int):
    print(f"{name}: починаю")
    await asyncio.sleep(delay)
    print(f"{name}: готово")
    return f"{name} result"

async def main():
    start = time.time()

    #A - послідовно(sync)
  #  await fetch_data("task1", 2)
  #  await fetch_data("task2", 2)

    results = await asyncio.gather(
        fetch_data("task1", 3),
        fetch_data("task2", 2),
        fetch_data("task3", 1),

    )

    #print(f"Час: {time.time() - start:.1f}s") #очікування ~4s

    print(results) # ~2s
    
asyncio.run(main())