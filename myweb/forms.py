from django import forms
from .models import Student, ResearchTopic, ResearchFile
from django.forms import modelformset_factory

class StudentIDForm(forms.Form):
    student_id = forms.CharField(label='Student ID', max_length=100)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['profile_image','name', 'reg_no', 'email', 'faculty', 'course']

ResearchTopicFormSet = modelformset_factory(ResearchTopic, fields=('topic', 'district_of_study', 'case_study_area'), extra=3)

class RegistrationNumberForm(forms.Form):
    reg_no = forms.CharField(max_length=50, label="Registration Number")

class ResearchFileForm(forms.ModelForm):
    class Meta:
        model = ResearchFile
        fields = ['file', 'description']