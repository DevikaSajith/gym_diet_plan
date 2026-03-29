from django.db import models

# Create your models here.
class Login(models.Model):
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    usertype = models.CharField(max_length=100, null=True, blank=True)


class UserRegistration(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True) # in cm
    weight = models.FloatField(null=True, blank=True) # in kg
    gender = models.CharField(max_length=10, null=True, blank=True)
    activity_level = models.CharField(max_length=50, null=True, blank=True) 
    health_goal = models.CharField(max_length=50, null=True, blank=True) # e.g., Weight Loss, Muscle Gain
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)


class NutritionistRegistration(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=300, null=True, blank=True)
    experience = models.CharField(max_length=100, null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)


class Dietplan(models.Model):
    CATEGORY_CHOICES = (
        ('Weight Loss', 'Weight Loss'),
        ('Muscle Gain', 'Muscle Gain'),
        ('Maintenance', 'Maintenance'),
    )

    dietplan = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(null=True, blank=True)
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()
    intermediate_foods = models.TextField()
    
    # Nutritional Info
    calories = models.PositiveIntegerField(default=0)
    protein = models.PositiveIntegerField(default=0)
    carbs = models.PositiveIntegerField(default=0)
    fats = models.PositiveIntegerField(default=0)
    
    drinking_water = models.TextField(default="pending")
    sleeping_hours = models.TextField(default="pending")
    activity = models.TextField(default="pending")
    notes = models.TextField(null=True, blank=True)
    
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE, null=True)
    
    # Custom Plan Fields
    is_custom = models.BooleanField(default=False)
    custom_for_user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_plans')


    def __str__(self):
        return self.dietplan

class DietRequest(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='diet_requests')
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    health_goal = models.CharField(max_length=50, null=True, blank=True)
    activity_level = models.CharField(max_length=50, null=True, blank=True)
    calculated_needs = models.CharField(max_length=100, null=True, blank=True)
    
    # Detailed Information for Manual Suggestion
    food_preference = models.CharField(max_length=50, null=True, blank=True, help_text="e.g., Veg, Non-Veg, Vegan")
    allergies = models.TextField(null=True, blank=True, help_text="List of allergies")
    medical_conditions = models.TextField(null=True, blank=True, help_text="Any existing medical conditions")
    daily_routine = models.TextField(null=True, blank=True, help_text="Brief about daily activity, sleep, etc.")
    dietary_history = models.TextField(null=True, blank=True, help_text="Current eating habits")
    
    description = models.TextField(help_text="User's specific request or conditions")
    status = models.CharField(max_length=20, default='pending') # pending, replied
    request_date = models.DateTimeField(auto_now_add=True)

    @property
    def latest_assignment(self):
        return self.assignments.order_by('-assigned_date').first()

    def __str__(self):
        return f"Request by {self.user.email} - {self.status}"

class DietPlanAssignment(models.Model):
    request = models.ForeignKey(DietRequest, on_delete=models.CASCADE, related_name='assignments')
    diet_plan = models.ForeignKey(Dietplan, on_delete=models.CASCADE)
    nutritionist = models.ForeignKey(Login, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='suggested') # suggested, selected
    assigned_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Plan {self.diet_plan.dietplan} for {self.request.user.email}"

class ChatMessage(models.Model):
    assignment = models.ForeignKey(DietPlanAssignment, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Login, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.email} at {self.timestamp}"

class SubscriptionSettings(models.Model):
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"Subscription Amount: {self.amount}"

class Payment(models.Model):
    assignment = models.ForeignKey(DietPlanAssignment, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.CharField(max_length=20, default='paid') # mock payment status
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.user.email}"

class Feedback(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True)  # 1-5 star rating
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, reviewed

    def __str__(self):
        return f"Feedback from {self.name} - {self.subject}"