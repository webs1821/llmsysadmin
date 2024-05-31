# Copyright (C) 2024 Konrad k13.pl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#Google related imports:
import google.generativeai as genai
import PIL.Image

#OpenAI related imports:
import base64
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat


system_instruction = ""

def question(prompt: str, engine: str, image: str = None) -> str | None:
    """
    Generate a response based on the prompt using the specified engine.

    :param prompt: The prompt to generate a response for.
    :param engine: The engine to use ('openai' or 'google').
    :param image: Optional image file path.
    :return: The generated response as a string or None if an error occurs.
    """
    if engine == "openai":
        return openai(prompt, image)
    elif engine == "google":
        return google(prompt, image)
    else:
        return None

def openai(prompt: str, image: str = None) -> str | None:
    """
    Generate a response using OpenAI's API.

    :param prompt: The prompt to generate a response for.
    :param image: Optional image file path.
    :return: The generated response as a string or None if an error occurs.
    """
    api_key = "sk-proj-xxx"
    client = OpenAI(api_key = api_key)
    if image is not None:
        try:
            with open(image, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            prompt = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        except Exception as e:
            print(f"An error occurred while opening the image: {e}")
            return None

    response = client.chat.completions.create(
        model="gpt-4o",
        # response_format=ResponseFormat(type="json_object"),
        temperature=0.4,
        n=1,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def google(prompt: str, image: str = None) -> str | None:
    """
    Generate a response using Google's Generative AI API.

    :param prompt: The prompt to generate a response for.
    :param image: Optional image file path.
    :return: The generated response as a string or None if an error occurs.
    """
    api_key = "xxx"
    genai.configure(api_key=api_key)
    system_instruction_local = system_instruction + " Do not use Markdown."
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction_local)
    generation_config=genai.types.GenerationConfig(
        candidate_count=1,
        temperature=0.4)
    if image is None:
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    else:
        try:
            img = PIL.Image.open(image)
            response = model.generate_content([prompt, img], generation_config=generation_config)
            return response.text
        except Exception as e:
            print(f"An error occurred while opening the image: {e}")
            return None
