from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Repository, CodeFile, FileVersion


class RegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True, label='电子邮箱')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': '用户名',
        }


class RepositoryForm(forms.ModelForm):
    """仓库创建表单"""
    class Meta:
        model = Repository
        fields = ['name', 'description']
        labels = {
            'name': '仓库名称',
            'description': '仓库描述',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class FileUploadForm(forms.Form):
    """文件上传表单"""
    file = forms.FileField(label='文件')
    file_path = forms.CharField(max_length=255, label='文件路径')
    commit_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label='提交信息'
    )


class FileVersionUploadForm(forms.ModelForm):
    """文件版本上传表单"""
    class Meta:
        model = FileVersion
        fields = ['file', 'commit_message']
        labels = {
            'file': '文件',
            'commit_message': '提交信息'
        }
        widgets = {
            'commit_message': forms.Textarea(attrs={'rows': 2}),
        } 