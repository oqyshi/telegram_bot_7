from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

poem = """
Белеет парус одинокий
В тумане моря голубом.
Что ищет он в стране далекой?
Что кинул он в краю родном?
""".strip().split("\n")

LAST_READ = "last_read"

WAIT_FOR_NEXT_STRING, WAIT_REPEAT_ALL, ENABLE_SUPHLER = 1, 2, 3


def start(update, context):
    update.message.reply_text("Давайте почитаем стихотворение по строчке по очереди.")
    update.message.reply_text("Я начну.")
    update.message.reply_text(poem[0])
    context.user_data[LAST_READ] = 0
    return WAIT_FOR_NEXT_STRING


def continue_or_repeat(update, user_data, next_string_index):
    if next_string_index + 1 < len(poem):  # Есть, что прочитать дальше.
        next_string_index += 1
        update.message.reply_text(poem[next_string_index])
        user_data[LAST_READ] = next_string_index

    if next_string_index + 1 < len(poem):  # Есть, что ждать дальше.
        return WAIT_FOR_NEXT_STRING
    else:  # Закончили.
        update.message.reply_text("Стихотворение закончилось. Хотите еще раз? (/yes /no)")
        return WAIT_REPEAT_ALL


def normalize(string):
    return string.lower().replace(".", "").replace(",", "").replace("-", "").replace("?", "").replace("!", "").replace(
        ":", "")


def get_next_string(update, context):
    next_string_index = context.user_data[LAST_READ] + 1
    if normalize(poem[next_string_index]) == normalize(update.message.text):  # Правильная строчка.
        return continue_or_repeat(update, context.user_data, next_string_index)
    else:  # Неправильная строчка.
        update.message.reply_text("Нет, не так. Попробуйте еще раз или позовите суфлера (/suphler).")
        return ENABLE_SUPHLER


def suphler(update, context):
    next_string_index = context.user_data[LAST_READ] + 1
    update.message.reply_text(poem[next_string_index])
    return continue_or_repeat(update, context.user_data, next_string_index)


def stop(update, context):
    update.message.reply_text("До новых встреч!")
    context.user_data[LAST_READ] = 0
    return ConversationHandler.END


def main():
    updater = Updater("YOUR_TOKEN", use_context=True)
    dp = updater.dispatcher

    museum_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            WAIT_FOR_NEXT_STRING: [
                MessageHandler(Filters.text, get_next_string, pass_user_data=True)
            ],
            ENABLE_SUPHLER: [
                MessageHandler(Filters.text, get_next_string, pass_user_data=True),
                CommandHandler('suphler', suphler, pass_user_data=True)
            ],
            WAIT_REPEAT_ALL: [
                CommandHandler('yes', start, pass_user_data=True),
                CommandHandler('no', stop, pass_user_data=True)
            ]
        },
        fallbacks=[CommandHandler('stop', stop, pass_user_data=True)]
    )

    dp.add_handler(museum_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()