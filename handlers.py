from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import tree, questions, answers, quizes, quiz_math, quiz_verbal, quizes_indexes
from service import generate_options_keyboard, get_question, get_question_quiz, new_quiz, get_quiz_index, get_quiz_index_quiz,\
 update_quiz_index, update_quiz_index_quiz, get_quiz_score_quiz, get_quiz_name,update_quiz_name

router = Router()

@router.callback_query(F.data.startswith("answ_"))
#@router.callback_query(F.data == 'answ_')
async def right_answer(callback: types.CallbackQuery):
    
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    """
    await callback.bot.edit_message_text.EditMessageText(
        text = '',
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    """
    answer_index = callback.data.split("_")[1]
    answer_index = int(answer_index)
    #await callback.message.answer(answer_index)

    current_question_index = await get_quiz_index(callback.from_user.id)

    current_question_index = current_question_index.decode('UTF-8')
    #await callback.message.answer(current_question_index)

    current_options = questions[current_question_index][1]    
    chosen_answer = current_options[answer_index]

    next_question = tree[chosen_answer]
    


    if next_question == '-1':
       await callback.message.answer("Это был последний вопрос.")
    else:
       next_question = next_question.encode('UTF-8')
       await update_quiz_index(callback.from_user.id, next_question)
       await get_question(callback.message, callback.from_user.id)

# Хэндлер на команду /start
@router.message(F.data=='start')
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    #builder.add(types.KeyboardButton(text="start"))
    #await message.answer("Привет!Ответь, пожалуйста, на несколько вопросов", reply_markup=builder.as_markup(resize_keyboard=True))
    await message.answer("Привет!Ответь, пожалуйста, на несколько вопросов")
    await new_quiz(message)
    
# Хэндлер на команду /quiz
#@router.message(F.text=="Start")
#async def cmd_quiz(message: types.Message):
    
    #await message.answer("Привет!Ответь, пожалуйста, на несколько вопросов", reply_markup=builder.as_markup(resize_keyboard=True))
    #await new_quiz(message)



@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    quiz_name = await get_quiz_name(callback.from_user.id)
    await callback.message.answer("Correct!")
    quiz_name = quiz_name.decode('UTF-8')

    current_question_index = await get_quiz_index_quiz(callback.from_user.id,quiz_name)
    current_score = await get_quiz_score_quiz(callback.from_user.id, quiz_name)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index_quiz(callback.from_user.id, current_question_index, current_score+1 ,quiz_name)

    quiz_data = quizes[quiz_name]
    n = len(quiz_data)
    

    if current_question_index < n:
        await get_question_quiz(callback.message, callback.from_user.id,quiz_name)
    else:
        current_score = await get_quiz_score_quiz(callback.from_user.id, quiz_name)
        await callback.message.answer(f"{quiz_name} quiz completed. Your score: {current_score} out of {n}")


@router.callback_query(F.data == "wrong_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    quiz_name = await get_quiz_name(callback.from_user.id)
    quiz_name = quiz_name.decode('UTF-8')

    await callback.message.answer("Incorrect!")
    current_question_index = await get_quiz_index_quiz(callback.from_user.id,quiz_name)
    current_score = await get_quiz_score_quiz(callback.from_user.id, quiz_name)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index_quiz(callback.from_user.id, current_question_index, current_score ,quiz_name)

    quiz_data = quizes[quiz_name]
    n = len(quiz_data)

    if current_question_index < n:
        await get_question_quiz(callback.message, callback.from_user.id,quiz_name)
    else:
        current_score = await get_quiz_score_quiz(callback.from_user.id, quiz_name)
        await callback.message.answer(f"{quiz_name} quiz completed. Your score: {current_score} out of {n}")