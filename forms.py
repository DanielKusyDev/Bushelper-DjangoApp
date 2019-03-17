from django import forms
DIRECTIONS = (
        ('lbn', 'Lublin'),
        ('lsw', 'Świdnik'),
    )


class SearchForm(forms.Form):
    origin = forms.CharField()
    destination = forms.CharField()
    coordinates = forms.CharField(widget=forms.HiddenInput, required=False)
    direction = forms.ChoiceField(choices=DIRECTIONS, initial='lbn')

    class Meta:
        fields = (
            'origin', 'destination', 'coordinates', 'direction'
        )
