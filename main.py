import asyncio
from interface.user_interface import run_user_interface


async def main():
    await run_user_interface()


if __name__ == "__main__":
    asyncio.run(main())