import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict

class Localization:
    __slots__ = ('translations', 'locales_dir', 'logger')
    
    def __init__(self, locale_file: str, logger, locales_dir: str = "locales"):
        self.translations: Dict[str, str] = {}
        self.locales_dir = Path(locales_dir)
        self.logger = logger
        asyncio.create_task(self.load_locale(locale_file))

    async def load_locale(self, locale_file: str) -> None:
        """Load one localization file asynchronously"""
        file_path = self.locales_dir / locale_file
        if not file_path.exists():
            await self.logger.error(f"❌ Localization file {file_path} was not found")
            raise FileNotFoundError(f"❌ Localization file {file_path} was not found")
        
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
            self.translations = json.loads(content)
        await self.logger.info(f"✅ Loaded localization file: {locale_file}")

    def get_text(self, key: str, **kwargs) -> str:
        """Get a translated string with support for nested keys and formatting"""
        translation = self.translations
        for part in key.split('.'):
            translation = translation.get(part, f"❌ Missing translation: {key}")
            if isinstance(translation, str):
                break
        return translation.format(**kwargs) if kwargs and isinstance(translation, str) else translation