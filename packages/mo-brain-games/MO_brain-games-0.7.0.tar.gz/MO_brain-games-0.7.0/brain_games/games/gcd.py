from math import gcd
import random

GAME_DESCRIPTION = 'Find the greatest common divisor of given numbers.'


def get_question_answer():
    x1 = random.randint(0, 50)
    x2 = random.randint(0, 50)
    question = '{} {}'.format(x1, x2)
    right_answer = str(gcd(x1, x2))
    return question, right_answer
