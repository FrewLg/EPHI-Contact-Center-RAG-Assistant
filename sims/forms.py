from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'description', 'attachment']
        
class ChatForm(forms.Form):
    message = forms.CharField(max_length=2000)