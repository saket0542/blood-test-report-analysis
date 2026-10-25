import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Groq client. It automatically looks for GROQ_API_KEY.
client = Groq()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a highly concise assistant. You must answer every question in exactly one short sentence. No lists, no paragraphs."
        },
        {
            "role": "user",
            "content": "how many planets we have in our solar system",
        }
    ],

    # The language model which will generate the completion.
    model="openai/gpt-oss-120b"
)

# Print the completion returned by the LLM.
print(chat_completion.choices[0].message.content)