import os
from dotenv import load_dotenv


class Config:    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DISCORD_TOKEN")
        self.text_channel_id = int(os.getenv("TEXT_CHANNEL_ID"))
        self.voice_1 = int(os.getenv("VOICE_1"))
        self.voice_2 = int(os.getenv("VOICE_2"))
        self.voice_3 = int(os.getenv("VOICE_3"))
        self.category_create_room = int(os.getenv("CATEGORY_CREATE_ROOM"))
        self.category_find = int(os.getenv("CATEGORY_FIND"))
        self.category_filled = int(os.getenv("CATEGORY_FILLED"))
        self.lang = os.getenv("LANG")
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