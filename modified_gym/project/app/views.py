from django.shortcuts import render,HttpResponse, HttpResponseRedirect, redirect,get_object_or_404
from django.db.models import Q
from .models import *
from .forms import DietForm, CalorieForm
from .utils import get_diet_recommendation, get_calorie_prediction
from django.contrib import messages
import re


# Create your views here.
def home(request):
    return render(request,'index.html')

def login(request):
    usertype = ""
    if request.POST:
        email = request.POST.get("log_email")
        password = request.POST.get("log_password")
        print(f"Attempting login for: {email}")
        
        logData = Login.objects.filter(email=email, password=password)
        if logData.exists():
            userdata = logData.first()
            usertype = userdata.usertype
            userstatus = userdata.status
            
            # Strip whitespace to ensure accurate matching
            if usertype: usertype = usertype.strip()
            if userstatus: userstatus = userstatus.strip()
            
            print(f"User found: Type='{usertype}', Status='{userstatus}'")

            if usertype == "User":
                request.session["uid"] = userdata.id
                request.session["usertype"] = "User"
                request.session["user_email"] = userdata.email
                
                try:
                    user_profile = UserRegistration.objects.get(loginid=userdata)
                    if user_profile.name:
                        request.session["user_name"] = user_profile.name
                    else:
                         request.session["user_name"] = userdata.email.split('@')[0].capitalize()
                except UserRegistration.DoesNotExist:
                    request.session["user_name"] = userdata.email.split('@')[0].capitalize()

                messages.success(request, "Login successful. Welcome back!")
                return redirect('/userhome')
            elif usertype == "admin":
                request.session["uid"] = userdata.id
                request.session["usertype"] = "admin"
                request.session["user_email"] = userdata.email
                messages.success(request, "Login successful. Welcome back!")
                return redirect('/homepage')
            elif usertype == "Nutritionist" and userstatus == "Approved":
                request.session["uid"] = userdata.id
                request.session["usertype"] = "Nutritionist"
                request.session["user_email"] = userdata.email
                messages.success(request, "Login successful. Welcome back!")
                return redirect('/nutrihome')
            elif userstatus == "pending":
                messages.warning(request, "Your account is awaiting Admin approval. Please try again later.")
            elif userstatus == "Rejected":
                messages.error(request, "Your account registration has been rejected by Admin.")
            else:
                messages.error(request, f"Account status: {userstatus}. Please contact support.")
        else:
            messages.error(request, "Invalid username or password")
    return render(request,'login.html' , {"usertype": usertype})

def logout(request):
    request.session.flush()
    return redirect('/')

def registration(request):
    if request.POST:
        name=request.POST['user_name']
        email=request.POST['user_email']
        phone=request.POST['user_phone']
        password=request.POST['user_password']
        confirmpassword=request.POST['user_confirm_password']
        
        # New Fields
        age = request.POST.get('user_age')
        gender = request.POST.get('user_gender')
        height = request.POST.get('user_height')
        weight = request.POST.get('user_weight')
        goal = request.POST.get('user_goal')

        # Validations
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, "Invalid Email Format")
            return redirect('/registration/')

        if not re.fullmatch(r"\d{10}", phone):
             messages.error(request, "Phone number must be exactly 10 digits")
             return redirect('/registration/')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return redirect('/registration/')
            
        try:
            if float(age) <= 0 or float(height) <= 0 or float(weight) <= 0:
                messages.error(request, "Age, Height and Weight must be positive values")
                return redirect('/registration/')
        except ValueError:
             messages.error(request, "Invalid numeric input")
             return redirect('/registration/')


        if password==confirmpassword:
            if(Login.objects.filter(email=email).exists()):
                messages.error(request, "Email already exists! Please use a different one.")
                return redirect('/registration/')
            else:
                userLogin = Login.objects.create(
                email=email, password=password, status="Approved", usertype="User")
                
                UserRegistration.objects.create(
                    name=name, email=email, phone=phone, password=password, 
                    loginid=userLogin,
                    age=age, gender=gender, height=height, weight=weight, health_goal=goal
                )
                messages.success(request, "Registration successful! You can login now.")
                return redirect('/login/')
        else:
            messages.error(request, "Password mismatch! Please type carefully.")
            return redirect('/registration/')
    return render(request,'registration.html')

def about(request):
    return render(request,'about.html')

def homepage(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    # Fetch data for admin overview
    diet_plans = Dietplan.objects.filter(is_custom=False).order_by('-id')[:6]
    diet_requests = DietRequest.objects.all().order_by('-request_date')[:10]
    
    context = {
        'diet_plans': diet_plans,
        'diet_requests': diet_requests
    }
    return render(request, 'admin/homepage.html', context)

def admin_settings(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    settings_obj, created = SubscriptionSettings.objects.get_or_create(id=1)
    
    if request.method == "POST":
        amount = request.POST.get('amount')
        settings_obj.amount = amount
        settings_obj.save()
        messages.success(request, "Subscription amount updated successfully.")
        return redirect('/admin_settings/')
        
    return render(request, 'admin/admin_settings.html', {'settings': settings_obj})

def userhome(request):
    if not request.session.get("uid") or request.session.get("usertype") != "User":
        return redirect('/login')

    if "user_name" not in request.session:
        uid = request.session["uid"]
        try:
            user_profile = UserRegistration.objects.get(loginid_id=uid)
            if user_profile.name:
                request.session["user_name"] = user_profile.name
            else:
                l = Login.objects.get(id=uid)
                request.session["user_name"] = l.email.split('@')[0].capitalize()
        except (UserRegistration.DoesNotExist, Login.DoesNotExist):
            try:
                l = Login.objects.get(id=uid)
                request.session["user_name"] = l.email.split('@')[0].capitalize()
            except:
                request.session["user_name"] = "User"

    return render(request,'user/userhome.html')

def nutrihome(request):
    if not request.session.get("uid") or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
    return render(request,'nutritionists/nutrihome.html')


def nutritionreg(request):
    if request.POST:
        name=request.POST['name']
        username=request.POST['user_name']
        email=request.POST['user_email']
        phone=request.POST['user_phone']
        qualification=request.POST['qualification']
        experience=request.POST['experience']
        password=request.POST['user_password']
        confirmpassword=request.POST['user_confirm_password']
        if password==confirmpassword:
            if Login.objects.filter(email=email).exists():
                messages.error(request, "Email already registered... Please Login")
                return redirect('/nutritionreg/')
            elif NutritionistRegistration.objects.filter(username=username).exists():
                messages.error(request, "Username already taken! Choose another.")
                return redirect('/nutritionreg/')
            else:
                NLogin = Login.objects.create(
                    email=email, password=password, status="pending", usertype="Nutritionist"
                )
                NLogin.save()
                userReg = NutritionistRegistration.objects.create(
                    name=name, username=username, email=email, phone=phone, qualification=qualification, experience=experience, password=password, loginid=NLogin
                )
                userReg.save()
                messages.success(request, "Nutritionist Registration Success. Waiting for approval!")
                return redirect('/login/')
        else:
            messages.error(request, "Password Mismatch!")
            return redirect('/nutritionreg/')

    return render(request,'nutritionreg.html')



def viewuser(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    abc=Login.objects.filter(status="pending")
    return render(request,'admin/viewuser.html')


def approveuser(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    uid=request.GET["id"]
    update=Login.objects.filter(id=uid).update(status="Approved")
    return HttpResponseRedirect("/viewuser")


def rejectuser(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    uid=request.GET["id"]
    update=Login.objects.filter(id=uid).update(status="Rejected")
    return HttpResponseRedirect("/viewusers")

def approvenutritionist(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    uid=request.GET["id"]
    update=Login.objects.filter(id=uid).update(status="Approved")
    return HttpResponseRedirect("/viewnutritionists")

def rejectnutritionist(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    uid=request.GET["id"]
    update=Login.objects.filter(id=uid).update(status="Rejected")
    return HttpResponseRedirect("/viewnutritionists")
    

def viewnutritionist(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    return render(request,'admin/viewnutritionist.html')

def deleteuser(request, id):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    try:
        # Find the login object first as it's the primary reference
        login_obj = Login.objects.get(id=id)
        usertype = login_obj.usertype
        
        # Delete the login object (cascades to UserRegistration/NutritionistRegistration)
        login_obj.delete()
        
        messages.success(request, "User deleted successfully!")
        
        # Redirect based on who we deleted
        if usertype == "User":
            return redirect('/viewusers')
        else:
            return redirect('/viewnutritionists')
            
    except Login.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('/homepage')


def adddietplan(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')

    if request.method == "POST":
        dietplan = request.POST.get('dietplan')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        breakfast = request.POST.get('breakfast')
        lunch = request.POST.get('lunch')
        dinner = request.POST.get('dinner')
        intermediate_foods = request.POST.get('intermediate_foods')
        calories = request.POST.get('calories', 0) or 0
        protein = request.POST.get('protein', 0) or 0
        carbs = request.POST.get('carbs', 0) or 0
        fats = request.POST.get('fats', 0) or 0
        drinking_water = request.POST.get('drinking_water')
        sleeping_hours = request.POST.get('sleeping_hours')
        activity = request.POST.get('activity')
        notes = request.POST.get('notes', '')

        # Get Nutritionist Login Object
        try:
            nutritionist_login = Login.objects.get(id=uid)
            Dietplan.objects.create(
                dietplan=dietplan, 
                category=category, 
                description=description,
                breakfast=breakfast, 
                lunch=lunch, 
                dinner=dinner, 
                intermediate_foods=intermediate_foods, 
                calories=calories,
                protein=protein,
                carbs=carbs,
                fats=fats,
                drinking_water=drinking_water, 
                sleeping_hours=sleeping_hours, 
                activity=activity,
                notes=notes,
                loginid=nutritionist_login
            )
            messages.success(request, "Diet Plan Added Successfully")
        except Login.DoesNotExist:
            return redirect('/login')


    return render(request,'nutritionists/adddietplan.html') 


def adminviewdietplan(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    # Exclude custom plans created for specific users
    plans = Dietplan.objects.filter(is_custom=False, custom_for_user__isnull=True)
    if category:
        plans = plans.filter(category=category)
    if search:
        plans = plans.filter(dietplan__icontains=search)
        
    return render(request, 'admin/adminviewdietplan.html', {
        'userData': plans,
        'current_category': category,
        'search_query': search
    })


def viewusers(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    userData = UserRegistration.objects.all()
    print(userData)
    return render(request, "admin/viewusers.html", {"userData": userData})


def viewnutritionists(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    userData = NutritionistRegistration.objects.all()
    print(userData)
    return render(request, "admin/viewnutritionists.html", {"userData": userData})


# Removed duplicate viewdietplan

def userviewdietplan(request):
    uid = request.session.get('uid')
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')

    context = {
        'personalized_plans': [],
        'recommended_plans': [],
        'user_goal': None
    }
    
    try:
        user_login = Login.objects.get(id=uid)
        user_profile = UserRegistration.objects.get(loginid_id=uid)
        user_goal = user_profile.health_goal
        context['user_goal'] = user_goal
        
        # 1. Fetch plans explicitly assigned to this user via assignments
        assigned_via_requests = Dietplan.objects.filter(
            dietplanassignment__request__user=user_login
        )
        
        # 2. Fetch plans marked as custom for this user
        custom_plans = Dietplan.objects.filter(
            custom_for_user=user_login, 
            is_custom=True
        )
        
        # Merge them into personalized_plans
        context['personalized_plans'] = (assigned_via_requests | custom_plans).distinct()
        
        # 3. Fetch general plans matching the user's goal
        if user_goal:
            # Only show plans with matching category, excluding ones already in personalized
            context['recommended_plans'] = Dietplan.objects.filter(
                category=user_goal, 
                is_custom=False
            ).exclude(id__in=context['personalized_plans'])
        else:
            # If no goal is set, we don't show any general "recommended" plans
            context['recommended_plans'] = []
                
    except (Login.DoesNotExist, UserRegistration.DoesNotExist):
        pass

    return render(request, "user/userviewdietplan.html", context)


def nutriviewdietplan(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
    
    # Sort by ID descending so newest/revised plans appear first
    userData = Dietplan.objects.filter(loginid=uid).order_by('-id')
    return render(request, "nutritionists/nutriviewdietplan.html", {"userData": userData})

def update_diet(request):
    if not request.session.get("uid") or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')

    id=request.GET['id']
    print(id)
    
    userData = Dietplan.objects.filter(id=id)

    if request.method == "POST":
        dietplan = request.POST['dietplan']
        category = request.POST['category']
        description = request.POST.get('description', '')
        breakfast = request.POST['breakfast']
        lunch = request.POST['lunch']
        dinner = request.POST['dinner']
        intermediate_foods = request.POST['intermediate_foods']
        calories = request.POST.get('calories', 0) or 0
        protein = request.POST.get('protein', 0) or 0
        carbs = request.POST.get('carbs', 0) or 0
        fats = request.POST.get('fats', 0) or 0
        drinking_water = request.POST['drinking_water']
        sleeping_hours = request.POST['sleeping_hours']
        activity = request.POST['activity']
        notes = request.POST.get('notes', '')

        obj=Dietplan.objects.filter(id=id).update(
            dietplan=dietplan, 
            category=category, 
            description=description,
            breakfast=breakfast, 
            lunch=lunch, 
            dinner=dinner, 
            intermediate_foods=intermediate_foods, 
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
            drinking_water=drinking_water, 
            sleeping_hours=sleeping_hours, 
            activity=activity,
            notes=notes
        )

        messages.success(request, "Diet Plan Updated Successfully")
        return redirect('/nutriviewdietplan')

    return render(request, "nutritionists/updatedietplan.html", {"userData": userData})
    



def updatedietplan(request):
    if not request.session.get("uid") or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
    return render(request,'nutritionists/updatedietplan.html') 


def deletediet(request):
    uid = request.session.get("uid")
    usertype = request.session.get("usertype")
    if not uid or usertype not in ["Nutritionist", "admin"]:
        return redirect('/login')
    
    pid = request.GET.get('id')
    if pid:
        Dietplan.objects.filter(id=pid).delete()
    
    if usertype == "admin":
        return redirect('/viewdietplan')
    return redirect('/nutriviewdietplan')
# User Request Views
def request_diet(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')
        
    user_details = {}
    try:
        user_reg = UserRegistration.objects.get(loginid_id=uid)
        user_details = {
            'age': user_reg.age,
            'height': user_reg.height,
            'weight': user_reg.weight,
            'gender': user_reg.gender,
            'health_goal': user_reg.health_goal
        }
    except UserRegistration.DoesNotExist:
        pass

    if request.method == "POST":
        login_obj = Login.objects.get(id=uid)
        health_goal = request.POST.get('health_goal')
        
        # --- SCIENTIFIC CALCULATION (Mifflin-St Jeor) ---
        try:
            age = int(request.POST.get('age'))
            height = float(request.POST.get('height'))
            weight = float(request.POST.get('weight'))
            gender = request.POST.get('gender')
            activity_level = request.POST.get('activity_level')
            
            # Step 1: Calculate BMR
            if gender == 'Male':
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else: # Female or Other (using Female formula as baseline or average)
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
                
            # Step 2: Activity Multiplier
            multiplier = 1.2 # Default Sedentary
            if activity_level == 'Lightly Active': multiplier = 1.375
            elif activity_level == 'Moderately Active': multiplier = 1.55
            elif activity_level == 'Very Active': multiplier = 1.725
            elif activity_level == 'Extra Active': multiplier = 1.9
            
            tdee = bmr * multiplier
            
            # Step 3: Adjust for Goal
            target_calories = tdee
            diet_type = "Balanced"
            
            if health_goal == 'Weight Loss':
                target_calories = tdee - 500
                diet_type = "Low Carb / High Fibre / Calorie Deficit"
            elif health_goal == 'Muscle Gain':
                target_calories = tdee + 300
                diet_type = "High Protein / High Carb / Calorie Surplus"
            elif health_goal == 'Maintenance':
                diet_type = "Balanced Diet / Maintenance Calories"
                
            # Step 4: Final String
            calculated_needs = f"{int(target_calories)} kcal/day - {diet_type}"
            
        except (ValueError, TypeError):
            # Fallback if parsing fails
            calculated_needs = "Calculation Failed (Check inputs)"

        DietRequest.objects.create(
            user=login_obj,
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            health_goal=health_goal,
            activity_level=activity_level,
            calculated_needs=calculated_needs,
            # Detailed Info
            food_preference=request.POST.get('food_preference'),
            allergies=request.POST.get('allergies'),
            medical_conditions=request.POST.get('medical_conditions'),
            daily_routine=request.POST.get('daily_routine'),
            dietary_history=request.POST.get('dietary_history'),
            
            description=request.POST.get('description')
        )
        messages.success(request, "Diet Plan Request Submitted Successfully!")
        return redirect('/my_requests')

    return render(request, 'user/request_diet.html', {'user_details': user_details})

def my_requests(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')
    
    my_reqs = DietRequest.objects.filter(user_id=uid).order_by('-request_date')
    
    # Get subscription amount
    settings_obj, _ = SubscriptionSettings.objects.get_or_create(id=1)
    
    # Check if user has ANY paid subscription
    has_any_payment = Payment.objects.filter(user_id=uid, status='paid').exists()
    
    # Enrich requests with payment status
    for req in my_reqs:
        latest = req.latest_assignment
        if latest:
            # Unlock chat if user has paid for ANY assignment
            latest.is_paid = has_any_payment 
            req.enriched_assignment = latest # Store it specifically to avoid property re-query

    return render(request, 'user/my_requests.html', {
        'my_requests': my_reqs,
        'subscription_amount': settings_obj.amount
    })

def request_detail(request, request_id):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')
    
    diet_request = get_object_or_404(DietRequest, id=request_id, user_id=uid)
    assignment = diet_request.latest_assignment
    
    if assignment:
        assignment.is_paid = Payment.objects.filter(user_id=uid, status='paid').exists()
        
    return render(request, 'user/request_detail.html', {
        'req': diet_request,
        'assign': assignment
    })

def pay_subscription(request, assignment_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login')
        
    assignment = get_object_or_404(DietPlanAssignment, id=assignment_id)
    settings_obj, _ = SubscriptionSettings.objects.get_or_create(id=1)
    
    return render(request, 'user/payment_page.html', {
        'assignment': assignment,
        'amount': settings_obj.amount
    })

def process_payment(request, assignment_id):
    uid = request.session.get('uid')
    if not uid:
        return redirect('/login')
        
    assignment = get_object_or_404(DietPlanAssignment, id=assignment_id)
    settings_obj, _ = SubscriptionSettings.objects.get_or_create(id=1)
    
    # Mocking successful payment
    Payment.objects.create(
        assignment=assignment,
        user=Login.objects.get(id=uid),
        amount=settings_obj.amount,
        status='paid'
    )
    
    return render(request, 'user/payment_success.html')

def accept_plan(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')
    
    assignment_id = request.GET.get('assignment_id')
    assignment = get_object_or_404(DietPlanAssignment, id=assignment_id)
    
    # Mark this assignment as selected and others for the same request as suggested (or not selected)
    # Also update original request status
    assignment.status = 'selected'
    assignment.save()
    
    DietPlanAssignment.objects.filter(request=assignment.request).exclude(id=assignment.id).update(status='suggested')
    
    messages.success(request, f"You have accepted the plan: {assignment.diet_plan.dietplan}")
    return redirect('/my_requests')


# Nutritionist Views
def view_diet_requests(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
    
    # Calculate BMI for display logic if needed or just pass raw data
    reqs = DietRequest.objects.all().order_by('-request_date')
    request_list = []
    for r in reqs:
        bmi = 0
        if r.height and r.weight:
            h_m = r.height / 100
            bmi = r.weight / (h_m * h_m)
        r.bmi = bmi
        request_list.append(r)
        
    return render(request, 'nutritionists/view_requests.html', {'requests': request_list})

def suggest_plan(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
        
    request_id = request.GET.get('request_id') or request.POST.get('request_id')
    req_obj = get_object_or_404(DietRequest, id=request_id)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "create_custom":
            # Create a new custom plan
            plan_name = f"Custom Plan for {req_obj.user.userregistration_set.first().name}"
            category = req_obj.health_goal
            
            diet_plan = Dietplan.objects.create(
                dietplan=plan_name,
                category=category,
                description=request.POST.get('description', ''),
                breakfast=request.POST.get('breakfast'),
                lunch=request.POST.get('lunch'),
                dinner=request.POST.get('dinner'),
                intermediate_foods=request.POST.get('intermediate_foods', 'None'),
                calories=request.POST.get('calories', 0) or 0,
                protein=request.POST.get('protein', 0) or 0,
                carbs=request.POST.get('carbs', 0) or 0,
                fats=request.POST.get('fats', 0) or 0,
                drinking_water=request.POST.get('drinking_water', 'pending'),
                sleeping_hours=request.POST.get('sleeping_hours', 'pending'),
                activity=request.POST.get('activity', 'pending'),
                notes=request.POST.get('notes', ''),
                loginid=Login.objects.get(id=uid),
                is_custom=True,
                custom_for_user=req_obj.user
            )
            comments = "Custom plan created specifically for your needs."
            
        else:
            # Assign existing plan
            diet_plan_id = request.POST.get('diet_plan_id')
            comments = request.POST.get('comments')
            
            if not diet_plan_id:
                messages.error(request, "Please select a diet plan to assign.")
                return redirect(f'/suggest_plan/?request_id={request_id}')
                
            diet_plan = get_object_or_404(Dietplan, id=diet_plan_id)

        nutritionist = Login.objects.get(id=uid)
        
        DietPlanAssignment.objects.create(
            request=req_obj,
            diet_plan=diet_plan,
            nutritionist=nutritionist,
            comments=comments
        )
        
        req_obj.status = 'replied'
        req_obj.save()
        
        messages.success(request, "Plan assigned successfully!")
        return redirect('/view_diet_requests')
        
    diet_plans = Dietplan.objects.filter(is_custom=False)
    
    # Fetch previous custom plan if it exists for this request to pre-fill the form
    previous_plan = Dietplan.objects.filter(
        dietplanassignment__request=req_obj, 
        is_custom=True
    ).order_by('-id').first()
    
    context = {
        'request_obj': req_obj, 
        'diet_plans': diet_plans,
        'previous_plan': previous_plan
    }
    
    return render(request, 'nutritionists/suggest_plan.html', context)

def request_revision(request):
    if request.method == "POST":
        assignment_id = request.POST.get('assignment_id')
        reason = request.POST.get('reason')
        
        assignment = get_object_or_404(DietPlanAssignment, id=assignment_id)
        assignment.status = 'revision_requested'
        assignment.rejection_reason = reason
        assignment.save()
        
        messages.info(request, "Revision requested successfully. Your nutritionist will update the plan.")
        return redirect('/my_requests')

def chat_view(request, assignment_id):
    uid = request.session.get("uid")
    if not uid:
        return redirect('/login')
        
    assignment = get_object_or_404(DietPlanAssignment, id=assignment_id)
    
    # Access Control: Only the user or the nutritionist involved can access
    if assignment.request.user.id != uid and assignment.nutritionist.id != uid:
        messages.error(request, "Unauthorized access to this chat.")
        return redirect('/')
        
    if request.method == "POST":
        message = request.POST.get('message')
        sender = Login.objects.get(id=uid)
        
        ChatMessage.objects.create(
            assignment=assignment,
            sender=sender,
            message=message
        )
        return redirect(f'/chat/{assignment_id}/')
        
    messages = ChatMessage.objects.filter(assignment=assignment).order_by('timestamp')
    
    # Payment Check for Users - Allow if ANY assignment has been paid for
    if request.session.get("usertype") == 'User':
        if not Payment.objects.filter(user_id=uid, status='paid').exists():
            messages.error(request, "Please pay the subscription amount to access chat.")
            return redirect('/my_requests')
    
    # Determine base template based on user type
    base_template = 'base.html' if request.session.get("usertype") == 'User' else 'nutritionists/base.html'
    
    return render(request, 'chat.html', {
        'assignment': assignment,
        'messages': messages,
        'base_template': base_template,
        'uid': uid # Pass uid to template to identify my messages
    })

def nutritionist_assignments(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "Nutritionist":
        return redirect('/login')
        
    assignments = DietPlanAssignment.objects.filter(nutritionist_id=uid).order_by('-assigned_date')
    
    # Check if user has paid for chat access
    for assignment in assignments:
        assignment.is_paid = Payment.objects.filter(user=assignment.request.user, status='paid').exists()
        
    return render(request, 'nutritionists/my_assignments.html', {'assignments': assignments})

def view_payments(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    from django.db.models import Sum
    payments = Payment.objects.all().order_by('-timestamp')
    total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'admin/view_payments.html', {
        'payments': payments,
        'total_revenue': total_revenue
    })

def submit_feedback(request):
    uid = request.session.get('uid')
    
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        rating = request.POST.get('rating')
        
        # Get user if logged in
        user_obj = None
        if uid:
            try:
                user_obj = Login.objects.get(id=uid)
            except Login.DoesNotExist:
                pass
        
        Feedback.objects.create(
            user=user_obj,
            name=name,
            email=email,
            subject=subject,
            message=message,
            rating=rating if rating else None
        )
        
        
        return redirect('/')
    
    # Pre-fill data if user is logged in
    user_data = {}
    if uid:
        try:
            user_login = Login.objects.get(id=uid)
            user_data['email'] = user_login.email
            
            # Try to get name from UserRegistration
            try:
                user_profile = UserRegistration.objects.get(loginid=user_login)
                user_data['name'] = user_profile.name
            except UserRegistration.DoesNotExist:
                user_data['name'] = user_login.email.split('@')[0]
        except Login.DoesNotExist:
            pass
    
    return render(request, 'user/feedback.html', {'user_data': user_data})

def view_feedback(request):
    if not request.session.get("uid") or request.session.get("usertype") != "admin":
        return redirect('/login')
    
    feedbacks = Feedback.objects.all().order_by('-submitted_date')
    
    return render(request, 'admin/view_feedback.html', {'feedbacks': feedbacks})

def edit_profile(request):
    uid = request.session.get("uid")
    if not uid or request.session.get("usertype") != "User":
        return redirect('/login')
        
    user_login = get_object_or_404(Login, id=uid)
    user_profile = get_object_or_404(UserRegistration, loginid=user_login)
    
    if request.method == "POST":
        user_profile.name = request.POST.get('name')
        user_profile.phone = request.POST.get('phone')
        user_profile.age = request.POST.get('age')
        user_profile.height = request.POST.get('height')
        user_profile.weight = request.POST.get('weight')
        user_profile.gender = request.POST.get('gender')
        user_profile.health_goal = request.POST.get('health_goal')
        user_profile.save()
        
        request.session["user_name"] = user_profile.name
        messages.success(request, "Profile updated successfully!")
        return redirect('/edit_profile')
        
    return render(request, 'user/edit_profile.html', {'user': user_profile})

def recommend_diet(request):
    if not request.session.get("uid"):
        return redirect('/login')
        
    result = None
    if request.method == 'POST':
        form = DietForm(request.POST)
        if form.is_valid():
            result = get_diet_recommendation(form.cleaned_data)
    else:
        uid = request.session.get("uid")
        initial_data = {}
        try:
             user_reg = UserRegistration.objects.get(loginid_id=uid)
             initial_data = {
                 'age': user_reg.age,
                 'weight': user_reg.weight,
                 'height': user_reg.height,
                 'gender': user_reg.gender,
                 'goal': user_reg.health_goal
             }
        except:
            pass
        form = DietForm(initial=initial_data)
    
    return render(request, 'user/recommend_diet.html', {'form': form, 'result': result})

def calorie_finder(request):
    if not request.session.get("uid"):
        return redirect('/login')

    result = None
    error = None
    suggestions = None

    if request.method == 'POST':
        form = CalorieForm(request.POST)
        if form.is_valid():
            food = form.cleaned_data['food_item']
            weight = form.cleaned_data['weight']
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

    return render(request, 'user/calorie_finder.html', {
        'form': form, 
        'result': result, 
        'error': error,
        'suggestions': suggestions
    })
