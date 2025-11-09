from django.contrib import admin

from .models import Run, User

admin.site.register(Run)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    
    list_display = ["username", "is_staff"]
    
    
