import random

GAME_DESCRIPTION = '''
Answer "yes" if given number is prime. Otherwise answer "no".'''


def get_question_answer():
    question = random.randrange(100)
    right_answer = 'yes' if is_prime(question) else 'no'
    return question, right_answer


def is_prime(number):
    if number < 2:
        return False
    for i in range(2, number // 2):
        if number % i == 0:
            return False
    return True
