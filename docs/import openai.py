from openai import OpenAI

# API key is read from the OPENAI_API_KEY environment variable by default
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Using a more current chat model
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a one-sentence bedtime story about a brave little robot.",
        },
    ],
    max_tokens=50,
)

print(response.choices[0].message.content)
