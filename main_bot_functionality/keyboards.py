
from main_bot_functionality.models import Salon, Specialist, Service, SalonManager

import django
import telebot


def create_back_button():
    return telebot.types.KeyboardButton('Назад')


# создаем кнопки согласия на обработку персональных данных
def create_consent_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    assept_button = telebot.types.InlineKeyboardButton(
        'Принять', callback_data='accept')
    reject_button = telebot.types.InlineKeyboardButton(
        'Отклонить', callback_data='reject')
    keyboard.add(assept_button, reject_button)
    return keyboard


def create_day_keyboard(working_days):
    markup = telebot.types.InlineKeyboardMarkup()
    for day in working_days:
        markup.add(telebot.types.InlineKeyboardButton(
            text=day,
            callback_data=f"day_{day}"
        ))
    return markup


def create_time_input_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("Отправить время"))
    return markup


# Создаем первый набор кнопок

def create_first_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton("Выбрать салон")
    button2 = telebot.types.KeyboardButton("Выбрать любимого специалиста")
    button3 = telebot.types.KeyboardButton(
        "Хочу записаться по номеру телефона")
    keyboard.row(button1)
    keyboard.row(button2, button3)
    return keyboard

# Создаем второй набор кнопок


def get_manager_number():
    keyboard = telebot.types.ReplyKeyboardMarkup()
    try:
        managers = SalonManager.objects.all()
        for manager in managers:
            button_text = f"{manager.phone_number} - ({manager.name})"
            button = telebot.types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"manager_{manager.id}"
            )
            keyboard.add(button)
    except Exception as e:
        print(f"Error fetching managers: {e}")
    return keyboard


def create_salons_keyboard_for_call():
    keyboard = telebot.types.InlineKeyboardMarkup()
    salons = Salon.objects.all()
    for salon in salons:
        button = telebot.types.InlineKeyboardButton(
            text=salon.name,
            callback_data=f"callSalon_{salon.name}"
        )
        keyboard.add(button)
    return keyboard


def create_second_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button5 = telebot.types.KeyboardButton("Прайс на процедуры")
    button6 = telebot.types.KeyboardButton("Запись по времени")
    button7 = telebot.types.KeyboardButton("Наши салоны")
    back_button = create_back_button()
    keyboard.row(button5, button6)
    keyboard.row(button7, back_button)
    return keyboard


def create_salons_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    salons = Salon.objects.all()
    for salon in salons:
        button = telebot.types.InlineKeyboardButton(
            text=salon.name,
            callback_data=f"salons_{salon.id}"
        )
        keyboard.add(button)
    return keyboard


def create_services_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    services = Service.objects.all()
    for service in services:
        button = telebot.types.InlineKeyboardButton(
            text=service.name,
            callback_data=f"service_{service.name}"
        )
        keyboard.add(button)
    return keyboard


def create_specialists_inline_keyboard(service_name):
    services = Service.objects.filter(
        category__icontains=service_name)
    specialists = Specialist.objects.filter(
        specialization__in=services).distinct()
    keyboard = telebot.types.InlineKeyboardMarkup()

    for specialist in specialists:
        button_text = f"{
            specialist.name} - {specialist.biography}"
        button = telebot.types.InlineKeyboardButton(
            text=button_text,
            callback_data=f"favoriteSpecialist_{specialist.id}"

        )
        keyboard.add(button)

    return keyboard


# Нет, это не капипаста - код выше треубет аргумент, нужно внимательно посмотреть на код в handlers.py

def create_only_specialists_inline_keyboard():
    specialists = Specialist.objects.all()
    keyboard = telebot.types.InlineKeyboardMarkup()

    for specialist in specialists:
        button_text = f"""{
            specialist.name} - {specialist.biography}"""
        button = telebot.types.InlineKeyboardButton(
            text=button_text,
            callback_data=f"favoriteSpecialist_{specialist.id}")
        keyboard.add(button)

    return keyboard
