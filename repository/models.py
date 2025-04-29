from django.db import models
from django.contrib.auth.models import User
import os


class Repository(models.Model):
    """代码仓库模型"""
    name = models.CharField('仓库名称', max_length=100)
    description = models.TextField('仓库描述', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories', verbose_name='所有者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '代码仓库'
        verbose_name_plural = '代码仓库'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def get_upload_path(self):
        """获取上传路径"""
        return os.path.join('uploads', str(self.id))


class CodeFile(models.Model):
    """代码文件模型"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='files', verbose_name='所属仓库')
    file_path = models.CharField('文件路径', max_length=255)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '代码文件'
        verbose_name_plural = '代码文件'
        ordering = ['file_path']
        unique_together = ['repository', 'file_path']  # 每个仓库中文件路径唯一

    def __str__(self):
        return self.file_path

    def get_latest_version(self):
        """获取最新版本"""
        return self.versions.order_by('-version_number').first()


def file_upload_path(instance, filename):
    """确定文件上传路径"""
    # 上传到 /media/uploads/仓库id/文件id/版本号_文件名
    return os.path.join(
        'uploads',
        str(instance.code_file.repository.id),
        str(instance.code_file.id),
        f"{instance.version_number}_{filename}"
    )


class FileVersion(models.Model):
    """文件版本模型"""
    code_file = models.ForeignKey(CodeFile, on_delete=models.CASCADE, related_name='versions', verbose_name='代码文件')
    version_number = models.PositiveIntegerField('版本号')
    file = models.FileField('文件', upload_to=file_upload_path)
    commit_message = models.TextField('提交信息', blank=True)
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploads', verbose_name='上传者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '文件版本'
        verbose_name_plural = '文件版本'
        ordering = ['-version_number']
        unique_together = ['code_file', 'version_number']  # 确保版本号对每个文件是唯一的

    def __str__(self):
        return f"{self.code_file.file_path} - v{self.version_number}"

    def get_file_size(self):
        """获取文件大小"""
        try:
            return self.file.size
        except:
            return 0

    def get_file_name(self):
        """获取文件名"""
        return os.path.basename(self.file.name) 