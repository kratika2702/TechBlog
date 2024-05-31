from django.shortcuts import render,HttpResponseRedirect, redirect, HttpResponse
from .forms import SignUpForm, LoginForm, BlogForm, ContactForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Blog, Author
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError

# Create your views here.
def home(request):
    blogs = Blog.objects.all()
    return render(request,'blog/home.html',{'blogs':blogs})

def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                author = Author.objects.create(user=user, name=user.username, email=user.email)
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                return render(request, 'blog/signup.html', {'form': form, 'error': 'This email is already registered.'})
    else:
        form = SignUpForm()
    return render(request, 'blog/signup.html', {'form': form})

def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request = request, data = request.POST)
            if form.is_valid():
                uname = form.cleaned_data['username']
                pwd = form.cleaned_data['password']
                user = authenticate(username=uname, password=pwd)
                if user is not None:
                    login(request, user)
                    if not hasattr(user, 'author'):
                        # Create an associated Author instance if not already created
                        author = Author.objects.create(user=user)
                    return HttpResponseRedirect('/dashboard/')
        else:
            form = LoginForm()
        return render(request, 'blog/login.html', {'form':form})
    else:
        return HttpResponseRedirect('/dashboard/')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        full_name = user.get_full_name()
        gps = user.groups.all()

        # Fetch blogs created by the currently logged-in user
        blogs = Blog.objects.filter(author__user=user)

        return render(request, 'blog/dashboard.html', {'blogs': blogs, 'full_name': full_name, 'groups': gps})
    else:
        return HttpResponseRedirect('/login/')

def add_blog(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = BlogForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                cont = form.cleaned_data['cont']
                # Get the currently logged-in user
                user = request.user
                # Check if the user is an instance of Author
                if hasattr(user, 'author'):
                    author = user.author
                    # Create a new Blog instance associated with the Author
                    blg = Blog(title=title, cont=cont, author=author)
                    blg.save()
                    form = BlogForm()
                else:
                    # Handle the case where the user is not an Author instance
                    # (This should not happen if your authentication system is set up correctly)
                    return HttpResponse("Error: User is not an author")
        else:
            form = BlogForm()
        return render(request, 'blog/addblog.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')

def update_blog(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Blog.objects.get(pk=id)
            form = BlogForm(request.POST,instance = pi)
            if form.is_valid():
                form.save()
        else:
            pi = Blog.objects.get(pk=id)
            form = BlogForm(instance=pi)
        return render(request, 'blog/updateblog.html',{'form':form})
    else:
        return HttpResponseRedirect('/login/')

def delete_blog(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pi = Blog.objects.get(pk=id)
            pi.delete()
            return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/login/')

def about(request):
    return render(request, 'blog/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Check if all required fields are filled in
            if all(form.cleaned_data.values()):
                # Render the template with the "thank you" message
                return render(request, 'blog/thank_you.html')
            else:
                # Some required fields are missing
                # Re-render the contact form with an error message
                error_message = "Please fill in all required fields."
                return render(request, 'blog/contact.html', {'form': form, 'error_message': error_message})
    else:
        form = ContactForm()
    return render(request, 'blog/contact.html', {'form': form})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/single_blog.html', {'blog': blog})


def author_blogs(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    blogs = author.blogs.all()
    return render(request, 'blog/author_blogs.html', {'author': author, 'blogs': blogs})
