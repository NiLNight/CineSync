import json
import aio_pika
import structlog
from .config import settings

logger = structlog.get_logger()

class EventPublisher:
    """
    Класс для отправки событий в брокер сообщений RabbitMQ.
    """
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        """Устанавливает соединение с RabbitMQ с повторными попытками."""
        import asyncio
        retries = 5
        while retries > 0:
            try:
                self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                self.channel = await self.connection.channel()
                logger.info("Successfully connected to RabbitMQ")
                return
            except Exception as e:
                retries -= 1
                logger.warning(f"Failed to connect to RabbitMQ, retrying... ({retries} left). Error: {e}")
                if retries == 0:
                    logger.error("Could not connect to RabbitMQ after multiple attempts")
                    raise
                await asyncio.sleep(5)

    async def close(self):
        """Закрывает соединение с RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")

    async def publish_user_created(self, user_id: int, email: str):
        """
        Отправляет событие о регистрации нового пользователя.
        """
        if not self.channel:
            logger.error("RabbitMQ channel not initialized")
            return

        message_body = {
            "event": "UserCreated",
            "user_id": user_id,
            "email": email
        }

        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    content_type="application/json"
                ),
                routing_key="user_created_queue"
            )
            logger.info(f"Published UserCreated event for user {email}")
        except Exception as e:
            logger.error(f"Failed to publish UserCreated event: {e}")

# Синглтон для использования в приложении
publisher = EventPublisher()
