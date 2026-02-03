from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import uuid

class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('cpp', 'C++'),
        ('c', 'C'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    code_file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['py', 'java', 'js', 'cpp', 'c', 'txt'])]
    )
    code_text = models.TextField(blank=True, null=True)
    file_size = models.IntegerField(default=0)
    line_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_temporary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_submissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.language})"
    
    def save(self, *args, **kwargs):
        if self.code_file and not self.code_text:
            try:
                # Ensure file pointer at start
                try:
                    self.code_file.seek(0)
                except Exception:
                    pass

                content = self.code_file.read()

                # UploadedFile.read() may return bytes or str
                if isinstance(content, bytes):
                    try:
                        content_text = content.decode('utf-8')
                    except Exception:
                        content_text = content.decode('latin-1', errors='ignore')
                else:
                    content_text = str(content)

                self.code_text = content_text

                # Reset pointer so storage can read it again when saving
                try:
                    self.code_file.seek(0)
                except Exception:
                    pass

                # Try to get file size
                try:
                    self.file_size = self.code_file.size
                except Exception:
                    try:
                        self.file_size = self.code_file.file.size
                    except Exception:
                        self.file_size = len(content) if content is not None else 0

                self.line_count = len(self.code_text.splitlines())
            except Exception:
                # If anything goes wrong reading the uploaded file, skip enriching fields
                pass
        super().save(*args, **kwargs)


class ComparisonRequest(models.Model):
    COMPARISON_TYPES = (
        ('single_vs_repo', 'Single File vs Repository'),
        ('file_vs_file', 'File vs File'),
        ('multiple_vs_multiple', 'Multiple Files vs Multiple Files'),
        ('text_vs_text', 'Text vs Text'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comparisons')
    comparison_type = models.CharField(max_length=30, choices=COMPARISON_TYPES)
    source_submission = models.ForeignKey(
        CodeSubmission, 
        on_delete=models.CASCADE, 
        related_name='source_comparisons'
    )
    target_submission = models.ForeignKey(
        CodeSubmission, 
        on_delete=models.CASCADE, 
        related_name='target_comparisons',
        blank=True,
        null=True
    )
    similarity_threshold = models.FloatField(default=0.75)
    use_ml_analysis = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'comparison_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comparison {self.request_id} by {self.user.username}"


class SimilarityResult(models.Model):
    result_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    comparison = models.OneToOneField(ComparisonRequest, on_delete=models.CASCADE, related_name='result')
    overall_similarity_score = models.FloatField()
    structural_similarity = models.FloatField(default=0.0)
    token_similarity = models.FloatField(default=0.0)
    ast_similarity = models.FloatField(default=0.0)
    ml_similarity = models.FloatField(default=0.0, blank=True, null=True)
    identical_segments = models.JSONField(default=list)
    near_identical_segments = models.JSONField(default=list)
    code_metrics = models.JSONField(default=dict)
    visualization_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'similarity_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Result {self.result_id} - {self.overall_similarity_score:.2%}"


class SavedComparison(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_comparisons')
    comparison = models.ForeignKey(ComparisonRequest, on_delete=models.CASCADE)
    result = models.ForeignKey(SimilarityResult, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_comparisons'
        ordering = ['-saved_at']
        unique_together = ['user', 'comparison']
    
    def __str__(self):
        return f"Saved by {self.user.username} - {self.comparison.request_id}"
