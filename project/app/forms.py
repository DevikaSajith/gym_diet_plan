from django import forms

class DietForm(forms.Form):
    age = forms.FloatField(label='Age', min_value=1, max_value=120)
    gender = forms.ChoiceField(label='Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    weight = forms.FloatField(label='Weight (kg)', min_value=1)
    height = forms.FloatField(label='Height (cm)', min_value=1)
    
    DISEASE_CHOICES = [
        ('None', 'None'),
        ('Diabetes', 'Diabetes'),
        ('Hypertension', 'Hypertension'),
        ('Obesity', 'Obesity'),
    ]
    disease = forms.ChoiceField(label='Disease / Condition', choices=DISEASE_CHOICES)
    
    ACTIVITY_CHOICES = [
        ('Sedentary', 'Sedentary'),
        ('Moderate', 'Moderate'),
        ('Active', 'Active'),
    ]
    activity = forms.ChoiceField(label='Physical Activity Level', choices=ACTIVITY_CHOICES)
    
    ALLERGY_CHOICES = [
        ('None', 'None'),
        ('Peanuts', 'Peanuts'),
        ('Gluten', 'Gluten'),
    ]
    allergies = forms.ChoiceField(label='Allergies', choices=ALLERGY_CHOICES)
    
    CUISINE_CHOICES = [
        ('Mexican', 'Mexican'),
        ('Chinese', 'Chinese'),
        ('Italian', 'Italian'),
        ('Indian', 'Indian'),
        ('Any', 'Any'),
    ]
    cuisine = forms.ChoiceField(label='Preferred Cuisine', choices=CUISINE_CHOICES)
    
    GOAL_CHOICES = [
        ('Weight Loss', 'Weight Loss'),
        ('Weight Gain', 'Weight Gain'),
        ('Maintain', 'Maintain'),
        ('Build Muscle', 'Build Muscle'),
    ]
    goal = forms.ChoiceField(label='Fitness Goal', choices=GOAL_CHOICES)

    exercise_hours = forms.FloatField(label='Weekly Exercise Hours', min_value=0, required=False, initial=4.0)

class CalorieForm(forms.Form):
    food_item = forms.CharField(label='Food Name', max_length=100)
    weight = forms.FloatField(label='Weight (grams)', min_value=0.1)
