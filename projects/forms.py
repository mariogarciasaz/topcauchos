from django import forms
from .models import *
from clientdata.models import Car


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']

        labels = {
            'title': 'Título',
            'client': 'Cliente',
            'employee': 'Empleado',
            'status': 'Estado',
            'start_date': 'Fecha de inicio',
            'end_date': 'Fecha de finalización',
            'description': 'Descripción',
            'car': 'Vehículo',
            'car_kms': 'Kilometraje del vehículo',
        }

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título', 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'car': forms.Select(attrs={'class': 'form-control'}),
            'car_kms': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, client=None, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Si hay cliente, filtra los autos de ese cliente
        if client:
            self.fields['car'].queryset = Car.objects.filter(client=client)
            self.fields['client'].queryset = Client.objects.filter(id=client.id)
            self.fields['client'].initial = client.id
        else:
            self.fields['car'].queryset = Car.objects.none()  # 🔹 Evita errores si no hay cliente

        



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