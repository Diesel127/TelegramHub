from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.constants import CLOSE_BUTTON
from src.quiz_data import QUIZ_DATA
from src.utils import send_text, send_image, send_text_buttons


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the quiz mode.
    Resets user state, initializes the quiz index,
    and sends the first quiz question.
    """
    context.user_data.clear()
    context.user_data["conversation_state"] = "quiz"
    context.user_data["quiz_index"] = 0

    await send_quiz_question(update, context)


async def send_quiz_question(update, context):
    """
    Send the current quiz question.
    Displays the question image, answer options as inline buttons,
    and navigation controls. Finishes the quiz when all questions are answered.
    """
    idx = context.user_data.get("quiz_index", 0)

    if idx >= len(QUIZ_DATA):
        await send_text_buttons(
            update,
            context,
            "Quiz finished.",
            CLOSE_BUTTON
        )
        return

    quiz_item = QUIZ_DATA[idx]

    await send_image(update, context, quiz_item["image"], folder="quiz_imgs")

    keyboard = []

    for option in quiz_item["options"]:
        keyboard.append([
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz_answer:{option}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("Next", callback_data="quiz_next"),
        InlineKeyboardButton("Close", callback_data="start"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=quiz_item["question"],
        reply_markup=reply_markup
    )


async def quiz_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle quiz inline button actions.
    Processes answer selection and moves to the next question
    when requested.
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    # answer of quiz question
    if data.startswith("quiz_answer:"):
        selected = data.split(":")[1]
        idx = context.user_data["quiz_index"]
        correct = QUIZ_DATA[idx]["correct"]

        if selected == correct:
            await query.message.reply_text("✅ Correct")
        else:
            await query.message.reply_text(f"❌ Wrong. Correct: {correct}")

        return

    # next question
    if data == "quiz_next":
        context.user_data["quiz_index"] += 1
        await send_quiz_question(update, context)
        return
