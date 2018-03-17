from django import forms
from .models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'description', )
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Image title',
                    'class': 'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Description...',
                    'class': 'form-control',
                    'rows': 3
                }
            ),
        }