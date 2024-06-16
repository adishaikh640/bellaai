import speech_recognition as sr
import requests
import pyttsx3
import webbrowser
import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Setting Microsoft Zira as the default voice
voices = engine.getProperty('voices')
for voice in voices:
    if "zira" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Load the model and tokenizer
model_name = "microsoft/DialoGPT-medium"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.add_special_tokens({'pad_token': '[PAD]'})

# Function to get response from chatbot
def get_chat_response(prompt):
    try:
        # Tokenize input text
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, padding=True, truncation=True)

        # Generate response
        response = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            pad_token_id=tokenizer.pad_token_id,
            max_length=150,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.9
        )

        # Decode response
        response_text = tokenizer.decode(response[0], skip_special_tokens=True)
        return response_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to get current weather for a city
def get_weather(city):
    try:
        api_key = '5adae566d664aaf4ba7d24ae7d4877d6'  # Replace with your OpenWeatherMap API key
        weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}")
        if weather_data.status_code == 200:
            weather = weather_data.json()['weather'][0]['description']
            temperature = weather_data.json()['main']['temp']
            return f"The weather in {city} is {weather}. The temperature is {temperature}°C."
        else:
            return "Failed to fetch weather data."
    except Exception as e:
        print(f"An error occurred while fetching weather data: {e}")
        return "Failed to fetch weather data."

# Function to listen for instructions
def listen_for_instruction():
    try:
        with sr.Microphone() as source:
            print("Listening...") 
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            instruction = recognizer.recognize_google(audio)
            print(f"Instruction: {instruction}")
            return instruction
    except sr.RequestError:
        # Network error
        print("Network error, please try again.")
        return None
    except sr.UnknownValueError:
        # Speech not understood
        print("Speech not understood, please try again.")
        return None
    except Exception as e:
        print(f"Error capturing instruction: {e}")
        return None

# Function to handle manual input
def manual_input():
    instruction = input('Enter your command: ')
    if instruction.strip():
        return instruction
    else:
        print("Invalid command. Please try again.")
        return None

# Function to handle voice commands
def bella():
    while True:
        instruction = listen_for_instruction()
        if instruction:
            if "stop" in instruction:
                break
            elif "weather" in instruction:
                city = input("Enter the city: ")
                response = get_weather(city)
            elif "time" in instruction:
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                response = f"The current time is {current_time}."
            elif "date" in instruction:
                current_date = datetime.datetime.now().strftime('%d/%m/%Y')
                response = f"Today's date is {current_date}."
            elif "play" in instruction:
                video_query = instruction.replace("play", "").strip()
                search_url = f"https://www.youtube.com/results?search_query={video_query}"
                webbrowser.open(search_url)
                response = f"Playing {video_query} on YouTube."
            else:
                response = get_chat_response(instruction)

            if response:
                print("Bella:", response)
                engine.say(response)
                engine.runAndWait()
            else:
                print("Failed to get a response.")

        else:
            manual_instruction = manual_input()
            if manual_instruction:
                if "stop" in manual_instruction:
                    break
                elif "weather" in manual_instruction:
                    city = input("Enter the city: ")
                    response = get_weather(city)
                elif "time" in manual_instruction:
                    current_time = datetime.datetime.now().strftime('%I:%M %p')
                    response = f"The current time is {current_time}."
                elif "date" in manual_instruction:
                    current_date = datetime.datetime.now().strftime('%d/%m/%Y')
                    response = f"Today's date is {current_date}."
                elif "play" in manual_instruction:
                    video_query = manual_instruction.replace("play", "").strip()
                    search_url = f"https://www.youtube.com/results?search_query={video_query}"
                    webbrowser.open(search_url)
                    response = f"Playing {video_query} on YouTube."

                if response:
                    print("Bella:", response)
                    engine.say(response)
                    engine.runAndWait()
                else:
                    print("Failed to get a response.")

# Run Bella
bella()
