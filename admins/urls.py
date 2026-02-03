from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('submissions/', views.admin_submissions, name='submissions'),
    path('submissions/<int:submission_id>/delete/', views.delete_submission, name='delete_submission'),
    path('comparisons/', views.admin_comparisons, name='comparisons'),
    path('comparisons/<int:comparison_id>/delete/', views.delete_comparison, name='delete_comparison'),
    path('statistics/', views.admin_statistics, name='statistics'),
]
