from django.forms import ModelForm, Textarea, TextInput
from .models import Thread


class ThreadForm(ModelForm):

    class Meta:
        model = Thread
        fields = ('title', )
        widgets = {
            # 'title': Textarea(attrs={'cols': 100, 'rows': 20}),
            'title': TextInput(attrs={'size': 200, 'title': 'Your name'}),
        }
