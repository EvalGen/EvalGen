from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"

__client = None


def __get_client():
    global __client

    if not __client:
        __client = OpenAI()

    return __client


def invoke(messages: list):
    client = __get_client()

    response = client.chat.completions.create(
        messages=messages,
        model=DEFAULT_MODEL,
    )

    return response.choices[0].message.content
