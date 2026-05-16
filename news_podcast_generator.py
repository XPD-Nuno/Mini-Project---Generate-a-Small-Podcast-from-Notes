

# 
# # Project Presentation
# 
# For my mini-project, I created a News Podcast Generator. The goal was to transform written news content into a short audio podcast.
# 
# The project starts by reading clean news content from a text file. Then I use the OpenAI ChatGPT API to transform that content into a podcast-style script. After that, the script is converted into an MP3 file using text-to-speech.
# 
# Finally, I created a Gradio interface so the user can paste news content, generate the podcast script, and listen to the audio directly from the app.
# 
# This project helped me practice API calls, environment variables, text processing, text-to-speech, and building a simple user interface with Gradio.

# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 



# CNN News Podcast Generator
#
# This project creates a simple news podcast generator.
# It reads news content, creates a podcast script using OpenAI,
# converts the script into audio, and shows everything in a Gradio app.
import time
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import os
import gradio as gr
# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Step Refactoring 1

@dataclass
class APIResponse:
    """Standardized API response."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    usage: Optional[Dict] = None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


# Step Refactoring 2

class OpenAIWrapper:
    """Wrapper for OpenAI API with error handling and retry logic."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini",
                 timeout: int = 30, max_retries: int = 3):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def _make_request(self, messages: List[Dict], **kwargs):
        """Make API request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    timeout=self.timeout,
                    **kwargs
                )
                return response
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
    
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> APIResponse:
        """Send a chat message and get a response."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self._make_request(messages)
            return APIResponse(
                success=True,
                data=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Request failed: {str(e)}'
            )
    
    def chat_with_history(self, messages: List[Dict]) -> APIResponse:
        """Send a multi-turn conversation."""
        try:
            response = self._make_request(messages)
            return APIResponse(
                success=True,
                data=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Request failed: {str(e)}'
            )
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


# Load environment variables

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully")
else:
    print("API key not found")


# Create OpenAI client

client = OpenAI(api_key=api_key)

 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Step Refactoring 2 - part 2

api_client = OpenAIWrapper(api_key=api_key)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# ## Read News Input File
# 
# This part reads the news text from `news_input.txt`.
# 
# The text is stored in `news_content`, so it can be used later to generate the podcast script with ChatGPT.
# 
# Flow:
# 
# `news_input.txt` → `news_content`


def read_news_input(file_path):
    """Read news content from a text file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            news_text = file.read()

        if not news_text.strip():
            return APIResponse(
                success=False,
                error=(
                    "ERROR in read_news_input(): File is empty.\n"
                    f"Location: {file_path}\n"
                    "Suggestion: Add news content to the file before running the app."
                )
            )

        return APIResponse(success=True, data=news_text)

    except FileNotFoundError:
        return APIResponse(
            success=False,
            error=(
                "ERROR in read_news_input(): FileNotFoundError\n"
                f"Location: File '{file_path}' was not found.\n"
                "Suggestion: Check that the file exists and the file path is correct."
            )
        )

    except PermissionError:
        return APIResponse(
            success=False,
            error=(
                "ERROR in read_news_input(): PermissionError\n"
                f"Location: File '{file_path}' could not be accessed.\n"
                "Suggestion: Check file permissions or close the file if it is open elsewhere."
            )
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=(
                "ERROR in read_news_input(): Unexpected error\n"
                f"Location: File '{file_path}'\n"
                f"Message: {str(e)}\n"
                "Suggestion: Check the file path and file content."
            )
        )

# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Step Refactoring 3

def validate_news_text(news_text: str) -> APIResponse:
    """Validate the news text before generating a podcast script."""
    if not news_text:
        return APIResponse(
            success=False,
            error="ERROR in validate_news_text(): No news text was provided."
        )

    cleaned_text = news_text.strip()

    if not cleaned_text:
        return APIResponse(
            success=False,
            error="ERROR in validate_news_text(): News text is empty or only contains spaces."
        )

    if len(cleaned_text) < 20:
        return APIResponse(
            success=False,
            error="ERROR in validate_news_text(): News text is too short. Please provide more content."
        )

    return APIResponse(success=True, data=cleaned_text)


def create_podcast_prompt(news_text: str) -> str:
    """Create the prompt used to generate the podcast script."""
    return f"""
You are a podcast script writer.

Create a short news podcast script based on the news content below.

Requirements:
- Use clear and simple English
- Do not copy the original text word-for-word
- Make it sound natural for audio
- Include a short intro
- Include the main story
- Include a short closing sentence
- Keep it around 1 to 2 minutes long

News content:
{news_text}
"""



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# ## Generate Podcast Script
# 
# This part sends the news content to ChatGPT.
# 
# ChatGPT receives instructions to turn the news text into a short podcast-style script.
# 
# The final script is saved in `podcast_script` and used later to create the audio file.


def generate_podcast_script(news_text):
    validation_result = validate_news_text(news_text)

    if not validation_result.success:
        return validation_result.error

    prompt = create_podcast_prompt(validation_result.data)

    result = api_client.chat(
        prompt=prompt,
        system_prompt="You create short and clear podcast scripts."
    )

    if result.success:
        return result.data
    else:
        return result.error

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Step Refactoring 4

def validate_script_text(script_text: str) -> APIResponse:
    """Validate the podcast script before generating audio."""
    if not script_text:
        return APIResponse(
            success=False,
            error="ERROR in validate_script_text(): No podcast script was provided."
        )

    cleaned_script = script_text.strip()

    if not cleaned_script:
        return APIResponse(
            success=False,
            error="ERROR in validate_script_text(): Podcast script is empty or only contains spaces."
        )

    if cleaned_script.startswith("ERROR in") or cleaned_script.startswith("Request failed"):
        return APIResponse(
            success=False,
            error="ERROR in validate_script_text(): Cannot generate audio because the podcast script contains an error."
        )

    return APIResponse(success=True, data=cleaned_script)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# ## Generate Podcast Audio
# 
# This part turns the podcast script into an MP3 audio file.
# 
# The script is sent to OpenAI text-to-speech, which creates the file `podcast.mp3`.
# 
# This audio file can then be played in the notebook or through the Gradio interface.


def generate_audio(script_text, output_file="podcast.mp3"):
    validation_result = validate_script_text(script_text)

    if not validation_result.success:
        return validation_result

    try:
        with api_client.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=validation_result.data
        ) as response:
            response.stream_to_file(output_file)

        return APIResponse(success=True, data=output_file)

    except Exception as e:
        return APIResponse(
            success=False,
            error=(
                "ERROR in generate_audio(): Audio generation failed.\n"
                f"Message: {str(e)}\n"
                "Suggestion: Check the OpenAI API key, internet connection, text-to-speech model, and input text."
            )
        )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Aggregating All Functions

#This part connects the project steps into one function.

#It takes the news text, creates the podcast script, creates the audio file, and sends both results back to the Gradio app.

#This is important because Gradio needs one main function to run when the user clicks submit.

#Flow:

#User text → podcast script → audio file → Gradio output



# 
# ## Create Gradio Web App
# 
# This part creates the final web interface using Gradio.
# 
# The user pastes news content into a text box, clicks submit, and the app generates both a podcast script and an audio file.
# 
# The script is shown on screen, and the audio can be played directly in the app.


def create_podcast_app(news_text):
    podcast_script = generate_podcast_script(news_text)

    if podcast_script.startswith("ERROR in") or podcast_script.startswith("Request failed"):
        return podcast_script, gr.update(value=None)

    audio_result = generate_audio(podcast_script)

    if not audio_result.success:
        return audio_result.error, gr.update(value=None)

    return podcast_script, audio_result.data


interface = gr.Interface(
    fn=create_podcast_app,
    inputs=gr.Textbox(
        label="Paste news content here",
        lines=10,
        placeholder="Paste a news title and summary here..."
    ),
    outputs=[
        gr.Textbox(label="Generated Podcast Script", lines=15),
        gr.Audio(label="Generated Podcast Audio")
    ],
    title="News Podcast Generator",
    description="Paste news content and generate a short podcast script with audio."
)

interface.launch()


