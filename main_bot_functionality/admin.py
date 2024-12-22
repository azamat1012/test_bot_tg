from django.contrib import admin
from main_bot_functionality.models import Specialist, Appointment, Payment, Notification, SalonManager, Salon, WorkingHour, Service


class WorkingHourInline(admin.TabularInline):
    model = WorkingHour
    extra = 1


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    inlines = [WorkingHourInline]


admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(Notification)
admin.site.register(SalonManager)
admin.site.register(Service)
admin.site.register(Salon)
