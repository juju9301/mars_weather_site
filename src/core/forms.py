from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Post, Comment


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})   
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password confirmation'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})   
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class PostForm(forms.ModelForm):
    random_mars_image_url = forms.URLField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Post
        fields = ['content', 'image', 'font_color', 'background_color']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'required': False}),
            'font_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'})
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
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40, 'data-testid': 'comment-form-content'}),
        }