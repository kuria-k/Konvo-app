from django.shortcuts import render, redirect, get_object_or_404
from .models import MyUser, Post, Comment, Like
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# SIGNUP VIEW
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not username or not email or not password1 or not password2:
            return render(request, 'signup.html', {'error': 'All fields are required'})

        if MyUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        if MyUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        # Save user
        hashed_password = make_password(password1)
        MyUser.objects.create(username=username, email=email, password=hashed_password)

        # Store success message in session
        request.session['success'] = 'Account created successfully'
        return redirect('login')

    return render(request, 'signup.html')


# LOGIN VIEW
def login_view(request):
    success = request.session.pop('success', None) 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {'error': 'Please enter both username and password'})

        try:
            user = MyUser.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})
        except MyUser.DoesNotExist:
            return render(request, 'login.html', {'error': 'User does not exist'})

    return render(request, 'login.html', {'success': success})


# HOME VIEW
def home_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = MyUser.objects.get(id=user_id)
    except MyUser.DoesNotExist:
        return redirect('login')

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'user': user, 'posts': posts})

def logout_view(request):
    request.session.flush()  
    return redirect('login')  


def upload_post(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        user_id = request.session.get('user_id')

        if image and user_id:
            Post.objects.create(user_id=user_id, image=image, caption=caption)
            return redirect('home')
    return redirect('home')



def like_post(request, post_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user_id=user_id)

    if not created:
        like.delete()  

    return redirect('home')



def add_comment(request, post_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text')

    if text:
        Comment.objects.create(post=post, user_id=user_id, text=text)

    return redirect('home')

@csrf_exempt
def toggle_like(request, post_id):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        post = get_object_or_404(Post, id=post_id)

        existing_like = Like.objects.filter(user_id=user_id, post=post).first()

        if existing_like:
            existing_like.delete()
            liked = False
        else:
            Like.objects.create(user_id=user_id, post=post)
            liked = True

        like_count = Like.objects.filter(post=post).count()
        return JsonResponse({"liked": liked, "like_count": like_count})






