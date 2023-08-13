import os
import json
import openai
import time
from time import time, sleep

with open('key_openai.txt', 'r', encoding='utf-8') as file:
    openai.api_key = file.read().strip()


# Function for generating a reply form the OpenAi Api
def chatgpt_completion(query):
    max_counter = 7
    counter = 0
    while True:
        try:
            completion = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              max_tokens=800,
              temperature=0.5,
              messages=query
            )
            response = (completion.choices[0].message.content)
            return response
        except Exception as e:
            counter +=1
            if counter >= max_counter:
                print(f"Exiting with error: {e}")
                exit()
            print(f"Retrying with error: {e} in 20 seconds...")
            sleep(20)
        
        
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
        
    
# Custom Conversation History List, this was done so the api can be swapped without major code rewrites.
class MainConversation:
    def __init__(self, max_entries, prompt, greeting):
        try:
            # Set Maximum conversation Length
            self.max_entries = max_entries
            # Set path for Conversation History
            self.file_path = f'./main_conversation_history.json'
            # Set Main Conversatoin with Main and Greeting Prompt
            self.main_conversation = [prompt, greeting]
            # Load existing conversation from file or set to empty.
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.running_conversation = data.get('running_conversation', [])
            else:
                self.running_conversation = []
        except Exception as e:
            print(e)

    def append(self, usernameupper, user_input, botnameupper, output):
        # Append new entry to the running conversation
        entry = []
        entry.append(f"{usernameupper}: {user_input}")
        entry.append(f"{botnameupper}: {output}")
        self.running_conversation.append("\n\n".join(entry))  # Join the entry with "\n\n"
        # Remove oldest entry if conversation length exceeds max entries
        while len(self.running_conversation) > self.max_entries:
            self.running_conversation.pop(0)
        self.save_to_file()

    def save_to_file(self):
        # Combine main conversation and formatted running conversation for saving to file
        data_to_save = {
            'main_conversation': self.main_conversation,
            'running_conversation': self.running_conversation
        }
        
        # Save the joined list to a json file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

    # Create function to call conversation history
    def get_conversation_history(self):
        if not os.path.exists(self.file_path):
            self.save_to_file()
        # Join Main Conversation and Running Conversation
        return self.main_conversation + ["\n\n".join(entry.split(" ")) for entry in self.running_conversation]
            

# Start the main chatbot loop
if __name__ == '__main__':
    # Create a conversation list for the chatbot prompts.
    conversation = list()
    # Define User and Bot name from .txt files in the Prompts folder
    bot_name = open_file('./Prompts/bot_name.txt')
    user_name = open_file('./Prompts/user_name.txt')
    # Create variables for upper case bot and username
    usernameupper = user_name.upper()
    botnameupper = bot_name.upper()
    # Define Main Prompt and Greeting Prompt from .txt files in the Prompts folder
    main_prompt = open_file(f'./Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
    greeting_prompt = open_file(f'./Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
    # Define Maximum Conversation List
    max_entries = 12
    # Define the main conversation class and pass through the needed variables
    main_conversation = MainConversation(max_entries, main_prompt, greeting_prompt)
    while True:
        # Wrap in an error handler
        try:
            # Get Conversation History
            conversation_history = main_conversation.get_conversation_history()
            # Get user input
            user_input = input(f'\n\n{usernameupper}: ')
            # Append generation list with the conversation history.  System prompt and greeting are at the beginning.
            conversation.append({'role': 'system', 'content': f"{conversation_history}\n"})
            # Append generation list with the user input
            conversation.append({'role': 'user', 'content': user_input})
            # Pass through the conversation list to the OpenAi function
            output = chatgpt_completion(conversation)
            # Print the response
            print(f"\n\n{botnameupper}: {output}")
            # Append json file with newest response
            main_conversation.append(usernameupper, user_input, botnameupper, output)
            # Clear Generation List 
            conversation.clear()
        except Exception as e:
            print(e)