from django.contrib import admin

from .models import Run, AthleteInfo, Challenge, Position

admin.site.register(Run)
admin.site.register(AthleteInfo)
admin.site.register(Challenge)
admin.site.register(Position)
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):

#     list_display = ["username", "is_staff"]
