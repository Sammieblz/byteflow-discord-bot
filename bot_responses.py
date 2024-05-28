from random import choice, randint



def get_response(user_input: str) -> str: # NOQA
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1,6)}' # NOQA
    else:
        return choice([
            'I am not sure I understand...',
            'What do you mean?',
            'Do you mind rephrasing that?',
            'Hmm....',
            'Thinking....',
        ])
