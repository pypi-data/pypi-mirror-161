import random

GAME_DESCRIPTION = 'What number is missing in the progression?'
LENGTH = 10


def get_question_answer():
    start = random.randint(0, 20)
    step = random.randint(-5, 5)
    progression = [str(start + step * i) for i in range(1, LENGTH + 1)]
    missing_index = random.randint(0, LENGTH - 1)
    right_answer = progression[missing_index]
    progression[missing_index] = '..'
    question = ' '.join(progression)
    return question, right_answer
