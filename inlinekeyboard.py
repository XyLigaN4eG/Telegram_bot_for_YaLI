import sys
from flask import Flask
from citytoiata import city_to_iata
from fly_requests import fly_requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence, \
    CallbackContext
from data import db_session

CITY_NAME, ONE_WAY, BEGINNING_OF_PERIOD, TRIP_DURATION, LIMITER, REQUESTER = range(6)
db_session.global_init("db/local_requests.sqlite")
reply_keyboard = [['Да', 'Нет']]
reply_keyboard_date = [[f'']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
REQUEST_KWARGS = {
    'proxy_url': 'socks5://orbtl.s5.opennetwork.cc:999',
    'urllib3_proxy_kwargs': {
        'username': '429604643',
        'password': '3mDjU04i'}
}


def start(update, context):
    update.message.reply_text(
        "Привет. Я бот, который поможет вам купить авиабилеты!\n"
        "Вы можете прервать мою работу, послав команду /stop.\n"
        "Откуда и куда вы хотите направиться? Пример: из Казани в Москву")
    return CITY_NAME


def city_name(update, context):
    dest_and_origin = str(city_to_iata(update.message.text)).split(",")
    context.user_data['or'] = dest_and_origin[0].replace("(", "").replace(")", "").replace("'", "")
    context.user_data['dest'] = dest_and_origin[1].replace("(", "").replace(")", "").replace("'", "").replace(" ", "")
    if context.user_data['or'] == context.user_data['dest']:
        update.message.reply_text("Ой-ой, кажется город отправления и прибытия совпадают. Попробуйте ещё раз.")
        return CITY_NAME

    update.message.reply_text("Нужны ли билеты на обратный путь?(Да/Нет)", reply_markup=markup)

    return ONE_WAY


def one_way(update, context):
    if str(update.message.text).lower == "да" or str(update.message.text) == "Да":
        context.user_data['one_way'] = "false"
        update.message.reply_text("Какова будет длительность путешествия в неделях.")
        return TRIP_DURATION
    elif str(update.message.text).lower == 'нет' or str(update.message.text) == "Нет":
        context.user_data['one_way'] = "true"

        update.message.reply_text("Введите первое число месяца, в который будут попадать даты отправления.(DD.MM.YYYY)")
        return BEGINNING_OF_PERIOD
    else:
        update.message.reply_text("Введите корректный ответ")
        return ONE_WAY


def trip_duration(update, context):
    if " " not in str(update.message.text):
        if str(update.message.text).isdigit():
            update.message.reply_text(
                "Введите первое число месяца, в который будут попадать даты отправления.(DD.MM.YYYY)")
            context.user_data['trip_duration'] = update.message.text
            return BEGINNING_OF_PERIOD
        else:
            update.message.reply_text(
                "Вы неправильно ввели длительность путешествия. Попробуйте ещё раз.")
            return TRIP_DURATION
    elif " " in str(update.message.text):
        trip_duration_name = str(update.message.text).split(" ")
        if str(trip_duration_name[0]).isdigit():
            context.user_data['trip_duration'] = trip_duration_name[0]
            update.message.reply_text(
                "Введите первое число месяца, в который будут попадать даты отправления.(DD.MM.YYYY)")
            return BEGINNING_OF_PERIOD
        else:
            update.message.reply_text(
                "Вы неправильно ввели длительность путешествия. Попробуйте ещё раз.")
            return TRIP_DURATION
    else:
        update.message.reply_text("Вы неправильно ввели длительность путешествия. Попробуйте ещё раз.")
        return TRIP_DURATION


def beginning_of_period(update, context):
    if "." in update.message.text:
        normal_date = str(update.message.text).split('.')
        if str(normal_date[0]).isdigit() and str(normal_date[1]).isdigit() and str(normal_date[2]).isdigit():
            if int(normal_date[0]) > 31 or int(normal_date[1]) > 12 or int(normal_date[2]) > 2100 or int(
                    normal_date[2]) < 2020:
                update.message.reply_text(
                    "Что-то мне подсказывает, что дата введена неверно. Может попробуете ещё раз?")
                return BEGINNING_OF_PERIOD
        context.user_data['date'] = str(normal_date[2]) + "-" + str(normal_date[1]) + "-" + str(normal_date[0])
        update.message.reply_text("Какое максимальное количество предложений вы хотите увидеть?")
        return LIMITER
    else:
        update.message.reply_text("Вы неправильно ввели дату. Попробуйте ещё раз.")
        return BEGINNING_OF_PERIOD


def limiter(update, context):
    if " " not in str(update.message.text):
        if str(update.message.text).isdigit():
            context.user_data['limit'] = update.message.text
            return REQUESTER
        else:
            update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
            return LIMITER
    elif " " in str(update.message.text):
        limit_name = str(update.message.text).split(" ")
        if str(limit_name[0]).isdigit():
            context.user_data['limit'] = limit_name[0]
            print(1)
            return REQUESTER
        else:
            update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
            return LIMITER
    else:
        update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
        return LIMITER


def requester(update, context):
    for i in range(len(fly_requests(context.user_data))):
        if len(str(fly_requests(context.user_data)[i][3])) < 1:
            if len(str(fly_requests(context.user_data)[i][4])) < 1:
                if len(str(fly_requests(context.user_data)[i][5])) < 1:
                    update.message.reply_text(str(fly_requests(context.user_data)[i][0] + "\n") +
                                              str(fly_requests(context.user_data)[i][1] + "\n") +
                                              str(fly_requests(context.user_data)[i][2] + "\n") +
                                              str(fly_requests(context.user_data)[i][3] + "\n") +
                                              str(fly_requests(context.user_data)[i][4] + "\n") +
                                              str(fly_requests(context.user_data)[i][5] + "\n"))
                else:
                    update.message.reply_text(str(fly_requests(context.user_data)[i][0] + "\n") +
                                              str(fly_requests(context.user_data)[i][1] + "\n") +
                                              str(fly_requests(context.user_data)[i][2] + "\n") +
                                              str(fly_requests(context.user_data)[i][3] + "\n") +
                                              str(fly_requests(context.user_data)[i][4] + "\n"))
            else:
                update.message.reply_text(str(fly_requests(context.user_data)[i][0] + "\n") +
                                          str(fly_requests(context.user_data)[i][1] + "\n") +
                                          str(fly_requests(context.user_data)[i][2] + "\n") +
                                          str(fly_requests(context.user_data)[i][3] + "\n"))
        else:
            update.message.reply_text(str(fly_requests(context.user_data)[i][0] + "\n") +
                                      str(fly_requests(context.user_data)[i][1] + "\n") +
                                      str(fly_requests(context.user_data)[i][2] + "\n"))
    return ConversationHandler.END


def stop(update, context):

    update.message.reply_text('Пока! Надеюсь, что я вам помог.')

    return ConversationHandler.END


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    updater = Updater("1213624266:AAFEhfCRLn-0nGulWqs5RJMrSJqgUhG8Q9s", use_context=True,
                      request_kwargs=REQUEST_KWARGS)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            CITY_NAME: [MessageHandler(Filters.text, city_name, pass_user_data=True)],
            ONE_WAY: [MessageHandler(Filters.text, one_way, pass_user_data=True)],
            TRIP_DURATION: [MessageHandler(Filters.text, trip_duration, pass_user_data=True)],
            BEGINNING_OF_PERIOD: [MessageHandler(Filters.text, beginning_of_period, pass_user_data=True)],
            LIMITER: [MessageHandler(Filters.text, limiter, pass_user_data=True)],
            REQUESTER: [MessageHandler(Filters.text, requester, pass_user_data=True)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conversation_handler)
    # dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("city_name", city_name))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
