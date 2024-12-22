from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta


class Service(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=200, null=True,
                                choices=[
                                    ('Стрижка волос', 'Стрижка волос'),
                                    ('Борода', 'Борода'),
                                    ('Укладка волос', 'Укладка волос'),
                                    ('Окрашивание волос', 'Окрашивание волос'),
                                    ('Уход за лицом', 'Уход за лицом'),
                                ])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(
        help_text="Продолжительность услуги в минутах")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.category


class Specialist(models.Model):
    name = models.CharField(max_length=200, null=True)
    biography = models.CharField(max_length=200, null=True, blank=True)
    specialization = models.ManyToManyField(
        Service, related_name="specialists")
    # rating - можно добавить в дальнейшем

    def __str__(self):
        return str(self.name)


class Salon(models.Model):
    name = models.CharField(max_length=200)
    specialists = models.ManyToManyField(Specialist, related_name="salons")
    location = models.TextField(null=True)
    phone_number = models.CharField(max_length=12, unique=True)
    tg_id = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return self.name


class WorkingHour(models.Model):
    specialist = models.ForeignKey(
        Specialist, on_delete=models.CASCADE, related_name="working_hours", null=True)
    days_of_week = models.CharField(
        max_length=11,
        choices=[
            ("Понедельник", "Понедельник"),
            ("Вторник", "Вторник"),
            ("Среда", "Среда"),
            ("Четверг", "Четверг"),
            ("Пятница", "Пятница"),
            ("Суббота", "Суббота"),
            ("Воскресенье", "Воскресенье"),
        ]
    )
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.days_of_week}: {self.open_time} - {self.close_time}"


class Appointment(models.Model):
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=12)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, related_name="appointments")
    salon = models.ForeignKey(
        Salon, on_delete=models.CASCADE, null=True, related_name="appointments")
    location = models.CharField(max_length=100)
    specialist = models.ForeignKey(
        Specialist, on_delete=models.CASCADE, null=True, related_name="appointments")
    start_session = models.DateTimeField()
    end_session = models.DateTimeField()

    def clean(self):
        """Чекаем на доступность временного слота"""
        overlapping_appointments = Appointment.objects.filter(
            specialist=self.specialist,
            start_session__lt=self.end_session,
            end_session__gt=self.start_session,
        ).exclude(pk=self.pk)  # Здесь мы и фильтруем
        if overlapping_appointments.exists():
            raise ValidationError(
                f"""Мастер {
                    self.specialist.name} - уже занят наа это время."""
            )

    def save(self, *args, **kwargs):
        self.clean()  # здесь мы валидируем инфу перед тем как финально все сохрнить в бд
        super().save(*args, **kwargs)

        Notification.objects.update_or_create(
            appointment=self,
            message=f"""{
                self.client_name}! Уже прошло 100 дней, а Вас все нет и нет :c""",
            send_at=self.end_session + timedelta(seconds=10),
            defaults={'status': "Не отправлено"}
        )            # Собственно уведомления

    def __str__(self):
        return self.client_name

    class Meta:
        ordering = ['-start_session', '-end_session']


class Payment(models.Model):
    # Модель для инфы о платежах

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, null=True, related_name="payments")
    specialist = models.ForeignKey(
        Specialist, on_delete=models.CASCADE, null=True, related_name="payments")
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=100, null=True, choices=[
        ("Оплачено", "Оплачено"),
        ("Не оплачено", "Не оплачено")
    ])

    def __str__(self):
        return f"{self.payment_method} - {self.status}"


class Notification(models.Model):
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, null=True, related_name="notifications")
    message = models.TextField(null=True, blank=True)
    send_at = models.DateTimeField()
    status = models.CharField(max_length=100, null=True, choices=[
        ("Отправлено", "Отправлено"),
        ("Не отправлено", "Не отправлено")
    ])

    def __str__(self):
        return self.message

    class Meta:
        ordering = ['-send_at']


class SalonManager(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=12, unique=True, null=True)
    salon = models.ForeignKey(
        Salon, on_delete=models.CASCADE, related_name="salon_managers", null=True)

    def __str__(self):
        return self.name
