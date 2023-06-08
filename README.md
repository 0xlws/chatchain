# ChatChain: AI Chatbot Assistant for Discord and Telegram

ChatChain is an AI-powered chatbot assistant designed to provide a variety of useful functionalities while integrating smoothly with the Discord and Telegram platforms. Driven by the latest advancements in natural language processing, ChatChain can understand and respond to user prompts effectively, offering valuable support and assistance in various tasks. Additionally, ChatChain stores all requests and responses for every user in separate files, allowing users to keep track of their conversation history.

## Overview

The project consists of the following main components:

1. **AIAssistant:** A class that leverages AI models such as ChatGPT(3.5, 4) to generate text-based responses to user inputs. The AIAssistant focuses on providing valuable information and assistance in a wide range of topics.

2. **Discord Interface:** Integration with the Discord platform that enables ChatChain to function as a Discord bot and seamlessly interact with users.

3. **Telegram Interface:** Integration with the Telegram platform that enables ChatChain to function as a Telegram bot and seamlessly interact with users.

4. **CLI Interface:** A separate Command Line Interface for interacting with ChatChain directly. This alternative method allows users to easily test, develop, and communicate from the command line.

The name "ChatChain" reflects the project's interconnected nature, signifying a chain of conversations that can span a variety of topics and user requests. The project's goal is to develop a dynamic, adaptive, and versatile chatbot assistant capable of handling an array of tasks, from providing code snippets to answering various questions.

## Installation

Clone the ChatChain repository and navigate to the project folder:

```bash
git clone https://github.com/0xlws/chatchain.git
cd chatchain
```

Set up and activate a Python virtual environment, and then install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

**Alternative:** Use the provided `launch.sh` script from the GitHub repository to run ChatChain seamlessly. The script will handle activating the virtual environment and installing the required dependencies.
To run ChatChain, simply execute the launch.sh script:

```bash
./launch.sh
```

## Configuration

Ensure that all API keys (e.g., OpenAI API key for ChatGPT, Discord bot token, Telegram bot token, and any additional API keys) have been properly configured in the project settings. Remember to set your OpenAI API key, as the chatbot relies on it to function correctly.

## Usage

ChatChain is designed to support ChatGPT and other AI models. It can be easily adapted to utilize alternative models, making it a flexible and versatile chatbot assistant.

### Running ChatChain as a Discord Bot

Ensure your Discord bot token is properly configured in the project settings. Once the bot is running, it will be online on your Discord server and ready to receive commands from users in the text channels.

### Running ChatChain as a Telegram Bot

Ensure your Telegram bot token is properly configured in the project settings. Once the bot is running, it will be online on your Telegram chat and ready to receive commands from users.

### Running ChatChain in CLI mode

To run ChatChain as a Command Line Interface, execute the following command in the root directory of the project:

```bash
python3 cli.py
```

This will launch a simple command-line interface for ChatChain. You can then enter commands and chat directly with the AI Chatbot Assistant, which will respond to your inputs using its AI model.

In all modes, ChatChain will process your commands and inputs and return appropriate responses based on the text input. It is tailored to provide valuable support and assistance in various tasks, whether it's fetching code snippets, answering questions, or delivering relevant information. As the project evolves, its capabilities will be further refined to facilitate longer conversations and handle a broader range of requests.
