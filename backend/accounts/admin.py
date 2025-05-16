from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # 一覧表示の設定
    list_display = ('username', 'email', 'university_id', 'is_staff')
    search_fields = ('username', 'email', 'university_id')

    # 編集画面のフィールド追加
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('university_id', 'university_password')}),
    )

    # 追加画面のフィールド追加
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('university_id', 'university_password')}),
    )
