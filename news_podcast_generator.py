

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

from openai import OpenAI
from dotenv import load_dotenv
import os
import gradio as gr
# 
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
    with open(file_path, "r", encoding="utf-8") as file:
        news_text = file.read()
    return news_text

# 
# ## Generate Podcast Script
# 
# This part sends the news content to ChatGPT.
# 
# ChatGPT receives instructions to turn the news text into a short podcast-style script.
# 
# The final script is saved in `podcast_script` and used later to create the audio file.


def generate_podcast_script(news_text):
    prompt = f"""
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You create short and clear podcast scripts."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# ## Generate Podcast Audio
# 
# This part turns the podcast script into an MP3 audio file.
# 
# The script is sent to OpenAI text-to-speech, which creates the file `podcast.mp3`.
# 
# This audio file can then be played in the notebook or through the Gradio interface.


def generate_audio(script_text, output_file="podcast.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=script_text
    )

    response.stream_to_file(output_file)

    return output_file


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
    audio_file = generate_audio(podcast_script)

    return podcast_script, audio_file



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


