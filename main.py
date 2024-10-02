import asyncio
import logging

from bethowen_app import BHApp

async def main():
    logging.basicConfig(level=logging.INFO)
    bh_app = BHApp()
    await bh_app.start()


if __name__ == "__main__":
    asyncio.run(main())

