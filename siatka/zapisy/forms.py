from django import forms
from .models import Entry, Player


class EntryForm(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=Player.objects.order_by('name'))

    class Meta:
        model = Entry
        fields = ('player', 'multisport')


class EventManagerForm(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=Player.objects.order_by('name'))

    class Meta:
        model = Entry
        exclude = ('event',)

    def __init__(self, *args, **kwargs):
        super(EventManagerForm, self).__init__(*args, **kwargs)
        self.fields['player'].required = False
