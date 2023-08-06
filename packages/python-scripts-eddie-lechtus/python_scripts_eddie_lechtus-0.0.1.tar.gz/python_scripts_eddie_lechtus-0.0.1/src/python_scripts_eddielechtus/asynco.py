
import asyncio
import multiprocessing


async def io_related(name):
    print(multiprocessing.current_process())
    print(f'{name} started')
    await asyncio.sleep(1000)
    print(f'{name} finished')


async def main():
    await asyncio.gather(
        io_related('first'),
        io_related('second'),
    )  # 1s + 1s = over 1s


if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())