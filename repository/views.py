from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponse, Http404
from django.db.models import Max
from django.db import transaction
from django.urls import reverse
from django.contrib import messages
import os

from .models import Repository, CodeFile, FileVersion
from .forms import RegistrationForm, RepositoryForm, FileUploadForm, FileVersionUploadForm


def home(request):
    """首页视图"""
    repositories = None
    if request.user.is_authenticated:
        # 获取用户的仓库并按最近更新时间排序，最多显示6个
        repositories = Repository.objects.filter(owner=request.user).order_by('-updated_at')[:6]
    return render(request, 'repository/home.html', {'repositories': repositories})


def register(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'repository/register.html', {'form': form})


@login_required
def repository_list(request):
    """仓库列表视图"""
    repositories = Repository.objects.filter(owner=request.user)
    return render(request, 'repository/repository_list.html', {
        'repositories': repositories
    })


@login_required
def create_repository(request):
    """创建仓库视图"""
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            repository = form.save(commit=False)
            repository.owner = request.user
            repository.save()
            messages.success(request, f'仓库 "{repository.name}" 创建成功！')
            return redirect('repository_detail', pk=repository.pk)
    else:
        form = RepositoryForm()
    return render(request, 'repository/create_repository.html', {'form': form})


@login_required
def repository_detail(request, pk):
    """仓库详情视图"""
    repository = get_object_or_404(Repository, pk=pk)
    # 检查权限
    if repository.owner != request.user:
        messages.error(request, '您没有权限访问此仓库。')
        return redirect('repository_list')
    
    files = repository.files.all()
    return render(request, 'repository/repository_detail.html', {
        'repository': repository,
        'files': files
    })


@login_required
def upload_file(request, repository_id):
    """上传文件视图"""
    repository = get_object_or_404(Repository, pk=repository_id)
    # 检查权限
    if repository.owner != request.user:
        messages.error(request, '您没有权限上传文件到此仓库。')
        return redirect('repository_list')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = form.cleaned_data['file_path']
            file = form.cleaned_data['file']
            commit_message = form.cleaned_data['commit_message']
            
            with transaction.atomic():
                # 尝试获取已存在的文件，如果不存在则创建
                code_file, created = CodeFile.objects.get_or_create(
                    repository=repository,
                    file_path=file_path,
                    defaults={'repository': repository}
                )
                
                # 获取最新版本号
                latest_version = code_file.versions.aggregate(Max('version_number'))
                next_version = 1
                if latest_version['version_number__max'] is not None:
                    next_version = latest_version['version_number__max'] + 1
                
                # 创建新版本
                file_version = FileVersion(
                    code_file=code_file,
                    version_number=next_version,
                    file=file,
                    commit_message=commit_message,
                    uploader=request.user
                )
                file_version.save()
            
            messages.success(request, f'文件 "{file_path}" 上传成功！')
            return redirect('repository_detail', pk=repository.pk)
    else:
        form = FileUploadForm()
    
    return render(request, 'repository/upload_file.html', {
        'form': form,
        'repository': repository
    })


@login_required
def file_detail(request, repository_id, file_id):
    """文件详情视图"""
    repository = get_object_or_404(Repository, pk=repository_id)
    # 检查权限
    if repository.owner != request.user:
        messages.error(request, '您没有权限访问此文件。')
        return redirect('repository_list')
    
    code_file = get_object_or_404(CodeFile, pk=file_id, repository=repository)
    versions = code_file.versions.all()
    
    return render(request, 'repository/file_detail.html', {
        'repository': repository,
        'code_file': code_file,
        'versions': versions
    })


@login_required
def upload_new_version(request, repository_id, file_id):
    """上传新版本视图"""
    repository = get_object_or_404(Repository, pk=repository_id)
    # 检查权限
    if repository.owner != request.user:
        messages.error(request, '您没有权限上传文件到此仓库。')
        return redirect('repository_list')
    
    code_file = get_object_or_404(CodeFile, pk=file_id, repository=repository)
    
    if request.method == 'POST':
        form = FileVersionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            commit_message = form.cleaned_data['commit_message']
            
            # 获取最新版本号
            latest_version = code_file.versions.aggregate(Max('version_number'))
            next_version = 1
            if latest_version['version_number__max'] is not None:
                next_version = latest_version['version_number__max'] + 1
            
            # 创建新版本
            file_version = FileVersion(
                code_file=code_file,
                version_number=next_version,
                file=file,
                commit_message=commit_message,
                uploader=request.user
            )
            file_version.save()
            
            messages.success(request, f'文件 "{code_file.file_path}" 新版本上传成功！')
            return redirect('file_detail', repository_id=repository.pk, file_id=code_file.pk)
    else:
        form = FileVersionUploadForm()
    
    return render(request, 'repository/upload_new_version.html', {
        'form': form,
        'repository': repository,
        'code_file': code_file
    })


@login_required
def download_file(request, version_id):
    """下载文件视图"""
    file_version = get_object_or_404(FileVersion, pk=version_id)
    
    # 检查权限
    if file_version.code_file.repository.owner != request.user:
        messages.error(request, '您没有权限下载此文件。')
        return redirect('repository_list')
    
    try:
        file_path = file_version.file.path
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_version.get_file_name()}"'
            return response
    except:
        raise Http404("文件不存在") 