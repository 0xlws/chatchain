from llm.assistant import AIAssistant

# one shot / conversation
# short / med / long

assistant = AIAssistant()
assistant.run_cli(conversation=True, length="s")
