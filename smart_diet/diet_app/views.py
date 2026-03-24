from .forms import DietForm, CalorieForm
from .utils import get_diet_recommendation, get_calorie_prediction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'diet_app/home.html')

def recommend_diet(request):
    result = None
    if request.method == 'POST':
        form = DietForm(request.POST)
        if form.is_valid():
            result = get_diet_recommendation(form.cleaned_data)
    else:
        form = DietForm()
    
    return render(request, 'diet_app/recommend_diet.html', {'form': form, 'result': result})

def calorie_finder(request):
    result = None
    error = None
    
    suggestions = None

    if request.method == 'POST':
        form = CalorieForm(request.POST)
        if form.is_valid():
            food = form.cleaned_data['food_item']
            weight = form.cleaned_data['weight']
            # Only 3 return values now: calories, error, suggestions
            calories, err, suggestions = get_calorie_prediction(food, weight)
            
            if calories is not None:
                result = {
                    'food': food,
                    'weight': weight,
                    'calories': round(calories, 2)
                }
            elif suggestions:
                pass
            else:
                error = err
    else:
        form = CalorieForm()

    return render(request, 'diet_app/calorie_finder.html', {
        'form': form, 
        'result': result, 
        'error': error,
        'suggestions': suggestions
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'diet_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'diet_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
