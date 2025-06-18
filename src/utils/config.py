import os
from dotenv import load_dotenv


class Config:
    __slots__ = ('token', 'text_channel_id', 'voice_1', 'voice_2', 'voice_3', 'lang', 'logger')
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DISCORD_TOKEN")
        self.text_channel_id = int(os.getenv("TEXT_CHANNEL_ID"))
        self.voice_1 = int(os.getenv("VOICE_1"))
        self.voice_2 = int(os.getenv("VOICE_2"))
        self.voice_3 = int(os.getenv("VOICE_3"))
        self.lang = os.getenv("LANG", "en.json")
        self.logger = None
        
    async def initialize(self, logger):
        self.logger = logger
        if not self.token:
            await self.logger.error("❌ DISCORD_TOKEN not found in .env")
            raise ValueError("❌ DISCORD_TOKEN is required")
        if not self.lang.endswith('.json'):
            await self.logger.error("❌ LANG must reference a .json file (e.g., 'en' for 'en.json')")
            raise ValueError("❌ LANG must reference a .json file")
        await self.logger.info("✅ Configuration loaded successfully")