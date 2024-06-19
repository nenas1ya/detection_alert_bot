import asyncio
import logging
from utils import CMDLineArguments, get_envs, DetectionsParser
from bot import TelegramBot


async def check_detections_periodically(bot, parser, interval=60):
    """
    Periodically check for new detections and update the bot.
    """
    while True:
        try:
            token = await parser.get_token()
            detections = await parser.get_detects(token)
            await bot.update_detections(detections)
            logging.info("Updated detections.")
        except Exception as e:
            logging.error("Failed to update detections: %s", e)
        await asyncio.sleep(interval)  # Adjust the interval as needed


async def main():
    logging.basicConfig(level=logging.DEBUG)
    p = CMDLineArguments()
    options = p.parse_args()

    env_vars = get_envs(
        "STK_LOGIN",
        "STK_PASSWORD",
        "DUTSSD_LOGIN",
        "DUTSSD_PASSWORD",
        "DEV_TOKEN",
        "BOT_TOKEN",
    )

    parser = DetectionsParser(
        login=env_vars["STK_LOGIN"], passw=env_vars["STK_PASSWORD"]
    )

    bot = TelegramBot(env_vars["BOT_TOKEN"])

    # Start the bot and the periodic check concurrently
    await asyncio.gather(bot.start(), check_detections_periodically(bot, parser))


if __name__ == "__main__":
    logging.info("Run asyncio from main")
    asyncio.run(main())
