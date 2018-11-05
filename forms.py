from django import forms


class SearchForm(forms.Form):
    origin = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control col-md-11',
            'placeholder': "Odjazd z...",
        }), label='')
    destination = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control fluid',
                'placeholder': "Przyjazd do..."}),
        label='',
        required=False
    )
    coordinates = forms.CharField(widget=forms.HiddenInput)
    directions = (
        ('lsw', 'Świdnik'),
        ('lbn', 'Lublin')
    )

    direction = forms.ChoiceField(
        choices=directions,
        initial='lbn',
        widget=forms.Select(
            attrs={
                'class': 'btn btn-default dropdown-toggle',
            }
        )
    )
