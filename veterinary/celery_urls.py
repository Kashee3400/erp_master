# urls.py (for your app)
from django.urls import path
from .views.celery_views import (
    TasksAPIView,
    ScheduledTasksAPIView,
    ReservedTasksAPIView,
    TaskDetailAPIView,
    WorkerStatsAPIView,
    RegisteredTasksAPIView,
    TaskControlAPIView,
    QueueLengthAPIView,
    TaskHistoryAPIView,
    CeleryDashboardAPIView,
    WorkerControlAPIView,
    TasksByNameAPIView,
    QueueControlAPIView,
)

app_name = 'celery_monitor'

urlpatterns = [
    # Task monitoring endpoints
    path('tasks/active/', TasksAPIView.as_view(), name='active-tasks'),
    path('tasks/scheduled/', ScheduledTasksAPIView.as_view(), name='scheduled-tasks'),
    path('tasks/reserved/', ReservedTasksAPIView.as_view(), name='reserved-tasks'),
    path('tasks/<str:task_id>/', TaskDetailAPIView.as_view(), name='task-detail'),
    path('tasks/control/', TaskControlAPIView.as_view(), name='task-control'),
    path('tasks/history/', TaskHistoryAPIView.as_view(), name='task-history'),

    # Worker monitoring endpoints
    path('workers/stats/', WorkerStatsAPIView.as_view(), name='worker-stats'),
    path('workers/registered-tasks/', RegisteredTasksAPIView.as_view(), name='registered-tasks'),

    # Queue monitoring endpoints
    path('queues/length/', QueueLengthAPIView.as_view(), name='queue-length'),
    path('dashboard/', CeleryDashboardAPIView.as_view(), name='celery-dashboard'),
    path('worker-control/', WorkerControlAPIView.as_view(), name='worker-control'),
    path('queue-control/', QueueControlAPIView.as_view(), name='queue-control'),
    path("tasks/<str:task_name>/", TasksByNameAPIView.as_view(), name="tasks-by-name"
         ),
]
