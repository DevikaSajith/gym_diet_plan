"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    # Admin & Auth URLs
    path('admin/', admin.site.urls),
    path('', views.home),
    path('login/', views.login),
    path('logout/', views.logout),
    path('registration/', views.registration),
    path('about/', views.about),
    path('homepage/', views.homepage),
    path('userhome/', views.userhome),
    path('nutritionreg/', views.nutritionreg),
    path('nutrihome/', views.nutrihome),
    path('viewuser/', views.viewuser),
    path('viewnutritionist/', views.viewnutritionist),
    path('viewdietplan/' , views.adminviewdietplan),
    path('adddietplan/' , views.adddietplan),
    path("viewusers/", views.viewusers),
    path("approveuser/", views.approveuser),
    path("rejectuser/", views.rejectuser),
    path("viewnutritionists/" , views.viewnutritionists),
    path("approvenutritionist/", views.approvenutritionist),
    path("rejectnutritionist/", views.rejectnutritionist),
    path("deleteuser/<int:id>/", views.deleteuser),
    path("userviewdietplan/" , views.userviewdietplan),
    path("nutriviewdietplan/" , views.nutriviewdietplan),
    path("update_diet/" , views.update_diet),
    path("updatedietplan/" , views.updatedietplan),
    path("deletediet/" , views.deletediet),
    
    # Diet Request Flow URLs
    path("request_diet/", views.request_diet),
    path("my_requests/", views.my_requests),
    path("accept_plan/", views.accept_plan),
    path("request_revision/", views.request_revision),
    path("view_diet_requests/", views.view_diet_requests),
    path("suggest_plan/", views.suggest_plan),
    path("request_detail/<int:request_id>/", views.request_detail),
    
    # Chat & Assignment URLs
    path("nutritionist_assignments/", views.nutritionist_assignments),
    path("chat/<int:assignment_id>/", views.chat_view),
    path("admin_settings/", views.admin_settings),
    path("pay_subscription/<int:assignment_id>/", views.pay_subscription),
    path("process_payment/<int:assignment_id>/", views.process_payment),
    path("view_payments/", views.view_payments),
    
    # Feedback URLs
    path("submit_feedback/", views.submit_feedback),
    path("view_feedback/", views.view_feedback),
    path("edit_profile/", views.edit_profile),
    path("recommend_diet/", views.recommend_diet),
    path("calorie_finder/", views.calorie_finder),
]
