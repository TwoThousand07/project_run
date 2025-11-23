from django.contrib import admin

from .models import Run, AthleteInfo, Challenge

admin.site.register(Run)
admin.site.register(AthleteInfo)
admin.site.register(Challenge)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
    
#     list_display = ["username", "is_staff"]
    
    
