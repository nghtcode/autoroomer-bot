import asyncio
import discord
from src.bot import Bot
from src.utils.config import Config
from src.utils.localization import Localization
from src.utils.logger import setup_async_logger

async def main():
    # Create logger
    logger = await setup_async_logger('Main')
    
    # Initialize configuration
    config = Config()
    await config.initialize(logger)
    
    # Initializing localization
    localization = Localization(config.lang, logger)
    
    # Initializing bot
    bot = Bot(config, localization, logger)
    await bot.setup()
    
    try:
        await bot.start(config.token)
    except discord.errors.PrivilegedIntentsRequired:
        await logger.error("❌ Privileged intents are not enabled in the Discord Developer Portal. "
                           "Please enable 'Message Content Intent' at https://discord.com/developers/applications")
        raise
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("❌ Bot was stopped manually")
    except Exception as e:
        await logger.error(f"❌ Failed to start bot: {e}")
        raise
    finally:
        await bot.close()
        logger.stop()


if __name__ == "__main__":
    asyncio.run(main())