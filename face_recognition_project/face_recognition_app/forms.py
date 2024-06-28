from django import forms
from .models import Student

class StudentForm(forms.Form):
    name = forms.CharField(max_length=255)
    mobile = forms.CharField(max_length=255)
    rno = forms.CharField(max_length=20)
    stream = forms.CharField(max_length=255)
    std = forms.CharField(max_length=10)

class ExcelGenerationForm(forms.Form):
    stream = forms.ChoiceField(choices=[])
    std = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(ExcelGenerationForm, self).__init__(*args, **kwargs)

        # Dynamically populate stream choices from the database
        streams = Student.objects.values_list('stream', flat=True).distinct()
        self.fields['stream'].choices = [(stream, stream) for stream in streams]

        # Dynamically populate std choices from the database
        stds = Student.objects.values_list('std', flat=True).distinct()
        self.fields['std'].choices = [(std, std) for std in stds]
