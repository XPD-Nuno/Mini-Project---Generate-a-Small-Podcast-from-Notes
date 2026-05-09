# News Podcast Generator

## Project Overview

This mini-project creates a simple podcast generator from news content.

The user provides a short news title and summary. The app sends this content to the OpenAI ChatGPT API, generates a short podcast-style script, and then converts the script into an audio file using text-to-speech.

The project also includes a simple Gradio interface where the user can paste news content, generate the podcast script, and listen to the generated audio.

## Main Workflow

1. Read news content from `news_input.txt`
2. Send the news content to the ChatGPT API
3. Generate a short podcast script
4. Convert the script into an audio file
5. Display the script and audio in a Gradio interface

## Technologies Used

- Python
- OpenAI API
- Text-to-Speech
- Gradio
- python-dotenv
- Jupyter Notebook

## Project Files

- `news_podcast_generator.ipynb` - main notebook with the project code
- `news_input.txt` - sample news input used by the project
- `requirements.txt` - list of required Python packages
- `.env` - stores the OpenAI API key
- `.gitignore` - prevents sensitive files from being uploaded
- `podcast.mp3` - generated podcast audio file

## Setup Instructions

Install the required packages:

```bash
pip install -r requirements.txt


Create a `.env` file, if it does not already exist, and add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here

```markdown
Run the notebook cells in order.