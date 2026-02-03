from django.db import models

class CodeMetric(models.Model):
    submission = models.OneToOneField('users.CodeSubmission', on_delete=models.CASCADE, related_name='metrics')
    cyclomatic_complexity = models.FloatField(default=0.0)
    maintainability_index = models.FloatField(default=0.0)
    lines_of_code = models.IntegerField(default=0)
    logical_lines = models.IntegerField(default=0)
    comment_lines = models.IntegerField(default=0)
    blank_lines = models.IntegerField(default=0)
    halstead_volume = models.FloatField(default=0.0)
    halstead_difficulty = models.FloatField(default=0.0)
    unique_operators = models.IntegerField(default=0)
    unique_operands = models.IntegerField(default=0)
    function_count = models.IntegerField(default=0)
    class_count = models.IntegerField(default=0)
    ast_node_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'code_metrics'
    
    def __str__(self):
        return f"Metrics for {self.submission.title}"
