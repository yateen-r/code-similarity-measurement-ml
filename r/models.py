from django.db import models
from django.conf import settings
from users.models import ComparisonRequest, SimilarityResult
import uuid

class SimilarityReport(models.Model):
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    )
    
    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    comparison = models.ForeignKey(ComparisonRequest, on_delete=models.CASCADE)
    result = models.ForeignKey(SimilarityResult, on_delete=models.CASCADE)
    report_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_path = models.FileField(upload_to='reports/%Y/%m/%d/')
    file_size = models.IntegerField(default=0)
    include_visualizations = models.BooleanField(default=True)
    include_code_segments = models.BooleanField(default=True)
    include_metrics = models.BooleanField(default=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)
    last_downloaded = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'similarity_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Report {self.report_id} - {self.report_format.upper()}"


class AggregateReport(models.Model):
    REPORT_TYPES = (
        ('user_activity', 'User Activity Report'),
        ('similarity_trends', 'Similarity Trends'),
        ('plagiarism_incidents', 'Plagiarism Incidents'),
        ('system_usage', 'System Usage Statistics'),
        ('model_performance', 'Model Performance'),
    )
    
    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_from = models.DateField()
    date_to = models.DateField()
    file_path = models.FileField(upload_to='aggregate_reports/%Y/%m/')
    data_summary = models.JSONField(default=dict)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'aggregate_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.date_from} to {self.date_to}"
