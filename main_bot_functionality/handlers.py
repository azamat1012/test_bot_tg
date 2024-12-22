from datetime import datetime, timedelta
from main_bot_functionality.models import Salon, Specialist, WorkingHour, Service, SalonManager, Appointment

from keyboards import (create_consent_keyboard,
                       create_first_keyboard, create_second_keyboard,
                       create_salons_inline_keyboard,
                       create_salons_inline_keyboard, create_services_inline_keyboard, create_salons_keyboard_for_call,
                       create_specialists_inline_keyboard, create_only_specialists_inline_keyboard, create_day_keyboard,
                       create_services_inline_keyboard)
from helpers import parse_callback_data, get_free_sessions

import telebot
from django.utils import timezone
from django.utils.timezone import make_aware


user_data = {}


# Обработчик команды /start
def handle_start(bot: telebot.TeleBot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        with open('agreement.txt', 'rb') as file:
            bot.send_document(message.chat.id, file)
        bot.send_message(message.chat.id, "Для продолжения работы с ботом необходимо принять соглашение "
                                          "об обработке персональных данных."
                         " Прочтите соглашение и нажмите кнопку 'Принять'.",
                         reply_markup=create_consent_keyboard()
                         )
        print(f"Бот запущен пользователем: {message.chat.id}")


def handle_callbacks(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        try:
            chat_id = call.message.chat.id
            user_action = call.data
            if user_action == 'accept':
                bot.send_message(call.message.chat.id, "Спасибо! Вы приняли соглашение. Теперь вы можете продолжить.",
                                 reply_markup=create_first_keyboard())

            elif user_action == 'reject':
                bot.send_message(call.message.chat.id,
                                 "Вы не приняли соглашение. Для продолжения работы с ботом необходимо дать согласие.")

            elif user_action.startswith('callSalon_'):
                salon_name = parse_callback_data(user_action)[1]

                chosen_manager = SalonManager.objects.filter(
                    salon__name__icontains=salon_name
                ).first()

                if chosen_manager:
                    bot.send_message(
                        call.message.chat.id,
                        f"""Вам звонить сюда:\n {
                            chosen_manager.name} - {chosen_manager.phone_number}"""
                    )

                else:
                    bot.send_message(
                        call.message.chat.id,
                        f"Для салона '{salon_name}' не найден менеджер."
                    )

            elif user_action.startswith('manager_'):
                manager_id = parse_callback_data(user_action)[1]
                chosen_manager = SalonManager.objects.filter(
                    id=manager_id).first()
                bot.send_message(call.message.chat.id, "Подскажите, какой салон Вас интересует?",
                                 "Успех")

            elif user_action.startswith("salons_"):
                salon_id = parse_callback_data(user_action)[1]
                chosen_salon = Salon.objects.filter(id=salon_id).first()
                if chosen_salon:
                    if chat_id not in user_data:
                        user_data[chat_id] = {}
                    user_data[chat_id]['salon'] = chosen_salon
                    bot.send_message(call.message.chat.id,
                                     f"Вы выбрали салон: {chosen_salon.name}.\nПожалуйста, выберите услугу:", reply_markup=create_services_inline_keyboard())
                else:
                    bot.send_message(call.message.chat.id, "Салон не найден.")

            elif user_action.startswith("favoriteSpecialist_") or user_action.startswith("specialist_"):
                specialist_id = parse_callback_data(user_action)[1]
                try:
                    chosen_specialist = Specialist.objects.get(
                        id=specialist_id)
                    if chosen_specialist:
                        if chat_id in user_data:
                            user_data[chat_id]['specialist'] = chosen_specialist

                    weekly_schedule = get_free_sessions(specialist_id)
                    working_days = [
                        day for day, schedule in weekly_schedule.items() if schedule != "Не работает"]
                    message = f"Вы выбрали специалиста: {
                        chosen_specialist.name}\n\n"
                    message += "Расписание на неделю:\nПожалуйста, выберите время:\n"
                    for day, schedule in weekly_schedule.items():
                        message += f"{day}: {schedule}\n"

                    bot.send_message(
                        call.message.chat.id,
                        message,
                        reply_markup=create_day_keyboard(working_days)
                    )
                except Specialist.DoesNotExist:
                    bot.send_message(call.message.chat.id,
                                     "Специалист не найден.")

            elif user_action.startswith("day_"):
                selected_day = user_action.split('_')[1]
                bot.send_message(call.message.chat.id, f"""Вы выбрали день: {
                                 selected_day}. Пожалуйста, укажите время (например, 13:10).""")
                bot.register_next_step_handler(
                    call.message, process_time_input, bot, selected_day

                )

            elif user_action.startswith("service_"):
                service_name = parse_callback_data(user_action)[1]
                service = Service.objects.get(name__icontains=service_name)
                if service:
                    if chat_id in user_data:
                        user_data[chat_id]['service'] = service
                bot.send_message(
                    call.message.chat.id,
                    f"""Вы выбрали услугу: {
                        service.category}\nВыберите специалиста:""",
                    reply_markup=create_specialists_inline_keyboard(
                        service_name)
                )
            print(f"Пользователь: {call.message.chat.id}: {user_action} ")

        except Exception as e:
            bot.send_message(call.message.chat.id,
                             "Произошла ошибка. Повторите попытку позже.")

            print(f"this mistake from the call back: {e}")


def handle_messages(bot: telebot.TeleBot):
    @bot.message_handler(func=lambda message: True)
    def handler_message(message):

        if message.text == "Хочу записаться по номеру телефона":
            bot.send_message(message.chat.id, "Подскажите, какой салон Вас интересует?",
                             reply_markup=create_salons_keyboard_for_call())

        elif message.text == "Выбрать салон":
            bot.send_message(message.chat.id, "Далее вы можете узнать цены на процедуры или записаться по времени",
                             reply_markup=create_second_keyboard())

        elif message.text == 'Прайс на процедуры':
            services = Service.objects.all()
            if not services:
                bot.send_message(message.chat.id, "Список услуг пуст.")
            else:
                response = "Прайс на процедуры:\n\n"
                for service in services:
                    response += f"""{service.category}\nЦена:{service.price} руб.\nДлительность:{
                        service.duration}  минут\nОписание{service.description}\n\n"""
                bot.send_message(message.chat.id, response)

        elif message.text == 'Назад':
            bot.send_message(message.chat.id, "Вы вернулись в Главное Меню",
                             reply_markup=create_first_keyboard())

        elif message.text == 'Наши салоны':
            bot.send_message(message.chat.id, "Выберите салон:",
                             reply_markup=create_salons_inline_keyboard())

        elif message.text == "Выбрать любимого специалиста":
            bot.send_message(message.chat.id, "Наши специалисты",
                             reply_markup=create_only_specialists_inline_keyboard())

        elif message.text == 'Запись по времени':
            bot.send_message(message.chat.id, "Выберите салон, который Вас интересует?",
                             reply_markup=create_salons_inline_keyboard())


def collect_client_name(message, bot, selected_day, chosen_time):
    bot.send_message(message.chat.id, "Пожалуйста, укажите своё имя.")
    bot.register_next_step_handler(
        message, process_client_name, bot, selected_day, chosen_time)


def process_client_name(message, bot, selected_day, chosen_time):
    client_name = message.text.strip()
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    user_data[message.chat.id]['client_name'] = client_name

    bot.send_message(message.chat.id, "Укажите свой номер телефона.")
    bot.register_next_step_handler(
        message, process_client_phone, bot, selected_day, chosen_time)


def process_client_phone(message, bot, selected_day, chosen_time):
    client_phone = message.text.strip()
    if message.chat.id in user_data:
        user_data[message.chat.id]['client_phone'] = client_phone
    confirm_booking_prompt(message, bot, selected_day, chosen_time)


def get_main_info_about_user(message):
    user_info = user_data.get(message.chat.id, {})
    client_name = user_info.get("client_name", "net")
    client_phone = user_info.get("client_phone", "net")
    service = user_info.get("service", "net")
    salon = user_info.get("salon", "net")
    specialist = user_info.get("specialist", "net")
    return client_name, client_phone, service, salon, specialist


def process_time_input(message, bot, selected_day):
    try:
        client_name, client_phone, service, salon, specialist = get_main_info_about_user(
            message)
        print(f"Debug - Service: {service}, Type: {type(service)}")
        chosen_time_str = message.text.strip()

        if not isinstance(service, Service):
            bot.send_message(
                message.chat.id,
                "Услуга не выбрана или неверная. Пожалуйста, выберите услугу снова."
            )
            return
        chosen_time_str = message.text.strip()
        service_duration = service.duration if service else 30
        try:
            chosen_time = datetime.strptime(chosen_time_str, "%H:%M").time()
        except ValueError:
            bot.send_message(
                message.chat.id,
                "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ."
            )
            bot.register_next_step_handler(
                message, process_time_input, bot, selected_day)
            return

        working_hours = WorkingHour.objects.filter(
            days_of_week__icontains=selected_day
        )

        valid_time = any(
            wh.open_time <= chosen_time <= wh.close_time for wh in working_hours
        )

        if not valid_time:
            bot.send_message(
                message.chat.id,
                f"Выбранное время {chosen_time.strftime(
                    '%H:%M')} выходит за пределы рабочего времени. "
                "Попробуйте выбрать другое время в пределах рабочего дня."
            )
            bot.register_next_step_handler(
                message, process_time_input, bot, selected_day)
            return

        # возможно есть другие варинаты как это можно реализовать
        chosen_datetime = datetime.combine(datetime.today(), chosen_time)
        chosen_datetime = timezone.make_aware(chosen_datetime)
        end_datetime = chosen_datetime + timedelta(minutes=service_duration)
        end_datetime = end_datetime

        # Проверка на свободный слот
        overlapping_appointments = Appointment.objects.filter(
            specialist=specialist,
            start_session__lt=end_datetime,
            end_session__gt=chosen_datetime
        )

        if overlapping_appointments.exists():
            bot.send_message(
                message.chat.id,
                "Извините, этот временной слот уже занят. Попробуйте выбрать другое время."
            )
            bot.register_next_step_handler(
                message, process_time_input, bot, selected_day
            )
            return
        bot.send_message(
            message.chat.id,
            f"Вы выбрали время: {chosen_time.strftime('%H:%M')} на {
                selected_day}."
        )
        collect_client_name(message, bot, selected_day, chosen_time)

    except Exception as e:
        bot.send_message(
            message.chat.id, "Произошла ошибка. Попробуйте снова или обратитесь к администратору."
        )
        print(f"Ошибка: {e}")


def confirm_booking_prompt(message, bot, selected_day, chosen_time):
    client_name, client_phone, service, salon, specialist = get_main_info_about_user(
        message)
    bot.send_message(message.chat.id,
                     f"Пожалуйста, подтвердите бронирование:\n"
                     f"День: {selected_day}\n"
                     f"Время: {chosen_time.strftime('%H:%M')}\n"
                     f"Имя клиента: {client_name}\n"
                     f"Телефон: {client_phone}\n"
                     f"Салон: {salon.name}\n"
                     f"Адрес: {salon.location}\n"
                     f"Специалист: {specialist}\n"
                     f"Услуга: {service}\n\n"
                     f"Подтвердите, пожалуйста, ваше бронирование. Напишите 'да' для подтверждения или 'нет' для отмены."
                     )
    bot.register_next_step_handler(
        message, confirm_booking, bot, selected_day, chosen_time
    )


def confirm_booking(message, bot, selected_day, chosen_time):
    user_response = message.text.strip().lower()

    if user_response in ['да', 'yes']:
        user_info = user_data.get(message.chat.id, {})
        client_name = user_info.get("client_name", "Не указано")
        client_phone = user_info.get("client_phone", "0000000000")
        service = user_info.get("service")
        salon = user_info.get("salon")
        specialist = user_info.get("specialist")

        start_datetime = make_aware(
            datetime.combine(datetime.now().date(), chosen_time)
        )
        service_duration = service.duration if service else 30
        end_datetime = start_datetime + timedelta(minutes=service_duration)

        # чек на свободный слот
        overlapping_appointments = Appointment.objects.filter(
            specialist=specialist,
            start_session__lt=end_datetime,
            end_session__gt=start_datetime
        )

        if overlapping_appointments.exists():
            bot.send_message(
                message.chat.id,
                "Извините, этот временной слот уже занят. Попробуйте выбрать другое время."
            )
            return

        # Сохрняем в бд если все ок
        appointment = Appointment(
            client_name=client_name,
            client_phone=client_phone,
            service=service,
            salon=salon,
            location=salon.location if salon else "Не указано",
            specialist=specialist,
            start_session=start_datetime,
            end_session=end_datetime,
        )
        appointment.save()

        bot.send_message(
            message.chat.id,
            f"Бронирование подтверждено! Вы записаны на {chosen_time.strftime('%H:%M')} с {
                specialist}."
        )
    elif user_response in ['нет', 'no']:
        bot.send_message(
            message.chat.id,
            "Бронирование отменено."
        )
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, введите 'да' для подтверждения или 'нет' для отмены."
        )
        bot.register_next_step_handler(
            message, confirm_booking, bot, selected_day, chosen_time
        )
