import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Write a one-sentence bedtime story about a unicorn."}
    ]
)

print(response['choices'][0]['message']['content'])