import json
import os
from typing import List, Dict

import toml
from openai import OpenAI

CONFIG = toml.load("config.toml")
PROMPTS = json.load(open("src/prompts.json"))


class OpenAIGenerator:
    def __init__(self):
        """
        Initialize the OpenAI client.
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response from the OpenAI chat model.

        Args:
            client (OpenAI): client for the OpenAI API
            messages (List[Dict[str, str]]): list of messages to send to the model

        Returns:
            str: response from the model
        """

        resp = self.client.chat.completions.create(
            model=CONFIG["GENERATION_MODEL"],
            messages=messages,
        )

        return resp.choices[0].message.content

    def generate_search_query(self, query: str, chat_history: str) -> str:
        """
        Generate a search query from the given query and chat history.

        Args:
            query (str): the user's latest query that will be rephrased
            chat_history (str): the chat history

        Returns:
            str: the generated search query
        """
        sys_prompt = PROMPTS["system_prompt"]
        search_prompt = PROMPTS["search_prompt"].format(
            chat_history=chat_history, question=query
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": search_prompt},
        ]
        response = self.chat_completion(messages=messages)
        return response

    def generate_chat_response(
        self, query: str, chat_history: str, context: str
    ) -> str:
        """
        Generate a response to a chat query.

        Args:
            query (str): the query to respond to
            chat_history (str): the chat history

        Returns:
            str: the response to the query
        """
        sys_prompt = PROMPTS["system_prompt"]
        chat_prompt = PROMPTS["chat_prompt"].format(
            chat_history=chat_history, question=query, context=context
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": chat_prompt},
        ]
        response = self.chat_completion(messages=messages)
        return response
