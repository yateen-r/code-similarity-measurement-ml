from django import forms
from .models import CodeSubmission, ComparisonRequest

class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ['title', 'description', 'language', 'code_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter code title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description (optional)'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'code_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TextSubmissionForm(forms.ModelForm):
    code_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control code-editor',
            'rows': 20,
            'placeholder': 'Paste your code here...'
        })
    )
    
    class Meta:
        model = CodeSubmission
        fields = ['title', 'description', 'language', 'code_text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter code title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description (optional)'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }


class ComparisonRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['source_submission'].queryset = CodeSubmission.objects.filter(user=user)
            self.fields['target_submission'].queryset = CodeSubmission.objects.filter(user=user)
    
    class Meta:
        model = ComparisonRequest
        fields = ['comparison_type', 'source_submission', 'target_submission', 
                  'similarity_threshold', 'use_ml_analysis']
        widgets = {
            'comparison_type': forms.Select(attrs={'class': 'form-control'}),
            'source_submission': forms.Select(attrs={'class': 'form-control'}),
            'target_submission': forms.Select(attrs={'class': 'form-control'}),
            'similarity_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1',
                'step': '0.01',
                'value': '0.75'
            }),
            'use_ml_analysis': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
