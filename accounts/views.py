from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
import uuid
from datetime import timedelta
from .models import CustomUser, PasswordResetToken, UserActivity
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileUpdateForm,
    PasswordResetRequestForm, PasswordResetForm
)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, activity_type, description, request):
    """Log user activity"""
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )


class RegisterView(CreateView):
    """User registration view"""
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.user_type = 'user'
        user.save()
        
        messages.success(
            self.request,
            'Registration successful! You can now login with your credentials.'
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


class LoginView(FormView):
    """User login view"""
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_admin_user():
                return redirect('admins:dashboard')
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if user.is_blocked:
                messages.error(self.request, 'Your account has been blocked. Please contact administrator.')
                return redirect('accounts:login')
            
            login(self.request, user)
            user.last_login_ip = get_client_ip(self.request)
            user.save()
            
            log_activity(user, 'login', f'User logged in from {get_client_ip(self.request)}', self.request)
            
            messages.success(self.request, f'Welcome back, {user.username}!')
            
            if user.is_admin_user():
                return redirect('admins:dashboard')
            return redirect('users:dashboard')
        else:
            messages.error(self.request, 'Invalid username or password.')
            return redirect('accounts:login')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required
def logout_view(request):
    """User logout view"""
    log_activity(request.user, 'logout', 'User logged out', request)
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'profile_update', 'User updated profile information', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'recent_activities': UserActivity.objects.filter(user=request.user)[:10]
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            log_activity(request.user, 'profile_update', 'User changed password', request)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
    
    return render(request, 'accounts/change_password.html')


def password_reset_request_view(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                
                # Create reset token
                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(hours=24)
                
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )
                
                # Send email (console backend for now)
                print(f"Password reset link: http://localhost:8000/accounts/password-reset/{token}/")
                
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('accounts:login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token):
    """Password reset confirmation view"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(request, 'This reset link has expired or already been used.')
            return redirect('accounts:login')
        
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                reset_token.is_used = True
                reset_token.save()
                
                messages.success(request, 'Password has been reset successfully! You can now login.')
                return redirect('accounts:login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'token': token})
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('accounts:login')
