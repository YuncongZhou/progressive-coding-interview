"""
Chat Messages System - Stage 4

Chat messages with backup/restore (zip/unzip) functionality.

Design Rationale:
- Store remaining TTL in backup for recalculation on restore
- Use zlib for compression
"""

import json
import uuid
import zlib


class ChatSystem:
    """Chat message storage system with backup/restore."""

    def __init__(self):
        self._messages: dict[str, dict] = {}
        self._user_messages: dict[str, set[str]] = {}
        self._backups: dict[str, bytes] = {}

    def send_message(self, user_id: str, message_id: str, content: str) -> bool:
        if message_id in self._messages:
            return False
        self._messages[message_id] = {
            "user_id": user_id,
            "content": content,
            "expires_at": None
        }
        if user_id not in self._user_messages:
            self._user_messages[user_id] = set()
        self._user_messages[user_id].add(message_id)
        return True

    def get_message(self, message_id: str) -> dict | None:
        if message_id not in self._messages:
            return None
        msg = self._messages[message_id]
        return {"user_id": msg["user_id"], "content": msg["content"]}

    def delete_message(self, message_id: str) -> bool:
        if message_id not in self._messages:
            return False
        user_id = self._messages[message_id]["user_id"]
        if user_id in self._user_messages:
            self._user_messages[user_id].discard(message_id)
        del self._messages[message_id]
        return True

    def list_messages(self, user_id: str) -> list[str]:
        if user_id not in self._user_messages:
            return []
        return sorted(self._user_messages[user_id])

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        if user_id not in self._user_messages:
            return []
        return sorted(mid for mid in self._user_messages[user_id] if mid.startswith(prefix))

    def send_message_with_expiry(
        self, user_id: str, message_id: str, content: str, timestamp: int, ttl: int
    ) -> bool:
        if message_id in self._messages:
            return False
        self._messages[message_id] = {
            "user_id": user_id,
            "content": content,
            "expires_at": timestamp + ttl
        }
        if user_id not in self._user_messages:
            self._user_messages[user_id] = set()
        self._user_messages[user_id].add(message_id)
        return True

    def get_message_at(self, message_id: str, timestamp: int) -> dict | None:
        if message_id not in self._messages:
            return None
        msg = self._messages[message_id]
        if msg["expires_at"] is not None and timestamp >= msg["expires_at"]:
            return None
        return {"user_id": msg["user_id"], "content": msg["content"]}

    def list_messages_at(self, user_id: str, timestamp: int) -> list[str]:
        if user_id not in self._user_messages:
            return []
        result = []
        for mid in self._user_messages[user_id]:
            msg = self._messages[mid]
            if msg["expires_at"] is None or timestamp < msg["expires_at"]:
                result.append(mid)
        return sorted(result)

    # Stage 4 methods

    def zip_messages(self, user_id: str, timestamp: int) -> str:
        """Creates compressed backup of user's non-expired messages."""
        backup_data = []
        if user_id in self._user_messages:
            for mid in self._user_messages[user_id]:
                msg = self._messages[mid]
                if msg["expires_at"] is None or timestamp < msg["expires_at"]:
                    remaining_ttl = None
                    if msg["expires_at"] is not None:
                        remaining_ttl = msg["expires_at"] - timestamp
                    backup_data.append({
                        "message_id": mid,
                        "content": msg["content"],
                        "remaining_ttl": remaining_ttl
                    })

        json_data = json.dumps({"user_id": user_id, "messages": backup_data})
        compressed = zlib.compress(json_data.encode("utf-8"))
        backup_id = str(uuid.uuid4())
        self._backups[backup_id] = compressed
        return backup_id

    def unzip_messages(self, backup_id: str, timestamp: int) -> int:
        """Restores messages from backup, recalculating TTLs."""
        if backup_id not in self._backups:
            return 0

        compressed = self._backups[backup_id]
        json_data = zlib.decompress(compressed).decode("utf-8")
        data = json.loads(json_data)

        user_id = data["user_id"]
        count = 0

        for msg_data in data["messages"]:
            mid = msg_data["message_id"]
            content = msg_data["content"]
            remaining_ttl = msg_data["remaining_ttl"]

            if remaining_ttl is None:
                expires_at = None
            else:
                expires_at = timestamp + remaining_ttl

            self._messages[mid] = {
                "user_id": user_id,
                "content": content,
                "expires_at": expires_at
            }
            if user_id not in self._user_messages:
                self._user_messages[user_id] = set()
            self._user_messages[user_id].add(mid)
            count += 1

        return count
