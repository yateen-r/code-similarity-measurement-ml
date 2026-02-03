from django.db import models
from django.contrib.auth.models import User


class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('javascript', 'JavaScript'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    code_text = models.TextField()
    code_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']


class Comparison(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_submission = models.ForeignKey(
        CodeSubmission, 
        on_delete=models.CASCADE, 
        related_name='source_comparisons'
    )
    target_submission = models.ForeignKey(
        CodeSubmission, 
        on_delete=models.CASCADE, 
        related_name='target_comparisons',
        null=True,
        blank=True
    )
    target_code_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    similarity_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comparison {self.id} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']


class SimilarityResult(models.Model):
    comparison = models.OneToOneField(
        Comparison, 
        on_delete=models.CASCADE, 
        related_name='result'
    )
    overall_similarity_score = models.FloatField()
    token_similarity = models.FloatField(null=True, blank=True)
    structural_similarity = models.FloatField(null=True, blank=True)
    ast_similarity = models.FloatField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result for Comparison {self.comparison.id}"
