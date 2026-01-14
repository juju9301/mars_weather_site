from django import forms

class PlotForm(forms.Form):
    sol_from_choices = [(200, 200), (201, 201)]
    sol_to_choices = [(4023, 4023), (4265, 4265)]
    param_choices = [('min_temp', 'min_temp'), ('max_temp', 'max_temp')]
    sol_from = forms.ChoiceField(choices=sol_from_choices)
    sol_to = forms.ChoiceField(choices=sol_to_choices)
    param = forms.ChoiceField(choices=param_choices)