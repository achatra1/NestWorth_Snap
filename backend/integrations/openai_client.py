"""OpenAI API integration for AI summary generation."""
import logging
from openai import AsyncOpenAI
from backend.config import settings

logger = logging.getLogger(__name__)

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_chat_completion(
    messages: list[dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    Generate a chat completion using OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
        temperature: Sampling temperature (0-2, default: 0.7)
        max_tokens: Maximum tokens in response (default: 2000)
    
    Returns:
        Generated text response
    
    Raises:
        Exception: If API call fails
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("OpenAI API call failed")
        raise Exception(f"OpenAI API error: {str(e)}")


async def test_connection() -> bool:
    """
    Test OpenAI API connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        await generate_chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {e}")
        return False