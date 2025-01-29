from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.conf import settings
import requests
from .models import Post, Comment
from weather.models import Weather
from .forms import RegisterForm, LoginForm, PostForm, CommentForm
from django.contrib.auth.models import User

from .serializers import PostSerializer, CommentSerializer, UserSerializer
from rest_framework import generics, status
from rest_framework.response import Response


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:index')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:index')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('core:index')

def index(request):
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 3)  # Show 10 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    recent_sol = Weather.objects.latest('sol') if Weather.objects.exists() else None
    return render(request, 'index.html', {'posts': posts, 'recent_sol': recent_sol, 'nasa_api_key': settings.NASA_API_KEY})

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            random_mars_image_url = form.cleaned_data.get('random_mars_image_url')
            if random_mars_image_url:
                response = requests.get(random_mars_image_url)
                if response.status_code == 200:
                    post.image.save(f"random_mars_image_{post.id}.jpg", ContentFile(response.content), save=False)
            post.save()
            return redirect('core:index')
    else:
        form = PostForm()
    return render(request, 'core/add_post.html', {'form': form, 'nasa_api_key': settings.NASA_API_KEY})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('core:index')
    else:
        form = CommentForm()
    return render(request, 'core/add_comment.html', {'form': form, 'post': post, 'comments': post.comments.all()})

# test endpoint views

class PostListCreateApiView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers =  self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PostDeleteApiView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        if ids:
            posts = Post.objects.filter(id__in=ids)
        else:
            posts = Post.objects.all()
        count = posts.count()
        posts.delete()
        return Response({'deleted': count}, status=status.HTTP_204_NO_CONTENT)

class CommentListCreateApiView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.request.query_params.get(post_id)
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers =  self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
class CommentDeleteApiView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        comments = Comment.objects.filter(id__in=ids)
        count = comments.count()
        comments.delete()
        return Response({'deleted': count}, status=status.HTTP_204_NO_CONTENT)
    
class UserDeleteApiView(generics.DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        if ids:
            users = User.objects.filter(id__in=ids)
        else:
            users = User.objects.all()
        ids = list(users.values_list('id', flat=True))
        users.delete()
        return Response({'deleted': ids}, status=status.HTTP_204_NO_CONTENT)

