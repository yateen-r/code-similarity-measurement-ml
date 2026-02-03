from django.urls import path
from . import views
from accounts import views as accounts_views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', accounts_views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/<str:token>/', accounts_views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Dashboard and Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Code Submissions
    path('upload/', views.upload_code_view, name='upload'),
    # alias expected by templates
    path('upload/', views.upload_code_view, name='upload_code'),
    path('submissions/', views.submissions_view, name='submissions'),
    path('submission/<uuid:submission_id>/', views.submission_detail_view, name='submission_detail'),
    path('submission/<uuid:submission_id>/delete/', views.delete_submission_view, name='delete_submission'),
    
    # Code Comparison
    path('compare/', views.compare_view, name='compare'),
    # alias expected by templates
    path('compare/', views.compare_view, name='compare_code'),
    path('comparisons/', views.comparisons_view, name='comparisons'),
    path('comparison/<uuid:comparison_id>/', views.comparison_detail_view, name='comparison_detail'),
    path('comparison/<uuid:comparison_id>/save/', views.save_comparison_view, name='save_comparison'),
    path('comparison/<uuid:comparison_id>/delete/', views.delete_comparison_view, name='delete_comparison'),
    
    # History
    path('history/', views.history_view, name='history'),
]
