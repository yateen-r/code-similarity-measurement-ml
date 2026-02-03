from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

# Import models
from accounts.models import CustomUser
from users.models import CodeSubmission, ComparisonRequest, SimilarityResult


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    
    if CodeSubmission is None:
        messages.error(request, 'Models not properly configured.')
        return redirect('users:dashboard')
    
    # Get statistics
    total_users = CustomUser.objects.count()
    total_submissions = CodeSubmission.objects.count()
    total_comparisons = ComparisonRequest.objects.count()
    
    completed_comparisons = ComparisonRequest.objects.filter(status='completed').count()
    
    # Recent activity
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_submissions = CodeSubmission.objects.order_by('-created_at')[:10]
    
    recent_comparisons = ComparisonRequest.objects.order_by('-created_at')[:10]
    
    # Language distribution
    language_stats = CodeSubmission.objects.values('language').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Similarity distribution
    high_similarity = 0
    medium_similarity = 0
    low_similarity = 0
    
    if SimilarityResult:
        high_similarity = SimilarityResult.objects.filter(
            overall_similarity_score__gte=75
        ).count()
        medium_similarity = SimilarityResult.objects.filter(
            overall_similarity_score__gte=50,
            overall_similarity_score__lt=75
        ).count()
        low_similarity = SimilarityResult.objects.filter(
            overall_similarity_score__lt=50
        ).count()
    
    # User activity in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    active_users = CustomUser.objects.filter(last_login__gte=week_ago).count()
    
    context = {
        'total_users': total_users,
        'total_submissions': total_submissions,
        'total_comparisons': total_comparisons,
        'completed_comparisons': completed_comparisons,
        'recent_users': recent_users,
        'recent_submissions': recent_submissions,
        'recent_comparisons': recent_comparisons,
        'language_stats': language_stats,
        'high_similarity': high_similarity,
        'medium_similarity': medium_similarity,
        'low_similarity': low_similarity,
        'active_users': active_users,
    }
    
    return render(request, 'admins/dashboard.html', context)


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def admin_users(request):
    """Manage users"""
    users = CustomUser.objects.annotate(
        submission_count=Count('submissions')
    ).order_by('-date_joined')
    
    context = {
        'users': users,
    }
    
    return render(request, 'admins/users.html', context)


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def admin_submissions(request):
    """View all submissions"""
    if CodeSubmission is None:
        messages.error(request, 'Models not properly configured.')
        return redirect('users:dashboard')
    
    submissions = CodeSubmission.objects.select_related('user').order_by('-created_at')
    
    context = {
        'submissions': submissions,
    }
    
    return render(request, 'admins/submissions.html', context)


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def admin_comparisons(request):
    """View all comparisons"""
    comparisons = ComparisonRequest.objects.select_related('user').order_by('-created_at')
    
    context = {
        'comparisons': comparisons,
    }
    
    return render(request, 'admins/comparisons.html', context)


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def admin_statistics(request):
    """Detailed statistics"""
    
    if CodeSubmission is None:
        messages.error(request, 'Models not properly configured.')
        return redirect('users:dashboard')
    
    # Time-based statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'today': {
            'submissions': CodeSubmission.objects.filter(created_at__date=today).count(),
            'comparisons': ComparisonRequest.objects.filter(created_at__date=today).count(),
            'users': CustomUser.objects.filter(date_joined__date=today).count(),
        },
        'week': {
            'submissions': CodeSubmission.objects.filter(created_at__date__gte=week_ago).count(),
            'comparisons': ComparisonRequest.objects.filter(created_at__date__gte=week_ago).count(),
            'users': CustomUser.objects.filter(date_joined__date__gte=week_ago).count(),
        },
        'month': {
            'submissions': CodeSubmission.objects.filter(created_at__date__gte=month_ago).count(),
            'comparisons': ComparisonRequest.objects.filter(created_at__date__gte=month_ago).count(),
            'users': CustomUser.objects.filter(date_joined__date__gte=month_ago).count(),
        },
    }
    
    # Average similarity scores
    avg_similarity = 0
    if SimilarityResult:
        result = SimilarityResult.objects.aggregate(avg_score=Avg('overall_similarity_score'))
        avg_similarity = result['avg_score'] or 0
    
    # Most active users
    active_users = CustomUser.objects.annotate(
        total_submissions=Count('submissions')
    ).order_by('-total_submissions')[:10]
    
    context = {
        'stats': stats,
        'avg_similarity': avg_similarity,
        'active_users': active_users,
    }
    
    return render(request, 'admins/statistics.html', context)


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def delete_user(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} has been deleted.')
    
    return redirect('admins:users')


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def delete_submission(request, submission_id):
    """Delete a submission"""
    if request.method == 'POST':
        if CodeSubmission:
            submission = get_object_or_404(CodeSubmission, id=submission_id)
            submission.delete()
            messages.success(request, 'Submission deleted successfully.')
    
    return redirect('admins:submissions')


@login_required
@user_passes_test(is_superuser, login_url='/users/dashboard/')
def delete_comparison(request, comparison_id):
    """Delete a comparison"""
    if request.method == 'POST':
        comparison = get_object_or_404(ComparisonRequest, id=comparison_id)
        comparison.delete()
        messages.success(request, 'Comparison deleted successfully.')
    
    return redirect('admins:comparisons')
