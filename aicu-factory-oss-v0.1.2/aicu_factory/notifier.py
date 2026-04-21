from __future__ import annotations

from dataclasses import dataclass

import requests

from .config import Settings


@dataclass(slots=True)
class TelegramNotifier:
    enabled_flag: bool
    bot_token: str
    chat_id: str

    @classmethod
    def from_settings(cls, settings: Settings) -> "TelegramNotifier":
        return cls(
            enabled_flag=settings.telegram_enabled,
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        )

    def enabled(self) -> bool:
        return bool(self.enabled_flag and self.bot_token and self.chat_id)

    def send(self, text: str) -> None:
        if not self.enabled():
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = requests.post(
            url,
            data={"chat_id": self.chat_id, "text": text},
            timeout=20,
        )
        response.raise_for_status()
