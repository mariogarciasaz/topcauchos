from django import forms
from .models import *


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title', 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'created_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'created_by': forms.TextInput(attrs={'class': 'form-control',}),
            'updated_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'updated_by': forms.TextInput(attrs={'class': 'form-control',}),
            'car': forms.Select(attrs={'class': 'form-control'}),
            'car_kms': forms.NumberInput(attrs={'class': 'form-control'}),
        }




class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['project'].initial = project

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment'}),
        }