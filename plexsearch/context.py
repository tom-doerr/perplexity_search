"""Conversation context management module."""
from typing import Dict, List

class ConversationContext:
    """Manage conversation context and history."""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the context."""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the context."""
        self.messages.append({"role": "assistant", "content": content})
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get a copy of the current context."""
        return self.messages.copy()
