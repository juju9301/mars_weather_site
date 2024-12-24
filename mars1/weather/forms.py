from django import forms
from .models import Weather, Post


class PlotForm(forms.Form):
    # sol_from_choices = [(str(w), str(w)) for w in Weather.objects.values_list('sol').order_by('sol')]
    sol_from_choices = [(200, 200), (201, 201)]
    # sol_to_choices = [(str(w), str(w)) for w in Weather.objects.values_list('sol').order_by('-sol')]
    sol_to_choices = [(4023, 4023), (4265, 4265)]
    param_choices = [('min_temp', 'min_temp'), ('max_temp', 'max_temp')]
    sol_from = forms.ChoiceField(choices=sol_from_choices)
    sol_to = forms.ChoiceField(choices=sol_to_choices)
    param = forms.ChoiceField(choices=param_choices)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        content = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'required': False}))
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')

        if not content and not image:
            raise forms.ValidationError('You must provide either content or an image.')

        return cleaned_data