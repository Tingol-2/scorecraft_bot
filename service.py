from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import tree, questions, answers, quizes, quiz_math, quiz_verbal, quizes_indexes


def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for i,option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answ_{i}")
        )

    builder.adjust(1)
    return builder.as_markup()

def generate_options_keyboard_quiz(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            # Текст на кнопках соответствует вариантам ответов
            text=option,
            # Присваиваем данные для колбэк запроса.
            # Если ответ верный сформируется колбэк-запрос с данными 'right_answer'
            # Если ответ неверный сформируется колбэк-запрос с данными 'wrong_answer'
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()



async def get_question(message, user_id):
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    current_question_index= current_question_index.decode('UTF-8')
    if current_question_index in quizes_indexes:
        #global quiz_name
        quiz_name = questions[current_question_index][0]
        await get_question_quiz(message, user_id, quiz_name)
        quiz_name = quiz_name.encode('UTF-8')
        await update_quiz_name(user_id, quiz_name)
    else:
        # print(current_question_index)
        current_question = questions[current_question_index]
        question_text = current_question[0]
        question_answers = current_question[1]
        opts = [answers[i] for i in question_answers]
        kb = generate_options_keyboard(opts)
        await message.answer(f"{question_text}", reply_markup=kb)


async def get_question_quiz(message, user_id, quiz_name):
    
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index_quiz(user_id, quiz_name)

    # Получаем список вариантов ответа для текущего вопроса
    #await message.message.answer(quiz_name)
    quiz_data = quizes[quiz_name]

    opts = quiz_data[current_question_index]['options']
    correct_index = quiz_data[current_question_index]['correct_option']
    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard_quiz(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = b'1'
    await update_quiz_index(user_id, current_question_index)
    await update_quiz_index_quiz(user_id, 0, 0, 'math')
    await update_quiz_index_quiz(user_id, 0, 0, 'verbal')
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `questions_database`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    



async def get_quiz_index_quiz(user_id, quiz_name):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `{quiz_name}_quiz`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]  


async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS String;

        UPSERT INTO `questions_database` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )
     

async def update_quiz_index_quiz(user_id, question_index, score, quiz_name):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;
	    DECLARE $score AS Uint64;

        UPSERT INTO `{quiz_name}_quiz` (`user_id`, `question_index`, `score`)
        VALUES ($user_id, $question_index, $score);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
        score = score
    )


async def get_quiz_score_quiz(user_id, quiz_name):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT score
        FROM `{quiz_name}_quiz`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["score"] is None:
        return 0
    return results[0]["score"]  

async def update_quiz_name(user_id, name):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $name AS String;

        UPSERT INTO `quiz_name` (`user_id`, `name`)
        VALUES ($user_id, $name);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        name=name
    )


async def get_quiz_name(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT name
        FROM `quiz_name`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["name"] is None:
        return 0
    return results[0]["name"]  