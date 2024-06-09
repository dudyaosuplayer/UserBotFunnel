import asyncio
from logger import logger

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import UserIsBlocked, InputUserDeactivated
from sqlalchemy.future import select
from datetime import datetime, timedelta

from config import settings
from database import async_session_maker
from client import MyClient
from models import User, UserStatus

api_id = settings.API_ID
api_hash = settings.API_HASH
bot_token = settings.BOT_TOKEN

bot_app = MyClient('bot_app', api_id=api_id, api_hash=api_hash, bot_token=settings.BOT_TOKEN)

# Словарь для хранения сообщений пользователей
user_messages = {}


def add_user_message(user_id, message_text: str):
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message_text)


def check_keywords(user_id, keywords: list[str]):
    if user_id not in user_messages:
        return False
    for message in user_messages[user_id]:
        if any(keyword in message.lower() for keyword in keywords):
            return True
    return False


async def funnel_logic(client):
    while True:
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.status == UserStatus.alive))
            users = result.scalars().all()

            for user in users:
                try:
                    time_since_start = datetime.utcnow() - user.created_at

                    # Проверка на триггеры
                    if check_keywords(user.id, ["прекрасно", "ожидать"]):
                        logger.info(f"Найден триггер 'прекрасно', 'ожидать'! Пользователь: {user.id}")
                        user.status = UserStatus.finished
                        user.status_updated_at = datetime.utcnow()
                        await session.commit()
                        continue

                    if user.first_message and check_keywords(user.id, ["триггер1"]) and not user.second_message:
                        logger.info(f"Найден триггер 'триггер1'! Пользователь: {user.id}")
                        user.second_message = datetime.utcnow()
                        await session.commit()
                        continue

                    # Шаг 1: Отправка после 6 минут
                    if time_since_start > timedelta(minutes=6) and not user.first_message:
                        logger.info(f"Первый этап! Первое сообщение пользователя {user.id}!")
                        await client.send_message(user.id, "msg_1")
                        logger.info(f"Сообщение msg_1 отправлено пользователю {user.id}!")
                        user.first_message = datetime.utcnow()
                        await session.commit()
                        continue

                    # Шаг 2: Отправка после 39 минут
                    if user.first_message and datetime.utcnow() - user.first_message > timedelta(
                        minutes=39) and not user.second_message:
                        logger.info("Второй этап!")
                        await client.send_message(user.id, "msg_2")
                        logger.info(f"Сообщение msg_2 отправлено пользователю {user.id}!")
                        user.second_message = datetime.utcnow()
                        await session.commit()
                        continue

                    # Шаг 3: Отправка после 1 дня и 2 часов
                    if user.second_message and datetime.utcnow() - user.second_message > timedelta(days=1,
                                                                                                   hours=2) and not user.third_message:
                        logger.info("Третий этап!")
                        await client.send_message(user.id, "msg_3")
                        logger.info(f"Сообщение msg_3 отправлено пользователю {user.id}!")
                        user.third_message = datetime.utcnow()
                        user.status = UserStatus.finished
                        user.status_updated_at = datetime.utcnow()
                        await session.commit()

                except UserIsBlocked:
                    logger.error(f"Бот был заблокирован пользователем {user.id}.")
                    user.status = UserStatus.dead
                    user.status_updated_at = datetime.utcnow()
                    await session.commit()
                except InputUserDeactivated:
                    logger.error(f"Пользователь {user.id} деактивировал свой аккаунт.")
                    user.status = UserStatus.dead
                    user.status_updated_at = datetime.utcnow()
                    await session.commit()
                except Exception as e:
                    logger.error(f"Произошла ошибка при обработке пользователя {user.id}: {e}")


@bot_app.on_message(filters.private)
async def handle_message(client, message):
    add_user_message(message.from_user.id, message.text)
    async with async_session_maker() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(id=message.from_user.id, created_at=datetime.utcnow())
            session.add(user)
        await session.commit()


async def main():
    await bot_app.start()
    await funnel_logic(bot_app)
    await bot_app.stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
