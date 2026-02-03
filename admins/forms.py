from django import forms
from .models import CodeDataset, MLModel, SystemConfiguration
from accounts.models import CustomUser

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = CodeDataset
        fields = ['name', 'description', 'dataset_type', 'language', 'file_path', 'external_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'dataset_type': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class MLModelUploadForm(forms.ModelForm):
    class Meta:
        model = MLModel
        fields = ['name', 'model_type', 'version', 'description', 'model_file', 
                  'training_dataset', 'accuracy', 'precision', 'recall', 'f1_score']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model_type': forms.Select(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'model_file': forms.FileInput(attrs={'class': 'form-control'}),
            'training_dataset': forms.Select(attrs={'class': 'form-control'}),
            'accuracy': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precision': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'recall': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'f1_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfiguration
        fields = ['config_key', 'config_value', 'description', 'value_type']
        widgets = {
            'config_key': forms.TextInput(attrs={'class': 'form-control'}),
            'config_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'value_type': forms.Select(attrs={'class': 'form-control'}),
        }


class UserManagementForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_blocked', 'is_verified']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_blocked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
