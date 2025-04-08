from django.urls import path, include
from .views import *
from . import views


urlpatterns = [
    path('', ProjectsView.as_view(), name='projects'),
    path('add/', AddProject.as_view(), name='add_project'),
    path('edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('delete/<int:pk>/', DeleteProject.as_view(), name='delete_project'),
    path('project_details/<int:pk>/', ProjectDetails.as_view(), name='project_details'),
    path('tasks/', Tasks.as_view(), name='tasks'),
    path('task/add_task/', Createtask.as_view(), name='add_task'),
    path('task/edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('task/delete/<int:pk>/', Deletetask.as_view(), name='delete_task'),
    path('task/task_details/<int:pk>/', ViewTask.as_view(), name='task_details'),
    path('task/task_details/add_comment/', CreateComment.as_view(), name='add_comment'),
    path('task/task_details/edit_comment/<int:pk>/', UpdateComment.as_view(), name='edit_comment'),
    path('task/task_details/delete_comment/<int:pk>/', DeleteComment.as_view(), name='delete_comment'),
    path('email/', email_report, name='email_report'),
]