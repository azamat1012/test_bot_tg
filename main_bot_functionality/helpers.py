from main_bot_functionality.models import Salon, Specialist, Service, SalonManager, WorkingHour, Appointment


def get_free_sessions(specialist_id):
    """Возвращаем недельный график спеца"""
    all_days = [
        "Понедельник", "Вторник", "Среда",
        "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]
    week_schedule = {day: "Не работает" for day in all_days}

    working_hours = WorkingHour.objects.filter(
        specialist__id=specialist_id
    ).order_by("days_of_week")

    for wh in working_hours:
        day = wh.days_of_week
        start_time = wh.open_time.strftime('%H:%M')
        end_time = wh.close_time.strftime('%H:%M')
        if week_schedule[day] == "Не работает":
            week_schedule[day] = f"{start_time} - {end_time}"
        else:
            week_schedule[day] += f", {start_time} - {end_time}"
    return week_schedule


# -------------

def parse_callback_data(data, expected_parts=2):
    return data.split("_", expected_parts - 1)
