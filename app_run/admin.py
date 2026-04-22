from django.contrib import admin

from .models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscripe


class RunAdmin(admin.ModelAdmin):
    list_display = ("athlete", "created_at", "distance", "status", "speed")


admin.site.register(Run, RunAdmin)
admin.site.register(AthleteInfo)
admin.site.register(Challenge)
admin.site.register(Position)
admin.site.register(CollectibleItem)
admin.site.register(Subscripe)
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):

#     list_display = ["username", "is_staff"]
