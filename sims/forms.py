from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'description', 'attachment']

# class ChatForm(forms.Form):
#     message = forms.CharField(max_length=2000)
    
class ChatForm(forms.Form):
    user_input = forms.CharField(
        label="Your Message",
        max_length=500,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Ask me anything...",
        })
    )