from django import forms
from .models import Comments, Rating

class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'row': 5})
        }

class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'row': 5})
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.HiddenInput(),
        }
