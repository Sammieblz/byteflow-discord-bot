import nltk
from random import choice, randint
from nltk.sentiment import SentimentIntensityAnalyzer
from discord import File
import requests  # For making API requests (if needed)
from googleapiclient.discovery import build
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests
import discord
from dotenv import load_dotenv
import os
import wolframalpha
import re



nltk.download('vader_lexicon')  # Download sentiment analysis data
sia = SentimentIntensityAnalyzer()

# Youtube v3 API Key

youtube = build('youtube', 'v3', developerKey=api_key)

# Load pre-trained Dialo GPT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
def get_response(user_input: str, context: dict = {}) -> tuple[str, str | None]:
    # Return a tuple of response text and optional file path
    lowered = user_input.lower()
    sentiment = sia.polarity_scores(user_input)

    if lowered == '':
        return "Well, you're awfully silent...", None

    if lowered in ['hello', 'hi', 'hey', 'sup', 'yo']:

        if 'user_name' in context:

            return f"Hi again, {context['user_name']}! 👋", None

        else:

            return "Hello there! What's your name?", None

    elif 'how are you' in lowered:

        if sentiment['compound'] > 0.5:

            return choice([

                "I'm fantastic! 😊 How about you?",

                "Couldn't be better! 😎 What's up with you?",

                "I'm doing great! Thanks for asking. 😄",

            ]), None

        else:

            return choice([

                "I'm hanging in there. 😐 Hopefully, your day is brighter.",

                "Could be better, but I'm here for you! 🤗 What's on your mind?",

                "Not the best day, but I'm sure it'll get better. 😊",

            ]), None

    # Likes and dislikes
    elif 'i like' in lowered or 'i love' in lowered:

        thing_liked = lowered.split('i like')[-1].strip() or lowered.split('i love')[-1].strip()

        context['liked_thing'] = thing_liked

        return f"That's awesome! {thing_liked} sounds great! Tell me more about why you like it.", None

    elif 'i dislike' in lowered or 'i hate' in lowered:
        thing_disliked = lowered.split('i dislike')[-1].strip() or lowered.split('i hate')[-1].strip()
        return choice([
            f"Oh no, what don't you like about {thing_disliked}?",
            f"That's too bad. Maybe you haven't found the right {thing_disliked} yet.",
            f"I'm sorry to hear that. Everyone has different tastes, I suppose.",
        ]), None

        # Activities and Hobbies
    elif 'hobby' in lowered or 'interests' in lowered:
        return choice([
            "I love learning new things and chatting with people! 🤓 What are your hobbies?",
            "I'm always up for a good conversation or a fun game. What do you like to do in your free time?",
        ]), None

    elif 'movie' in lowered or 'film' in lowered:
        return choice([
            "Oh, I love movies! 🍿 What's your favorite genre?",
            "Have you seen any good movies lately? I'm always looking for recommendations.",
            "I'm a big fan of classic films. 🎬 What about you?",
        ]), None

    # Favorites
    elif 'favorite' in lowered:
        return choice([
            "Ooh, favorites! That's always a tough question. 🤔 What are some of yours?",
            "I have so many favorites, it's hard to choose! 🎶 Maybe we share some in common. "
            "What are some of your favorites?",
        ]), None

    # Example: Sending an image when user mentions cats
    elif 'cat' in lowered:
        return "I love cats! 🐱", "./images/cute-cat.jpg"

    elif 'bye' in lowered:
        return "Goodbye! It was nice talking to you. 👋", None

    elif 'roll dice' in lowered:
        return f'You rolled a {randint(1, 6)}.', None

    elif 'my name is' in lowered:
        name = lowered.split('my name is')[-1].strip()
        context['user_name'] = name
        return f"Nice to meet you, {name}! 😊", None

    # Time/Date
    elif 'time' in lowered:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return f"The current time is {current_time}.", None
    elif 'date' in lowered:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        return f"Today is {current_date}.", None

    # Joke
    elif 'joke' in lowered or 'funny' in lowered:
        return choice([
            "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
            "Parallel lines have so much in common. It's a shame they'll never meet. 🤷",
            "I told my wife she was drawing her eyebrows too high. She seemed surprised. 🤨",
        ]), None

    # YouTube search
    elif 'youtube' in lowered and 'search' in lowered:

        query = lowered.split('search')[-1].strip()

        try:

            request = youtube.search().list(q=query, part='id,snippet', maxResults=1, type='video')

            response = request.execute()

            if response['items']:

                video_id = response['items'][0]['id']['videoId']

                video_title = response['items'][0]['snippet']['title']

                return f"Here's a video I found: https://www.youtube.com/watch?v={video_id} - {video_title}", None

            else:

                return "Sorry, I couldn't find any videos for that search.", None

        except Exception as e:  # Add error handling here

            print(f"Error occurred during YouTube search: {e}")

            return "Oops! Something went wrong with the search.", None

    # Weather
    elif "weather" in lowered:
        city_name = None
        if "in" in lowered:
            city_name = lowered.split("in")[-1].strip()
        elif "for" in lowered:
            city_name = lowered.split("for")[-1].strip()
        else:
            return "Please specify a city (e.g., 'weather in London' or 'weather for New York').", None

        api_key = os.getenv("OPENWEATHER_API_KEY")
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name + "&units=imperial"  # imperial for Farenheit
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            main = data["main"]
            temperature = main["temp"]
            humidity = main["humidity"]
            description = data["weather"][0]["description"]
            return (
                f"The weather in {city_name} is currently {temperature}°F with {humidity}% humidity. The sky is {description}.",
                None,
            )
        else:
            return f"Sorry, I couldn't find weather information for {city_name}.", None

    # Math
    elif user_input.startswith("calculate") or user_input.startswith("math"):
        expression = user_input.split(maxsplit=1)[1].strip()  # Extract expression

        # Check if extracted expression is a valid math expression
        if re.match(r"^[0-9\+\-\*\/\%\(\)\.\s]+$", expression):  # Check the expression, not user_input
            try:
                # Use Wolfram Alpha to evaluate the expression
                client = wolframalpha.Client(os.getenv("WOLFRAM_ALPHA_APPID"))
                res = client.query(expression)
                answer = next(res.results).text
                return f"According to Wolfram Alpha, the answer is: {answer}", None
            except Exception as e:
                print(f"Error fetching Wolfram Alpha result: {e}")
                return "Sorry, I couldn't calculate that.", None
    else:
        try:
            # Build context from past conversation (up to the last 3 interactions)
            conversation_history = "\n".join(
                [f"{role}: {text}" for role, text in context.get("history", [])[-3:]]
            )

            # Construct the prompt with instructions and context
            prompt = f"""You are a friendly and helpful Discord bot named Chatty. Keep your responses concise and relevant to the conversation.
                                \n\n{conversation_history}\nUser: {user_input}\nChatty:"""

            # Generate response using DialoGPT
            new_user_input_ids = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors='pt')

            # Generate output with attention to length limitations
            max_length = 1900
            bot_input_ids = model.generate(
                new_user_input_ids,
                max_length=max_length,
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=2,  # Discourage repetition
                do_sample=True,  # Introduce some randomness
                top_k=50,
                top_p=0.95,
            )

            response = tokenizer.decode(bot_input_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)

            # Basic filtering for inappropriate content (you might want to expand this)
            if any(word in response.lower() for word in ["idiot", "stupid", "dumb", "shut up"]):
                response = "Please be respectful!"

            # Store response in context
            context.setdefault('history', []).append(('User', user_input))
            context['history'].append(('Chatty', response))

            return response, None
        except Exception as e:
            print(f"Error occurred while fetching response from DialoGPT: {e}")
            # Fallback to your original choices if Dialo GPT fails completely
            return choice([
                'I am not sure I understand...',
                'What do you mean?',
                'Do you mind rephrasing that?',
                'Hmm....',
                'Thinking....',
            ]), None