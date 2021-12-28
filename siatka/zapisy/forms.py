from django import forms
from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ('player', 'multisport')


class EventManagerForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ('event',)

    def __init__(self, *args, **kwargs):
        super(EventManagerForm, self).__init__(*args, **kwargs)
        self.fields['player'].required = False
