from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
	last_password_set = forms.DateTimeField(label="", required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Password Set'}))
	class Meta:
		model = Employee
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff','last_password_set')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
		# self.fields['is_staff'].widget.attrs['class'] = 'form-control'
		self.fields['is_staff'].widget.attrs['placeholder'] = 'Staff'
		self.fields['is_staff'].label = ''
		self.fields['is_staff'].help_text = '<span class="form-text text-muted"><small>Is this user a member of staff.</small></span>'


class EditForm(UserChangeForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    remove_groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    last_password_set = forms.DateTimeField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Password Set'}), required=False)

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['groups'].widget.attrs['class'] = 'form-control'
        self.fields['remove_groups'].widget.attrs['class'] = 'form-control'