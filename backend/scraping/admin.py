from django.contrib import admin
from .models import Assignment, Course

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'user', 'due_date', 'is_submitted')
    list_filter = ('user', 'course')
    search_fields = ('title', 'course__title')
    ordering = ('user', 'course', 'due_date')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'day_of_week', 'period')
    list_filter = ('user', 'day_of_week', 'period')
    search_fields = ('title',)
    ordering = ('user', 'title')


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Course, CourseAdmin)