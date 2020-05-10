import logging
import telegram
from flask import Flask
from flask_restful import Api
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from citytoiata import city_to_iata
from data import db_session
from data.local_requests import LocalRequests
from fly_requests import fly_requests

app = Flask(__name__)
api = Api(app)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logging.basicConfig(level=logging.DEBUG)


def log():
    logging.debug('Debug')
    logging.info('Info')
    logging.warning('Warning')
    logging.error('Error')
    logging.critical('Critical or Fatal')


CITY_NAME, ONE_WAY, BEGINNING_OF_PERIOD, TRIP_DURATION, LIMITER, REQUESTER = range(6)
db_session.global_init("db/local_requests.sqlite")
reply_keyboard = [['Да', 'Нет']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)


def tg_help(update, context):
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
    if str(update.message.text) == '/start':
        return start(update, context)
    update.message.reply_text("Моей основной задачей является подбор авиабилетов, но вот с их "
                              "покупкой я пока не дружу :(\nПропишите команду /start, чтобы начать выбор билетов,"
                              "или команду /stop, чтобы прервать мою работу.")


def start(update, context):
    telegram.ReplyKeyboardRemove(selective=True)
    update.message.reply_text(
        "Привет. Я бот, который поможет вам купить авиабилеты!\n"
        "Вы можете узнать, на что я способен, просто прописав команду /help.\n"
        "Откуда и куда вы хотите направиться? Пример: из Казани в Москву.")

    return CITY_NAME


def city_name(update, context):
    if str(update.message.text) == '/help':
        return tg_help(update, context)
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
    try:
        dest_and_origin = str(city_to_iata(update.message.text, context.user_data)).split(",")
        if len(dest_and_origin[0]) != 0:
            context.user_data['or'] = dest_and_origin[0].replace("(", "").replace(")", "").replace("'", "")
            context.user_data['dest'] = dest_and_origin[1].replace("(", "").replace(")", "").replace("'", "").replace(
                " ",
                "")
        else:
            update.message.reply_text("Ой-ой, что-то пошло не так. Проверьте правильность написания.")
        if context.user_data['or'] == context.user_data['dest']:
            update.message.reply_text("Ой-ой, кажется город отправления и прибытия совпадают. Попробуйте ещё раз.")
            return CITY_NAME

        update.message.reply_text("Нужны ли билеты на обратный путь?(Да/Нет)", reply_markup=markup)

        return ONE_WAY
    except IndexError:
        update.message.reply_text("Название некорректно. Проверьте правильность написания.")
        return CITY_NAME


def one_way(update, context):
    if str(update.message.text) == '/help':
        return tg_help(update, context)
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
    if str(update.message.text) == "да" or str(update.message.text) == "Да" or str(update.message.text) == "ДА":
        context.user_data['one_way'] = "false"
        update.message.reply_text("Какова будет длительность путешествия в неделях(Максимум 4)?")
        return TRIP_DURATION
    elif str(update.message.text) == 'нет' or str(update.message.text) == "Нет" or str(update.message.text) == 'НЕТ':
        context.user_data['one_way'] = "true"
        context.user_data['trip_duration'] = 0
        update.message.reply_text("Введите первое число месяца, в который будут попадать даты отправления.(DD.MM.YYYY)")
        return BEGINNING_OF_PERIOD
    else:
        update.message.reply_text("Введите корректный ответ.")
        return ONE_WAY


def trip_duration(update, context):
    telegram.ReplyKeyboardRemove(selective=True)
    if str(update.message.text) == '/help':
        return tg_help(update, context)
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
    if int(update.message.text) > 4:
        update.message.reply_text("Введите корректный ответ.")
        return TRIP_DURATION
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
    telegram.ReplyKeyboardRemove(selective=True)
    if str(update.message.text) == '/help':
        return tg_help(update, context)
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
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
    if str(update.message.text) == '/help':
        return tg_help(update, context)
    if str(update.message.text) == '/stop':
        return ConversationHandler.END
    if " " not in str(update.message.text):
        if str(update.message.text).isdigit():
            context.user_data['limit'] = update.message.text
            return requester(update, context)
        else:
            update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
            return LIMITER
    elif " " in str(update.message.text):
        limit_name = str(update.message.text).split(" ")
        if str(limit_name[0]).isdigit():
            context.user_data['limit'] = limit_name[0]
            return requester(update, context)
        else:
            update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
            return LIMITER
    else:
        update.message.reply_text("Вы неправильно ввели максимальное количество предложений. Попробуйте ещё раз.")
        return LIMITER


def requester(update, context):
    telegram.ReplyKeyboardRemove(selective=True)
    session_2 = db_session.create_session()
    update.message.reply_text(
        "Идёт подбор билетов, ожидайте.")
    if fly_requests(context.user_data) == 1:
        for user in session_2.query(LocalRequests).filter(LocalRequests.id < int(context.user_data['limit']) + 1):
            update.message.reply_text(
                str('Город отправления: ' + str(context.user_data["not_iata_or"])) + "\n" + str(
                    'Город прибытия: ' + str(context.user_data["not_iata_ds"])) + "\n" +
                str(user.value) + "\n" + str(user.depart_date) + "\n" +
                str(user.return_date).replace('None', 'Не установлено') +
                '\n' + str(user.gate).replace("NOTION", "https://www.s7.ru/ru/").replace("OneTwoTrip",
                                                                                         "https://www.onetwotrip.com"
                                                                                         "/ru/"
                                                                                         ).replace('Tinkoff',
                                                                                                   'https://www.tinkoff'
                                                                                                   '.ru/'
                                                                                                   'travel/flights/').
                replace("Azimuth", "https://azimuth.aero/ru").replace('Aeroflot', 'https://www.aeroflot.ru/ru-ru').
                replace('SuperSaver', 'https://www.supersaver.ru/').replace('', '').replace(
                    "Rusline", "https://www.rusline.aero/").replace("Pobeda", "https://www.pobeda.aero/").
                replace("Utair", "https://www.utair.ru/"))

        update.message.reply_text(
            "Благодарим за использование бота!")
        session_2.query(LocalRequests).delete()
        session_2.commit()
    else:
        update.message.reply_text(
            "К сожалению на данный момент билеты на подобные рейсы отсутствуют. Попытайтесь в другое время.")
    return ConversationHandler.END


def fallback(update, context):
    return ConversationHandler.END


def main():
    updater = Updater("1291892923:AAGFf_G_ETvtISyXJC9_tSJnZAG9hPdVnDA", use_context=True)

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CITY_NAME: [MessageHandler(Filters.text, city_name, pass_user_data=True)],
            ONE_WAY: [MessageHandler(Filters.text, one_way, pass_user_data=True)],
            TRIP_DURATION: [MessageHandler(Filters.text, trip_duration, pass_user_data=True)],
            BEGINNING_OF_PERIOD: [MessageHandler(Filters.text, beginning_of_period, pass_user_data=True)],
            LIMITER: [MessageHandler(Filters.text, limiter, pass_user_data=True)],
            REQUESTER: [MessageHandler(Filters.text, requester, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('stop', fallback)]
    )
    dp.add_handler(CommandHandler('help', tg_help))
    dp.add_handler(conversation_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
    log()
