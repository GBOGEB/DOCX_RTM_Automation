import openai
import os


def get_openai_response(prompt_message):
    """
    Sends a prompt to OpenAI's ChatCompletion API and returns the response.

    Ensure the OPENAI_API_KEY environment variable is set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY environment variable not set."

    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_message},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An API error occurred: {e}"


if __name__ == "__main__":
    # Example usage:
    user_prompt = "Write a one-sentence bedtime story about a brave little robot exploring a new planet."

    print(f'Sending prompt to OpenAI: "{user_prompt}"')
    story = get_openai_response(user_prompt)
    print("\nOpenAI's Response:")
    print(story)

    # To run this script:
    # 1. Make sure you have the openai Python package installed: pip install openai
    # 2. Set your OpenAI API key as an environment variable:
    #    export OPENAI_API_KEY='your_actual_api_key'
    #    (on Windows, use: set OPENAI_API_KEY=your_actual_api_key)
    # 3. Execute the script: python openai_example.py
