from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
import requests
from .models import Post, Comment
from weather.models import Weather
from .forms import RegisterForm, LoginForm, PostForm, CommentForm
from .decorators import redirect_authenticated_user
from django.contrib.auth.models import User
from django.db.models import Count, Max, Min

from .serializers import PostSerializer, CommentSerializer, UserSerializer
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response


@redirect_authenticated_user
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

@redirect_authenticated_user
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
    weather_summary = Weather.objects.aggregate(
        sol_count=Count('id'),
        min_sol=Min('sol'),
        max_sol=Max('sol'),
    )
    recent_sol = (
        Weather.objects.filter(sol=weather_summary['max_sol']).first()
        if weather_summary['max_sol'] is not None
        else None
    )

    champions = []
    champion_fields = (
        ('Warmest air', 'max_temp', True, '°C'),
        ('Coldest air', 'min_temp', False, '°C'),
        ('Warmest ground', 'max_gts_temp', True, '°C'),
        ('Coldest ground', 'min_gts_temp', False, '°C'),
        ('Highest pressure', 'pressure', True, 'Pa'),
        ('Lowest pressure', 'pressure', False, 'Pa'),
    )
    for label, field, highest_first, unit in champion_fields:
        ordering = f'-{field}' if highest_first else field
        record = (
            Weather.objects.filter(**{f'{field}__isnull': False})
            .only('sol', 'terrestrial_date', field)
            .order_by(ordering, 'sol')
            .first()
        )
        champions.append({
            'label': label,
            'record': record,
            'value': getattr(record, field) if record is not None else None,
            'unit': unit,
        })

    coverage = None
    if weather_summary['sol_count']:
        sol_span = weather_summary['max_sol'] - weather_summary['min_sol'] + 1
        coverage = {
            'min_sol': weather_summary['min_sol'],
            'max_sol': weather_summary['max_sol'],
            'record_count': weather_summary['sol_count'],
            'sol_span': sol_span,
            'missing_count': sol_span - weather_summary['sol_count'],
            'percentage': round(weather_summary['sol_count'] / sol_span * 100, 1),
        }

    return render(request, 'index.html', {
        'recent_sol': recent_sol,
        'champions': champions,
        'coverage': coverage,
    })

def community_posts(request):
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 5)  # Show 5 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'core/community_posts.html', {'posts': posts})

@login_required
def add_post(request):
    if not request.user.is_staff:
        raise PermissionDenied

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
            return redirect('core:community_posts')
    else:
        form = PostForm()
    return render(request, 'core/add_post.html', {'form': form})

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
            return redirect('core:community_posts')
    else:
        form = CommentForm()
    return render(request, 'core/add_comment.html', {'form': form, 'post': post, 'comments': post.comments.all()})

# test endpoint views

class PostListCreateApiView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers =  self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDeleteApiView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminUser]

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

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id')
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
class CommentDeleteApiView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        comments = Comment.objects.filter(id__in=ids)
        count = comments.count()
        comments.delete()
        return Response({'deleted': count}, status=status.HTTP_204_NO_CONTENT)
    
class UserDeleteApiView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', None)
        if ids:
            users = User.objects.filter(id__in=ids)
        else:
            users = User.objects.all()
        ids = list(users.values_list('id', flat=True))
        users.delete()
        return Response({'deleted': ids}, status=status.HTTP_204_NO_CONTENT)
    
class UserListApiView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

