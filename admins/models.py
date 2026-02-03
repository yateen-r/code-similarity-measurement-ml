from django.db import models
from django.conf import settings
import uuid

class CodeDataset(models.Model):
    DATASET_TYPES = (
        ('training', 'Training Dataset'),
        ('validation', 'Validation Dataset'),
        ('reference', 'Reference Repository'),
        ('benchmark', 'Benchmark Dataset'),
    )
    
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('multi', 'Multi-Language'),
    )
    
    dataset_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    dataset_type = models.CharField(max_length=20, choices=DATASET_TYPES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    file_path = models.FileField(upload_to='datasets/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    file_count = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_processed = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_datasets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_dataset_type_display()})"


class MLModel(models.Model):
    MODEL_TYPES = (
        ('random_forest', 'Random Forest'),
        ('neural_network', 'Neural Network'),
        ('svm', 'Support Vector Machine'),
        ('gradient_boosting', 'Gradient Boosting'),
        ('ensemble', 'Ensemble Model'),
    )
    
    STATUS_CHOICES = (
        ('training', 'Training'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    )
    
    model_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=50)
    description = models.TextField()
    model_file = models.FileField(upload_to='ml_models/')
    training_dataset = models.ForeignKey(CodeDataset, on_delete=models.SET_NULL, null=True, related_name='trained_models')
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    training_params = models.JSONField(default=dict)
    feature_importance = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    is_default = models.BooleanField(default=False)
    trained_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    trained_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'ml_models'
        ordering = ['-trained_at']
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.status})"


class SystemConfiguration(models.Model):
    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.TextField()
    value_type = models.CharField(
        max_length=20,
        choices=[('string', 'String'), ('integer', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('json', 'JSON')],
        default='string'
    )
    is_editable = models.BooleanField(default=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"


class AdminActivity(models.Model):
    ACTIVITY_TYPES = (
        ('user_management', 'User Management'),
        ('dataset_management', 'Dataset Management'),
        ('model_management', 'Model Management'),
        ('system_config', 'System Configuration'),
        ('report_generation', 'Report Generation'),
    )
    
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    action = models.CharField(max_length=100)
    description = models.TextField()
    affected_object = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_activities'
        ordering = ['-timestamp']
        verbose_name_plural = 'Admin Activities'
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} at {self.timestamp}"


class SystemAlert(models.Model):
    ALERT_TYPES = (
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Information'),
        ('success', 'Success'),
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'system_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"
