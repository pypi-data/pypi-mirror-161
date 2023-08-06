from brain_games.cli import greet_user
import prompt

MAX_LIMIT = 3


def play(game):
    user_name = greet_user()
    print(game.GAME_DESCRIPTION)
    for _ in range(MAX_LIMIT):
        question, right_answer = game.get_question_answer()
        print(f'Question: {question}')
        user_answer = prompt.string('Your answer: ')
        if user_answer == right_answer:
            print('Correct!')
        else:
            print('{} is wrong answer ;(. Correct answer was {}'.format(
                user_answer, right_answer
            ))
            print(f"Let's try again, {user_name}!")
            break
    else:
        print(f'Congratulations, {user_name}!')
