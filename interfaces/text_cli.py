from abc import ABC, abstractmethod
import os
import sys
import asyncio

from plugins.config.config_env import OPENAI_API_KEY


class GPTCLI(ABC):
    settings = ""

    def run_cli(self, conversation=False, length="s"):
        system_message = ""
        if length == "s":
            system_message = (
                "Answer as short as humanly possible unless requested otherwise."
            )

        if length == "m":
            system_message = "You will aim to provide concise, clear, and sufficiently detailed answers to questions."
        if length == "l":
            system_message = "Please provide the most thorough and comprehensive answer possible, including all relevant details and examples."

        self.clear_terminal()
        # Display help message for available commands
        print("Type your message or use the following commands:")
        print("/help - to display this help message")
        print("/q - to exit the CLI")

        print()

        self.cli_active = True

        if conversation:
            # TODO add conversation function
            pass

        while self.cli_active:
            # print(f"\nCurrent settings: {self.get_settings()}\n")

            user_input = input(">> ")
            if user_input.startswith("/"):
                self.process_command(user_input)
            else:
                response = asyncio.run(
                    self.get_response(user_input, system_role=system_message)
                )
                print(response[0])

    def clear_terminal(self):
        # Clear the terminal
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")

    def process_command(self, command):
        if command == "/q":
            self.cli_active = False
        elif command.startswith("/set"):
            # Update settings
            pass
        elif command == "/help":
            self.display_help()

    @abstractmethod
    async def response(self, user_input, **kwargs):
        pass

    async def get_response(self, user_input, **kwargs):
        if not OPENAI_API_KEY:
            return print("'OPENAI_API_KEY' not set.")
        response = await self.response(user_input, **kwargs)
        return response

    def get_settings(self):
        return self.settings

    def display_help(self):
        print()
        print("Available commands:")
        print("/help - to display this help message")
        print("/q - to exit the CLI")
        print("/set <option> - to modify settings")
        print()
