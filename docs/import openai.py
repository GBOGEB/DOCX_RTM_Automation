import openai

response = openai.Completion.create(
    model="text-davinci-003",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn.",
        },
    ],
    max_tokens=50,
)

print(response["choices"][0]["message"]["content"])
