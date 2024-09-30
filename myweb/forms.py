from django import forms
from .models import Student, Candidate, Vote


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'reg_no', 'phone_number', 'graduation_year']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['reg_no'].widget.attrs['placeholder'] = 'Enter your registration number'
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['graduation_year'].widget.attrs['placeholder'] = 'Enter your graduation year'

        # Remove labels by setting them to an empty string
        for field in self.fields.values():
            field.label = ""





class LoginForm(forms.Form):
    reg_no = forms.CharField(label='Registration Number')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['reg_no'].widget.attrs['placeholder'] = 'Enter your registration number'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'

        # Remove labels by setting them to an empty string
        for field in self.fields.values():
            field.label = ""



class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['candidate']
