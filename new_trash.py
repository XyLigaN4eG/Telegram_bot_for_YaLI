data = []
r = 0
for i in range(10):
    for j in range(10):
        data.append(r)
        r += 1
print(data)





_____________________________________________

def asker():
    one_way_asker = input("Нужны ли Вам обратные билеты?(Да/Нет)\n")
    if one_way_asker.lower() == "нет":
        ONE_WAY = "true"
    duration_asker = input("Сколько дней будет длиться Ваше прибывание в другом городе?(В неделях)\n")
    if " " in duration_asker:
        duration_asker.split(" ")
        trip_duration = duration_asker[0]
    else:
        trip_duration = duration_asker

    beginning_of_period_asker = input(
        "Введите дату, когда бы Вы хотели отправиться.(будут показаны результаты на месяц с даты отправления."
        "Формат ввода: DD.MM.YYYY)\n")
    correct_date = beginning_of_period_asker.split(".")
    BEGINNING_OF_PERIOD = correct_date[2] + "-" + correct_date[1] + "-" + correct_date[0]
    limit = input("Какое максимальное количество предложений предложений Вы хотите увидеть?\n")
    origin = str(iata[0]).replace("(", "").replace("'", "")

    destination = str(iata[1]).replace(")", "").replace("'", "").replace(" ", "")

-------------------------------------------------------------------------------------------


from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
import flask_restful
import logging
from fly_requests import fly_requests

REQUEST_KWARGS = {
    'proxy_url': 'socks5://96.113.176.101:1080'}
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GREETING, PROCESSING, ONE_WAY_TICKET, DATE, ORIGIN_AND_DESTINATION, CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(8)


# reply_keyboard = [['Нужен ли билет обратно?', 'Путь отправления/назначения.'],
#                  ['Дата отправления.', 'Something else...'],
#                 ['Завершить']]
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    reply_text = "Hi! My name is Doctor Botter."
    if context.user_data:
        reply_text += " You already told me your {}. Why don't you tell me something more " \
                      "about yourself? Or change anything I " \
                      "already know.".format(", ".join(context.user_data.keys()))
    else:
        reply_text += " I will hold a more complex conversation with you. Why don't you tell me " \
                      "something about yourself?"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text.lower()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = 'Your {}, I already know the following ' \
                     'about that: {}'.format(text, context.user_data[text])
    else:
        reply_text = 'Your {}? Yes, I would love to hear about that!'.format(text)
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(update, context):
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{}"
                              "You can tell me more, or change your opinion on "
                              "something.".format(facts_to_str(context.user_data)),
                              reply_markup=markup)

    return CHOOSING


def show_data(update, context):
    update.message.reply_text("This is what you already told me:"
                              "{}".format(facts_to_str(context.user_data)))


def done(update, context):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(facts_to_str(context.user_data)))
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def date(update, context):
    pass


def origin_and_destination(update, context):
    pass


def greet(update, context):
    pass


def process(update, context):
    pass


def one_way_ticket(update, context):
    pass


def main():
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater("719309973:AAF-hkTc61L07XjVxPy08eM6elxzWIMaq3Y", persistence=pp, use_context=True,
                      request_kwargs=REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PROCESSING: [MessageHandler(Filters.text,
                                        process),
                         ],
            ORIGIN_AND_DESTINATION: [MessageHandler(Filters.regex('^Путь отправления/назначения.$'),
                                                    origin_and_destination),
                                     ],
            ONE_WAY_TICKET: [MessageHandler(Filters.regex('^Нужен ли билет обратно?$'),
                                            one_way_ticket),
                             ],
            DATE: [MessageHandler(Filters.regex('^Дата отправления.$'),
                                  date),
                   ],
            GREETING: [MessageHandler(Filters.text,
                                      greet),
                       ],
            CHOOSING: [MessageHandler(Filters.regex('^(Age|Favourite colour|Number of siblings)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^Something else...$'),
                                      custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^/done$'), done)],
        name="my_conversation",
        persistent=True
    )

    dp.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data)
    dp.add_handler(show_data_handler)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
