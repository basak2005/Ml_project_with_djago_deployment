from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import User

# ----------------------------
# LANDING PAGE VIEW
# ----------------------------
def landing_page(request):
    """Landing page for the house brokerage firm - always accessible"""
    return render(request, 'landing.html')

# ----------------------------
# LOGIN VIEW
# ----------------------------
def login_view(request):
    if request.session.get('is_authenticated'):
        return redirect('ml_predictor:home')  # Redirect to ml_predictor home

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username, password=password)

                # Store session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['user_name'] = user.name
                request.session['is_authenticated'] = True
                request.session.set_expiry(1800)  # 30 min

                messages.success(request, f'Welcome back, {user.name}!')
                return redirect('ml_predictor:home')  # Redirect to ml_predictor on success
                    
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password. Please register if you don\'t have an account.')
                return render(request, 'login.html')  # Stay on login page with error
        else:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'login.html')  # Stay on login page with error

    return render(request, 'login.html')

# ----------------------------
# REGISTER VIEW
# ----------------------------
def register_view(request):
    if request.session.get('is_authenticated'):
        return redirect('ml_predictor:home')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validation
        if not all([name, email, username, password]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'register.html')
            
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'register.html')
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
            return render(request, 'register.html')
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return render(request, 'register.html')
        
        try:
            # Create new user and automatically log them in
            user = User.objects.create(
                name=name,
                email=email,
                address=address,
                mobile=phone,
                username=username,
                password=password  # In production, you should hash this password
            )
            
            # Auto-login after registration
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['user_name'] = user.name
            request.session['is_authenticated'] = True
            request.session.set_expiry(1800)  # 30 min
            
            messages.success(request, f'Registration successful! Welcome, {user.name}!')
            return redirect('ml_predictor:home')  # Go directly to ML Predictor
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
    
    return render(request, 'register.html')

# ----------------------------
# LOGOUT VIEW
# ----------------------------
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('landing')  # Redirect to landing page
# ----------------------------
# DECORATOR TO PROTECT VIEWS
# ----------------------------
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            messages.error(request, 'Login required to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Helper function to check if user is authenticated (deprecated - use decorator instead)
def is_user_authenticated(request):
    return request.session.get('is_authenticated', False)
