import pytest
from plexsearch.context import ConversationContext

def test_conversation_context_initialization():
    context = ConversationContext()
    assert context.get_context() == []

def test_conversation_context_add_user_message():
    context = ConversationContext()
    context.add_user_message("Hello")
    assert context.get_context() == [{"role": "user", "content": "Hello"}]

def test_conversation_context_add_assistant_message():
    context = ConversationContext()
    context.add_assistant_message("Hi there!")
    assert context.get_context() == [{"role": "assistant", "content": "Hi there!"}]

def test_conversation_context_get_context():
    context = ConversationContext()
    context.add_user_message("Hello")
    context.add_assistant_message("Hi!")
    retrieved_context = context.get_context()
    assert retrieved_context == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
    # Ensure it's a copy
    retrieved_context.append({"role": "user", "content": "Another message"})
    assert context.get_context() == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]

def test_conversation_context_multiple_messages():
    context = ConversationContext()
    context.add_user_message("First")
    context.add_assistant_message("Response 1")
    context.add_user_message("Second") 
    context.add_assistant_message("Response 2")
    assert context.get_context() == [
        {"role": "user", "content": "First"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Second"},
        {"role": "assistant", "content": "Response 2"}
    ]

def test_conversation_context_empty_messages():
    context = ConversationContext()
    context.add_user_message("")
    context.add_assistant_message("")
    assert context.get_context() == [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]
import pytest
from plexsearch.context import ConversationContext

def test_conversation_context_initialization():
    context = ConversationContext()
    assert context.get_context() == []

def test_conversation_context_add_user_message():
    context = ConversationContext()
    context.add_user_message("Hello")
    assert context.get_context() == [{"role": "user", "content": "Hello"}]

def test_conversation_context_add_assistant_message():
    context = ConversationContext()
    context.add_assistant_message("Hi there!")
    assert context.get_context() == [{"role": "assistant", "content": "Hi there!"}]

def test_conversation_context_get_context():
    context = ConversationContext()
    context.add_user_message("Hello")
    context.add_assistant_message("Hi!")
    retrieved_context = context.get_context()
    assert retrieved_context == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
    # Ensure it's a copy
    retrieved_context.append({"role": "user", "content": "Another message"})
    assert context.get_context() == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
