from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 首页和用户认证
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='repository/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 仓库管理
    path('repositories/', views.repository_list, name='repository_list'),
    path('repositories/create/', views.create_repository, name='create_repository'),
    path('repositories/<int:pk>/', views.repository_detail, name='repository_detail'),
    
    # 文件管理
    path('repositories/<int:repository_id>/upload/', views.upload_file, name='upload_file'),
    path('repositories/<int:repository_id>/files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('repositories/<int:repository_id>/files/<int:file_id>/upload/', views.upload_new_version, name='upload_new_version'),
    path('files/version/<int:version_id>/download/', views.download_file, name='download_file'),
] 