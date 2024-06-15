import os
import base64
import requests
import json
from io import BytesIO
from typing import List, Optional

from openai import OpenAI
from fastapi import UploadFile, HTTPException

from exceptions import NoMessageException, UnprocessableMessageException
from llm_functions import function_schemas, call_function
from dependencies import db_dependency, user_dependency
from models import Message
from enums import MessageType


client = OpenAI()


# System messages do not count towards the limit:
def get_messages(db: db_dependency, user: user_dependency, limit: int = 20) -> List[Message]:
    system_messages = get_system_messages(db, user)
    user_messages = get_user_messages(db, user, limit)
    return system_messages + user_messages


# Returns messages between a specific user and the assistant:
def get_user_messages(db: db_dependency, user: user_dependency, limit: int = 20) -> List[Message]:
    # Combining desc and then reversing the order may seem redundant, 
    # but this way we get only the last X messages, with the oldest message appearing first:
    return db.query(Message).filter_by(user_id=user.id).order_by(Message.timestamp.desc()).limit(limit).all()[::-1]


def get_system_messages(db: db_dependency, user: user_dependency) -> List[Message]:
    return db.query(Message).filter(
        (Message.type == MessageType.SYSTEM) & ((Message.user_id == None) | (Message.user_id == user.id))
        ).order_by(Message.timestamp.asc()).all()


def format_messages(messages: List[Message], user: user_dependency) -> List[str]:
    # Need to use the string value of the enum to avoid issues with JSON serialization:
    formatted_messages = []
    for message in messages:
        if message.type == MessageType.USER: text = f"{user.name}'s Prompt: {message.text}"
        else: text = message.text

        formatted_messages.append({"role": message.type.value, "content": [{"type": "text", "text": text}]})
    
    return formatted_messages


def add_message(db: db_dependency, user: user_dependency, type: MessageType, text: str) -> Message:
    new_message = Message(user_id=user.id, type=type, text=text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def delete_messages(db: db_dependency, user: user_dependency) -> None:
    messages = db.query(Message).filter((Message.user_id == user.id) & ((Message.type == MessageType.USER) | (Message.type == MessageType.ASSISTANT))).all()
    for message in messages: db.delete(message)
    db.commit()


def speech_to_text(audio_bytes: bytes, file_name: str) -> str:
    audio_file = BytesIO(audio_bytes)
    audio_file.name = file_name
    return client.audio.transcriptions.create(model="whisper-1", file=audio_file).text


def text_to_speech(text: str) -> bytes: 
    return client.audio.speech.create(model="tts-1", voice="alloy", input=text).content


async def completion(db: db_dependency, user: user_dependency, text: Optional[str],
    audio: Optional[UploadFile], image: Optional[UploadFile], generate_audio=False, save_messages=True) -> dict: 

    try:
        # If at least one type of input is not provided, raising an exception:
        if not any([text, audio, image]):
            raise NoMessageException

        transcription = None
        if audio:
            # Reading the audio and converting to text:
            audio_bytes = await audio.read()
            transcription = speech_to_text(audio_bytes, audio.filename)
            await audio.close()


        encoded_image = None
        if image:
            # Reading and encoding the image file:
            image_content = await image.read()
            encoded_image = base64.b64encode(image_content).decode("utf-8")
            await image.close()

        # Concatenating user's text and audio prompts:
        user_text = f"{text or ''} {transcription or ''}".strip()

        if save_messages:
            # Adding the user's message to the DB:
            add_message(db, user, MessageType.USER, user_text)

            # Getting all the messages associated to that user:
            messages = get_messages(db, user)

        else:
            messages = get_system_messages(db, user)

        # Sending the completion request to the API:
        completion_text = send_completion_request(user, messages, encoded_image)

        if save_messages:
            # Adding the assistant response to the db:
            add_message(db, user, MessageType.ASSISTANT, completion_text)

        encoded_audio = None
        if generate_audio:
            # Converting the response text to audio:
            audio_bytes = text_to_speech(completion_text)
            encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")

        # Need to use the string value of the enum to avoid issues with JSON serialization:
        return {"type": MessageType.ASSISTANT.value, "text": completion_text,  "encoded_audio": encoded_audio}

    except HTTPException as h:
        # Raising HTTP Exceptions again without modification:
        raise h
    
    except Exception as e:
        print(f"Error during completion: {e}")
        raise UnprocessableMessageException from e
        

def send_completion_request(user: user_dependency, messages: dict, encoded_image: str = None, formatted: bool = False, max_tokens: int = 300) -> str:
    # Ensuring the messages are in the correct format for the API:
    if formatted: formatted_messages = messages
    else: formatted_messages = format_messages(messages, user)

    print(f"\n\nFormatted Messages:\n{formatted_messages}\n\n")

    if encoded_image is not None: 
        # If there is an image, adding it to the user's last message (all past images excluded due to context window limits):
        # (There will always be a content field due to the formatting method.)
        formatted_messages[-1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}})
        
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    payload = {"model": "gpt-4o", "messages": formatted_messages, "max_tokens": max_tokens, "tools": function_schemas, "tool_choice": "auto"}

    # Sending the completion request:
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Extracting the response content:
    response_data = response.json()

    # Need to obtain values from dict (rather than attributes) since we are using requests instead of SDK:
    response_message = response_data["choices"][0]["message"]
    formatted_messages.append(response_message)

    function_calls = response_message.get("tool_calls")
    if function_calls is not None:

        for function_call in function_calls:
            function_name = function_call["function"]["name"]
            function_args = json.loads(function_call["function"]["arguments"])

            # Calling the function:
            function_result = call_function(function_name, args=function_args)

            # Adding the result to the messages:
            formatted_messages.append(
                {
                    "tool_call_id": function_call["id"], 
                    "role": "tool",
                    "name": function_name,
                    "content": function_result,
                }
            )

        # Sending the completion request again with the new messages:
        return send_completion_request(user, formatted_messages, formatted=True)

    response_text = response_message["content"]

    return response_text