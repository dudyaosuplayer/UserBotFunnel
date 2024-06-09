from pyrogram import Client
from loguru import logger


class MyClient(Client):
    client_name = "my_client"

    async def start(self):
        logger.info(f"{self.client_name} is starting...")
        await super().start()

    async def stop(self):
        logger.info(f"{self.client_name} is stopping...")
        await super().stop()

    def on_message(self, filters=None, group=0):
        return super().on_message(filters, group)
