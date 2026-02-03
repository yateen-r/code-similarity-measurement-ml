from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<uuid:request_id>/', views.generate_report_view, name='generate_report'),
    path('download/<uuid:report_id>/', views.download_report_view, name='download_report'),
    path('my-reports/', views.my_reports_view, name='my_reports'),
]
