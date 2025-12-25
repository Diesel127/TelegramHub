import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from src.en_words import EN_WORDS
from src.utils import send_image


def scramble(word: str) -> str:
    """
    Example:
        scramble("network") -> nteowrk
    """
    if len(word) <= 3:
        return f"*{word}*"
    first = word[0]
    last = word[-1]
    middle = list(word[1:-1])
    random.shuffle(middle)
    return f"*{first}*{''.join(middle)}*{last}*"


async def english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User enters command /english
    Bot sends scrambled word and waits for user's guess.
    """
    context.user_data.clear()
    context.user_data["conversation_state"] = "english"
    await send_image(update, context, "english")
    word = random.choice(EN_WORDS)

    context.user_data["english_word"] = word
    context.user_data["english_scrambled"] = scramble(word)
    context.user_data["english_answer"] = None

    text = (
        "Make a word from letters:\n"
        "_First and last letters are correct_\n\n"
        f"{context.user_data['english_scrambled']}"
    )

    keyboard = [
        [
            InlineKeyboardButton("Next", callback_data="eng_next"),
            InlineKeyboardButton("Close", callback_data="start"),
        ],
    ]

    await update.effective_chat.send_message(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def english_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline keyboard actions for the English word scramble game.
    Behavior:
    - Ignores callbacks if the current conversation state is not "english".
    - On "eng_next", starts a new English game round.
    """
    query = update.callback_query
    await query.answer()

    if context.user_data.get("conversation_state") != "english":
        return

    if query.data == "eng_next":
        await english(update, context)
