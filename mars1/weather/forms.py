from django import forms
from .models import Weather, Post, Comment

class PlotForm(forms.Form):
    sol_from_choices = [(200, 200), (201, 201)]
    sol_to_choices = [(4023, 4023), (4265, 4265)]
    param_choices = [('min_temp', 'min_temp'), ('max_temp', 'max_temp')]
    sol_from = forms.ChoiceField(choices=sol_from_choices)
    sol_to = forms.ChoiceField(choices=sol_to_choices)
    param = forms.ChoiceField(choices=param_choices)

class PostForm(forms.ModelForm):
    random_mars_image_url = forms.URLField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'required': False}),
        }

    content = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'required': False}))

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        random_mars_image_url = cleaned_data.get('random_mars_image_url')

        if not content and not image and not random_mars_image_url:
            raise forms.ValidationError('You must provide either content or an image.')

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }