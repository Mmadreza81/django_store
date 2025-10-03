from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'class': 'form-control me-2',
                                                                                     'type': 'search',
                                                                                     'placeholder': 'Search',
                                                                                     'name': 'search'}))
