from django.contrib import admin
from .models import Repository, CodeFile, FileVersion


class FileVersionInline(admin.TabularInline):
    """文件版本内联管理"""
    model = FileVersion
    extra = 0
    readonly_fields = ['created_at', 'get_file_size']
    fields = ['version_number', 'file', 'commit_message', 'uploader', 'created_at']


class CodeFileAdmin(admin.ModelAdmin):
    """代码文件管理"""
    list_display = ['file_path', 'repository', 'created_at', 'updated_at']
    list_filter = ['repository']
    search_fields = ['file_path']
    inlines = [FileVersionInline]


class CodeFileInline(admin.TabularInline):
    """代码文件内联管理"""
    model = CodeFile
    extra = 0
    fields = ['file_path', 'created_at']
    readonly_fields = ['created_at']


class RepositoryAdmin(admin.ModelAdmin):
    """代码仓库管理"""
    list_display = ['name', 'owner', 'created_at', 'updated_at']
    list_filter = ['owner']
    search_fields = ['name', 'description']
    inlines = [CodeFileInline]


admin.site.register(Repository, RepositoryAdmin)
admin.site.register(CodeFile, CodeFileAdmin)
admin.site.register(FileVersion) 