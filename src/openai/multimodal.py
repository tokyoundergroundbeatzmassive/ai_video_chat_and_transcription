import base64
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ユーザーごとのメッセージ履歴を保持する辞書
user_messages = {}

def get_user_messages(user_id: str):
    if user_id not in user_messages:
        user_messages[user_id] = []
    return user_messages[user_id]

def get_image_description(text: str, image_paths: list[str], user_id: str):
    messages = get_user_messages(user_id)
    image_contents = []
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            image_contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/webp;base64,{encoded_image}"
                }
            })

    system_prompt = "Your text will be spoken by tts, so keep your response short and concise."
    # Add system message only once
    if not any(msg['role'] == 'system' for msg in messages):
        messages.append({"role": "system", "content": system_prompt})

    # Create a copy of messages for API request
    api_messages = messages + [{"role": "user", "content": [{"type": "text", "text": text}, *image_contents]}]
    # print(f"api_messages: {api_messages}")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=api_messages,
        max_tokens=300,
    )
    assistant_response = response.choices[0].message.content
    messages.append({"role": "user", "content": text})
    messages.append({"role": "assistant", "content": assistant_response})

    # Ensure the messages list does not exceed 21 items
    while len(messages) > 11:
        messages.pop(1)

    print(f"messages: {messages}")
    return assistant_response
