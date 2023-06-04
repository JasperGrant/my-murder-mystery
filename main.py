# My Murder Mystery CLI Game
# Written in 3 hours for lifelike hackathon
# 2023-06-03

import random
from lifelike import brain
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
import openai

# Load .env
load_dotenv()

# PUT OPENAI API KEY HERE:
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up large language model
llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Set up files for characters and conversations
characters = brain.Characters('json/characters.json')
conversations = brain.Conversations('json/conversations/json', characters, llm)

# Add player character
characters.add('Detective', '')

# Initialize list of characters and empty list of conversation contexts for each character
suspects = {}
convo_contexts = ["", "", ""]


# Function to get a chatgpt response
def ask_chatgpt(input_string):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": input_string}])['choices'][0]['message']['content']


# Context of mystery based on a prompt given to chatgpt
mystery_context = ask_chatgpt(
    "Write me a short hook (20-30 words) to a murder mystery with a random theme in second person. Please use short lines with lots of newlines. This "
    "mystery should have one murderer. Do not tell me who it is. Lots of '\n'. Make sure to say that I am the detective")


# Function for interrogation process
def interrogate_suspect(suspect):
    for questions in range(0, 2):
        # Prompt player
        print("What would you like to ask the suspect?")
        # If no conversation context for character
        if convo_contexts[suspect] == "":
            #Make new context and then convo
            convo_contexts[suspect] = suspects[suspect][
                                          0] + "This is what the detective told you from his perspective. You are not the detective and should take the following as a story beiing told to you. " + mystery_context + " You are being questioned as a suspect " + (
                                          'You want the detective to guess you are the murderer' if suspect == murderer else (
                                                      "You suspect that " + suspects[murderer][0] + "is the murderer"))
            conversations.new(convo_contexts[suspect], {suspects[suspect][0], 'Detective'})

        # Use lifelike to add to conversation
        conversations.append(convo_contexts[suspect], 'Detective', input())
        conversations.generate(convo_contexts[suspect], mystery_context, {'Detective'})
        print(conversations.get(convo_contexts[suspect])["log"][-1])


# Add murderer's confession to convo. For some reason the suspects will not confess
def murderer_confess(suspect):
    conversations.append(convo_contexts[suspect], 'Detective',
                         'You have been found out and are going to jail. How did you do it?')
    conversations.generate(convo_contexts[suspect], mystery_context, {'Detective'})
    print(conversations.get(convo_contexts[suspect])["log"][-1])


# User can choose a suspect from list of 3
# TODO: Error handling
def suspect_select():
    for j in range(0, 3):
        print(str(j) + '. ' + suspects[j][0])
    choice = input()
    while int(choice) not in [0, 1, 2]:
        choice = input()
    return int(choice)


# Main script
print("Welcome to My Murder Mystery")
print('\n')
print("Generating your mystery...")
print('\n\n\n')

print(mystery_context)
print('\n\n\n')
print("The suspects:")

# Choose murderer
murderer = random.randrange(3)

suspects[0] = ask_chatgpt(
    "Give me an interesting character from the above story in 10 words. Please use short lines with lots of "
    "newlines. Their name should be the first two words, and then their description shoould be after a : "
    "be scary. Do not forget the :" + (
        "They are the murderer but will try badly to hide it." if murderer == 0 else "")).split(':')
characters.add(suspects[0][0], suspects[0][1])
print(suspects[0][0] + '\nDescription:' + suspects[0][1] + '\n')

suspects[1] = ask_chatgpt(
    "Give me an another interesting character from the above story in 10 words. Please use short lines with lots of newlines. "
    "Their name should be the first two words, and then their description shoould be after a : "
    "They should be "
    "silly. Do not forget the :" + (
        "They are the murderer but will try badly to hide it" if murderer == 1 else "")).split(':')
characters.add(suspects[1][0], suspects[1][1])
print(suspects[1][0] + '\nDescription:' + suspects[1][1] + '\n')

suspects[2] = ask_chatgpt(
    "Give me an another interesting character from the above story in 10 words. Please use short lines with lots of newlines. "
    "Their name should be the first two words, and then their description shoould be after a : They should be "
    "weird. Do not forget the :" + (
        "They are the murderer but will try badly to hide it" if murderer == 2 else "")).split(':')
characters.add(suspects[2][0], suspects[2][1])
print(suspects[2][0] + '\nDescription:' + suspects[2][1] + '\n')

# Interrogation loop
for i in range(0, 3):
    print('\n\n\n')
    print("You will get three interrogations. You may ask two questions to each subject in each interrogation")
    print("Please select a suspect to interrogate")
    interrogate_suspect(suspect_select())

print("Interrogations are over. Who do you think is the murderer?")

# If player found murderer
if suspect_select() == murderer:
    print("Congratulations, you correctly guessed the murderer!")
else:
    print("Incorrect " + suspects[murderer][0] + " was the murderer")

# Confession from murderer
murderer_confess(murderer)
input()
exit()
