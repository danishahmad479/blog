from django.shortcuts import render , HttpResponse , redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from .models import *
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
# Create your views here.



def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')


        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'message': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'message': 'Email already exists'})
        
        user = User.objects.create(username=username,email=email)
        user.set_password(password)
        user.save()
        return redirect("user_login")

    return render(request,"register.html")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("blog_list")
        else:
            return render(request, 'login.html', {'message': 'Invalid credentials'})

    return render(request, 'login.html')



# def blog_list(request):
#     if not request.user.is_authenticated:
#         return redirect('user_login')

#     posts_list = Blog.objects.all().order_by('-published_date')
#     paginator = Paginator(posts_list, 5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'blog_list.html', {'page_obj': page_obj})


def blog_list(request):
    if not request.user.is_authenticated:
        return redirect('user_login')


    search_query = request.GET.get('search', '')
    blogs = Blog.objects.filter(title__icontains=search_query) | Blog.objects.filter(description__icontains=search_query)
    
    paginator = Paginator(blogs, 5)  # Show 10 blogs per page.
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'blogs': list(page_obj.object_list.values('id', 'title', 'description', 'published_date')),
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_number,
            'total_pages': paginator.num_pages,
        }
        return JsonResponse(data)
    
    return render(request, 'blog_list.html', {'page_obj': page_obj})


def blog_detail(request, pk):
    if request.user.is_authenticated:
        post = Blog.objects.filter(pk=pk).first()
        return render(request, 'blog_detail.html', {'post': post})
    return redirect("user_login")





def send_blog_email(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        post_id = request.POST.get('post_id')
        post = Blog.objects.filter(pk=post_id).first()
        
        if not email:
            return HttpResponseBadRequest("Email is required")
        
        if not settings.EMAIL_HOST_USER:
            return HttpResponseBadRequest("Email configuration is missing")

        subject = f"Check out this blog post: {post.title}"
        message = f"Here is the blog post you wanted to share:\n\n{post.title}\n\n{post.description}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return redirect('blog_list') 

    return HttpResponseBadRequest("Invalid request")


def add_comment(request, pk):
    if not request.user.is_authenticated:
        return redirect('user_login')
    blog = Blog.objects.filter(id=pk).first()
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return HttpResponseBadRequest("Content is required")
        comment = Comment(blog=blog, user=request.user, content=content)
        comment.save()
        return redirect('blog_detail', pk=pk)
    return HttpResponseBadRequest("Invalid request")


def like_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('user_login')
    comment = Comment.objects.filter(id=comment_id).first()
    user = request.user
    if not Like.objects.filter(comment=comment, user=user).exists():
        Like.objects.create(comment=comment, user=user)
        return redirect('blog_detail', pk=comment.blog.pk)
    return HttpResponseBadRequest("You have already liked this comment")
