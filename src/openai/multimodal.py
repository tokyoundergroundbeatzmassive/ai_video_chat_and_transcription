import base64
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_image_description(text, image_paths):
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
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [{"type": "text", "text": text}, *image_contents]},
        ],
        max_tokens=300,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content
