from django import forms

class WAVForm(forms.Form):
    WAV=forms.FileField()
    dict=forms.FileField(required=False)
