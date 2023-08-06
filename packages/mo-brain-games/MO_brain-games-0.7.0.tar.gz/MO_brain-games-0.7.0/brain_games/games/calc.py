import random
from operator import add, sub, mul

OPERATIONS = [
    ('+', add),
    ('-', sub),
    ('*', mul)
]

GAME_DESCRIPTION = 'What is the result of the expression?'


def get_question_answer():
    x1 = random.randint(0, 25)
    x2 = random.randint(0, 25)
    sign, operation = random.choice(OPERATIONS)
    question = '{} {} {}'.format(x1, sign, x2)
    right_answer = str(operation(x1, x2))
    return question, right_answer
