from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from accounts.forms import UserRegistrationForm
from django.contrib.auth import update_session_auth_hash
from .models import CodeSubmission, ComparisonRequest, SimilarityResult, SavedComparison
from .forms import CodeSubmissionForm
import difflib
import re
import ast as _ast
from django.utils import timezone


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        # Redirect superusers to admin dashboard
        if request.user.is_superuser:
            return redirect('admins:dashboard')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user type
                if user.is_superuser:
                    return redirect('admins:dashboard')
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('users:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def dashboard_view(request):
    """User dashboard - redirect superusers to admin dashboard"""
    
    # Redirect superusers to admin dashboard
    if request.user.is_superuser:
        return redirect('admins:dashboard')
    
    # Get user's recent submissions
    recent_submissions = CodeSubmission.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Get user's recent comparisons
    recent_comparisons = ComparisonRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Statistics
    total_submissions = CodeSubmission.objects.filter(user=request.user).count()
    total_comparisons = ComparisonRequest.objects.filter(user=request.user).count()
    completed_comparisons = ComparisonRequest.objects.filter(
        user=request.user, 
        status='completed'
    ).count()

    # High similarity results for user's dashboard (show top recent)
    try:
        high_similarity = SimilarityResult.objects.filter(
            comparison__user=request.user,
            overall_similarity_score__gte=75
        ).order_by('-created_at')[:5]
    except Exception:
        high_similarity = []
    
    context = {
        'recent_submissions': recent_submissions,
        'recent_comparisons': recent_comparisons,
        'total_submissions': total_submissions,
        'total_comparisons': total_comparisons,
        'completed_comparisons': completed_comparisons,
        'high_similarity': high_similarity,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile_view(request):
    """User profile"""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    # Statistics
    stats = {
        'total_submissions': CodeSubmission.objects.filter(user=request.user).count(),
        'total_comparisons': ComparisonRequest.objects.filter(user=request.user).count(),
        'completed_comparisons': ComparisonRequest.objects.filter(
            user=request.user, 
            status='completed'
        ).count(),
    }
    
    return render(request, 'accounts/profile.html', {'stats': stats})


@login_required
def change_password_view(request):
    """Change password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def upload_code_view(request):
    """Upload code submission"""
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            messages.success(request, 'Code uploaded successfully!')
            return redirect('users:submissions')
    else:
        form = CodeSubmissionForm()
    
    return render(request, 'users/upload_code.html', {'form': form})


@login_required
def submissions_view(request):
    """List user's submissions"""
    submissions = CodeSubmission.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'users/submissions.html', {'submissions': submissions})


@login_required
def submission_detail_view(request, submission_id):
    """View submission details"""
    submission = get_object_or_404(CodeSubmission, submission_id=submission_id, user=request.user)
    return render(request, 'users/submission_detail.html', {'submission': submission})


@login_required
def delete_submission_view(request, submission_id):
    """Delete submission"""
    if request.method == 'POST':
        submission = get_object_or_404(CodeSubmission, submission_id=submission_id, user=request.user)
        submission.delete()
        messages.success(request, 'Submission deleted successfully.')
    
    return redirect('users:submissions')


@login_required
def compare_view(request):
    """Compare code"""
    if request.method == 'POST':
        source_id = request.POST.get('source_submission')
        target_id = request.POST.get('target_submission')
        
        if not source_id or not target_id:
            messages.error(request, 'Please select both source and target submissions.')
            return redirect('users:compare_code')
        
        try:
            source = CodeSubmission.objects.get(submission_id=source_id, user=request.user)
            target = CodeSubmission.objects.get(submission_id=target_id, user=request.user)
        except CodeSubmission.DoesNotExist:
            messages.error(request, 'One or both submissions not found.')
            return redirect('users:compare_code')
        
        # Create comparison request (processing)
        comparison = ComparisonRequest.objects.create(
            user=request.user,
            source_submission=source,
            target_submission=target,
            comparison_type='file_vs_file',
            status='processing'
        )

        # Gather texts
        src_text = source.code_text or ''
        tgt_text = target.code_text or ''
        try:
            if not src_text and source.code_file:
                src_text = source.code_file.read().decode('utf-8', errors='ignore')
                try:
                    source.code_file.seek(0)
                except Exception:
                    pass
        except Exception:
            src_text = src_text or ''
        try:
            if not tgt_text and target.code_file:
                tgt_text = target.code_file.read().decode('utf-8', errors='ignore')
                try:
                    target.code_file.seek(0)
                except Exception:
                    pass
        except Exception:
            tgt_text = tgt_text or ''

        # Normalization helpers
        def normalize_whitespace(s):
            return re.sub(r"\s+", ' ', s).strip()

        def token_sequence(s):
            return re.findall(r"\w+", s.lower())

        def seq_ratio(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()

        # Token similarity (sequence matcher on tokens)
        try:
            toks_src = token_sequence(src_text)
            toks_tgt = token_sequence(tgt_text)
            token_sim = seq_ratio(' '.join(toks_src), ' '.join(toks_tgt)) if toks_src or toks_tgt else 0.0
        except Exception:
            token_sim = 0.0

        # Structural similarity (line-based)
        try:
            lines_src = [normalize_whitespace(l) for l in src_text.splitlines() if l.strip()]
            lines_tgt = [normalize_whitespace(l) for l in tgt_text.splitlines() if l.strip()]
            struct_sim = seq_ratio('\n'.join(lines_src), '\n'.join(lines_tgt)) if lines_src or lines_tgt else 0.0
        except Exception:
            struct_sim = 0.0

        # AST similarity for python files
        ast_sim = 0.0
        try:
            if source.language == 'python' and target.language == 'python':
                try:
                    a_src = _ast.parse(src_text)
                    a_tgt = _ast.parse(tgt_text)

                    def flatten_ast(node):
                        nodes = []
                        for n in _ast.walk(node):
                            nodes.append(type(n).__name__)
                        return ' '.join(nodes)

                    ast_seq_src = flatten_ast(a_src)
                    ast_seq_tgt = flatten_ast(a_tgt)
                    ast_sim = seq_ratio(ast_seq_src, ast_seq_tgt)
                except Exception:
                    ast_sim = 0.0
        except Exception:
            ast_sim = 0.0

        # Aggregate overall score (weights) - keep as fraction, then convert to percentage for storage
        overall = (0.5 * token_sim) + (0.3 * struct_sim) + (0.2 * ast_sim)

        # Convert to percentage (0-100) for display consistency
        overall_pct = overall * 100
        token_pct = token_sim * 100
        struct_pct = struct_sim * 100
        ast_pct = ast_sim * 100

        # Persist result (store percentages)
        SimilarityResult.objects.create(
            comparison=comparison,
            overall_similarity_score=overall_pct,
            structural_similarity=struct_pct,
            token_similarity=token_pct,
            ast_similarity=ast_pct,
            identical_segments=[],
            near_identical_segments=[],
            code_metrics={},
            visualization_data={}
        )

        # Mark comparison and related submissions as completed
        comparison.status = 'completed'
        comparison.completed_at = timezone.now()
        comparison.save()

        try:
            source.status = 'completed'
            source.save()
        except Exception:
            pass

        try:
            target.status = 'completed'
            target.save()
        except Exception:
            pass

        messages.success(request, 'Comparison completed!')
        return redirect('users:comparison_detail', comparison_id=comparison.request_id)
    
    # Get user's submissions for dropdown
    submissions = CodeSubmission.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'users/compare_code.html', {'submissions': submissions})


@login_required
def comparisons_view(request):
    """List comparisons"""
    comparisons = ComparisonRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'users/comparisons.html', {'comparisons': comparisons})


@login_required
def comparison_detail_view(request, comparison_id):
    """View comparison details"""
    comparison = get_object_or_404(ComparisonRequest, request_id=comparison_id, user=request.user)
    result = None
    try:
        result = comparison.result
    except SimilarityResult.DoesNotExist:
        pass
    return render(request, 'users/comparison_detail.html', {'comparison': comparison, 'result': result})


@login_required
def save_comparison_view(request, comparison_id):
    """Save comparison for later viewing"""
    comparison = get_object_or_404(ComparisonRequest, request_id=comparison_id, user=request.user)
    
    # Get result if it exists
    result = None
    try:
        result = comparison.result
    except SimilarityResult.DoesNotExist:
        pass
    
    # Check if already saved
    saved, created = SavedComparison.objects.get_or_create(
        user=request.user,
        comparison=comparison,
        defaults={'result': result}
    )
    
    if created:
        messages.success(request, 'Comparison saved successfully.')
    else:
        messages.info(request, 'Comparison already saved.')
    
    return redirect('users:comparison_detail', comparison_id=comparison_id)


@login_required
def delete_comparison_view(request, comparison_id):
    """Delete comparison"""
    if request.method == 'POST':
        comparison = get_object_or_404(ComparisonRequest, request_id=comparison_id, user=request.user)
        comparison.delete()
        messages.success(request, 'Comparison deleted successfully.')
    
    return redirect('users:comparisons')


@login_required
def history_view(request):
    """View history"""
    comparisons = ComparisonRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'users/history.html', {'comparisons': comparisons})
