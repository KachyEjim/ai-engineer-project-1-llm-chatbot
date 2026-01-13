import time
import openai
from openai import OpenAI
from .config import GEMINI_API_KEY, OPENAI_API_KEY, GEMINI_MODEL, OPENAI_MODEL, RESERVED_OUTPUT_TOKENS
import openai
def create_chat_completion(messages: list[dict[str, str]], *, model: str, temperature: float, max_tokens: int) -> tuple[str, int | None, int | None]:
	"""
	Robust OpenAI chat completion with error handling and retries.
	Returns (assistant_text, prompt_tokens, completion_tokens)
	"""
	api_key = OPENAI_API_KEY
	if not api_key:
		print("[ERROR] OPENAI_API_KEY not set. Please add it to your .env file.")
		return "", None, None
	client = OpenAI(api_key=api_key)
	retries = 5
	backoff = 1
	for attempt in range(1, retries + 1):
		try:
			from openai.types.chat import (
				ChatCompletionSystemMessageParam,
				ChatCompletionUserMessageParam,
				ChatCompletionAssistantMessageParam,
			)
			def to_openai_message(msg):
				if msg["role"] == "system":
					return ChatCompletionSystemMessageParam(role="system", content=msg["content"])
				elif msg["role"] == "user":
					return ChatCompletionUserMessageParam(role="user", content=msg["content"])
				elif msg["role"] == "assistant":
					return ChatCompletionAssistantMessageParam(role="assistant", content=msg["content"])
				else:
					raise ValueError(f"Unknown role: {msg['role']}")
			openai_messages = [to_openai_message(m) for m in messages]
			completion = client.chat.completions.create(
				model=model,
				messages=openai_messages,
				temperature=temperature,
				max_tokens=max_tokens,
			)
			assistant_text = completion.choices[0].message.content or ""
			if hasattr(completion, "usage") and completion.usage is not None:
				prompt_tokens = completion.usage.prompt_tokens
				completion_tokens = completion.usage.completion_tokens
			else:
				from .tokens import count_tokens
				prompt_tokens = count_tokens(messages, model)
				completion_tokens = count_tokens([
					{"role": "assistant", "content": assistant_text}
				], model)
			return assistant_text, prompt_tokens, completion_tokens
		except openai.error.AuthenticationError: # type: ignore
			print("[ERROR] Invalid or missing OpenAI API key. Please set OPENAI_API_KEY in your .env file.")
			return "", None, None
		except openai.error.RateLimitError: # type: ignore
			if attempt < retries:
				print(f"[Rate Limit] Retrying in {backoff}s... ({retries - attempt} retries left)")
				time.sleep(backoff)
				backoff *= 2
			else:
				print("[ERROR] Rate limit exceeded. Please try again later.")
				return "", None, None
		except (openai.error.Timeout, openai.error.APIConnectionError, openai.error.ServiceUnavailableError, openai.error.APIError) as e: # pyright: ignore[reportAttributeAccessIssue]
			if attempt < retries:
				print(f"[Network/API Error] {e}. Retrying in {backoff}s... ({retries - attempt} retries left)")
				time.sleep(backoff)
				backoff *= 2
			else:
				print("[ERROR] Network or API error. Please check your connection and try again later.")
				return "", None, None
		except Exception as e:
			print(f"[ERROR] Unexpected error: {e}")
			return "", None, None
	return "", None, None





def get_llm_client():
	"""
	Detect available API keys and return the appropriate client.
	Priority: Gemini (default for our testing), fallback to OpenAI if only OpenAI key exists.
	"""
	gemini_key = GEMINI_API_KEY
	openai_key = OPENAI_API_KEY
    
	if gemini_key:
		try:
			from google import genai
			from google.genai import types
			client = genai.Client(api_key=gemini_key)
			model = GEMINI_MODEL
			return "gemini", client, model
		except ImportError:
			print("Warning: google-genai not installed. Install with: pip install google-genai")
			if not openai_key:
				raise
	if openai_key:
		try:
			from openai import OpenAI
			client = OpenAI(api_key=openai_key)
			model = OPENAI_MODEL
			return "openai", client, model
		except ImportError:
			print("Warning: openai not installed. Install with: pip install openai")
			raise
	raise ValueError(
		"No API key found. Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
	)

def call_openai(client, model: str, messages: list[dict[str, str]]) -> tuple[str, int, int]:
	"""Call OpenAI API and return the assistant's response, prompt tokens, and completion tokens."""
	completion = client.chat.completions.create(
		model=model,
		messages=messages,
		max_tokens=RESERVED_OUTPUT_TOKENS,
	)
	assistant_text = completion.choices[0].message.content or ""
	if hasattr(completion, "usage") and completion.usage is not None:
		prompt_tokens = completion.usage.prompt_tokens
		completion_tokens = completion.usage.completion_tokens
	else:
		from .tokens import count_tokens
		prompt_tokens = count_tokens(messages, model)
		completion_tokens = count_tokens([
			{"role": "assistant", "content": assistant_text}
		], model)
	return assistant_text, prompt_tokens, completion_tokens

def call_gemini(client, model: str, messages: list[dict[str, str]]) -> tuple[str, int, int]:
	"""Call Gemini API and return the assistant's response, prompt tokens, and completion tokens."""
	conversation_history = []
	for msg in messages:
		conversation_history.append({
			"role": msg["role"],
			"content": msg["content"]
		})
	interaction = client.interactions.create(
		model=model,
		input=conversation_history,
		generation_config={
			"max_output_tokens": RESERVED_OUTPUT_TOKENS
		}
	)
	outputs = getattr(interaction, "outputs", [])
	assistant_text = ""
	for output in outputs:
		if hasattr(output, "text"):
			assistant_text = output.text
	from .tokens import count_tokens
	prompt_tokens = count_tokens(messages, model)
	completion_tokens = count_tokens([
		{"role": "assistant", "content": assistant_text}
	], model)
	return assistant_text, prompt_tokens, completion_tokens
