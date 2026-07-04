import asyncio
import json
import os
import aio_pika
import structlog
from observability import setup_observability
from opentelemetry.instrumentation.aio_pika import AioPikaInstrumentor

# Будет инициализировано в main
logger = None

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

async def check_health() -> dict:
    """Простая проверка работоспособности сервиса (Health Check)"""
    # В будущем здесь может быть проверка подключения к RabbitMQ
    logger = structlog.get_logger()
    await logger.ainfo("Health check requested")
    return {"status": "healthy", "service": "notification_service"}

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    """
    Обработка входящего сообщения.
    """
    async with message.process():
        try:
            body = json.loads(message.body.decode())
            event_name = body.get("event")
            
            if event_name == "UserCreated":
                user_id = body.get("user_id")
                email = body.get("email")
                
                logger.info("=" * 50)
                logger.info(f"📧 SENDING WELCOME EMAIL TO: {email}")
                logger.info(f"User ID: {user_id}")
                logger.info("Welcome to CineSync! We happy to see you.")
                logger.info("=" * 50)
            else:
                logger.warning(f"Unknown event type: {event_name}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

async def main():
    """
    Главный цикл сервиса.
    """
    global logger
    logger = setup_observability("notification_service")
    AioPikaInstrumentor().instrument()

    connection = None
    while True:
        try:
            # Подключение с повторными попытками
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            
            # Объявляем очередь (на случай если она еще не создана)
            queue = await channel.declare_queue("user_created_queue", durable=False)
            
            logger.info("[*] Waiting for messages. To exit press CTRL+C")
            
            # Начинаем прослушивание
            await queue.consume(process_message)
            
            # Ждем пока соединение открыто
            try:
                await asyncio.Future()
            finally:
                await connection.close()
                
        except Exception as e:
            logger.error(f"Connection failed, retrying in 5s... Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped")
