"""Utility & helper functions."""

from typing import Any, List, Union

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from common.document_parsers import extract_file_content


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)


def process_message_content(content: Union[str, list[Union[str, dict]]]) -> str:
    """Process message content to extract text and file content.
    
    Args:
        content: The message content, which can be a string or a list of strings and dictionaries
                containing text and file information.
                
    Returns:
        str: The processed content with text and extracted file content.
    """
    if isinstance(content, str):
        return content
    
    processed_content = []
    
    for item in content:
        if isinstance(item, str):
            processed_content.append(item)
        elif isinstance(item, dict):
            if item.get("type") == "text":
                processed_content.append(item.get("text", ""))
            elif item.get("type") == "file" and item.get("source_type") == "base64":
                # Extract file information
                file_data = item.get("data", "")
                metadata = item.get("metadata", {})
                filename = metadata.get("filename", "unknown_file")
                mime_type = item.get("mime_type", "application/octet-stream")
                
                # Process the file content based on mime type
                file_content = extract_file_content(file_data, filename, mime_type)
                processed_content.append(f"\n\n文件内容 ({filename}):\n{file_content}")
    
    return "".join(processed_content).strip()


def process_messages(messages: List[Any]) -> List[Any]:
    """Process a list of messages to extract text and file content.
    
    Args:
        messages: A list of messages to process. Each message should have a content attribute.
        
    Returns:
        List[Any]: A new list of messages with processed content, preserving all other attributes.
    """
    processed_messages = []
    for message in messages:
        # Create a copy of the message to avoid modifying the original
        processed_message = message.model_copy() if hasattr(message, 'model_copy') else message
        # Process only the content
        processed_message.content = process_message_content(message.content)
        processed_messages.append(processed_message)
    return processed_messages
