# Dietary Management System - ER Diagram Schema Documentation

This document provides a detailed breakdown of the schema for the Entity-Relationship (ER) diagram of the Gym/Dietary Management System. It explains the various entities (derived from the Django models), their attributes, and their relationships within the system.

---

## 1. Entities and Attributes

### 1.1 Login
Manages authentication credentials and user roles for all types of users in the system.
*   **id** *(Primary Key)*: Unique identifier.
*   **email**: Email address used for authentication.
*   **password**: User's password.
*   **status**: Current account status (e.g., active, inactive).
*   **usertype**: The role of the user (e.g., 'user', 'nutritionist', 'admin').

### 1.2 UserRegistration
Stores detailed profile information for standard users seeking dietary plans.
*   **id** *(Primary Key)*: Unique identifier.
*   **name, email, phone, password**: Basic contact and identity information.
*   **age, height, weight, gender**: Biometric data.
*   **activity_level**: The user's physical activity (e.g., sedentary, active).
*   **health_goal**: Desired outcome (e.g., Weight Loss, Muscle Gain).
*   **loginid** *(Foreign Key)*: Links to the corresponding `Login` credential.

### 1.3 NutritionistRegistration
Stores detailed profile and professional information for nutritionists.
*   **id** *(Primary Key)*: Unique identifier.
*   **name, username, email, phone, password**: Basic contact and identity information.
*   **qualification**: Educational or professional degrees.
*   **experience**: Years/details of professional experience.
*   **loginid** *(Foreign Key)*: Links to the corresponding `Login` credential.

### 1.4 Dietplan
Represents dietary plans that can be standard or customized for specific users.
*   **id** *(Primary Key)*: Unique identifier.
*   **dietplan**: Name or title of the plan.
*   **category**: Category of the plan (e.g., Weight Loss, Muscle Gain).
*   **description**: Detailed description of the plan's purpose.
*   **breakfast, lunch, dinner, intermediate_foods**: Meal-specific details.
*   **calories, protein, carbs, fats**: Nutritional macros.
*   **drinking_water, sleeping_hours, activity, notes**: Additional lifestyle recommendations.
*   **is_custom**: Boolean flag indicating if the plan is uniquely tailored.
*   **loginid** *(Foreign Key)*: Links to the Nutritionist (`Login`) who created it.
*   **custom_for_user** *(Foreign Key)*: Links to a User (`Login`) if custom-made.

### 1.5 DietRequest
Captures a user's specific request for a new or customized diet plan.
*   **id** *(Primary Key)*: Unique identifier.
*   **age, height, weight, gender, health_goal, activity_level**: User's condition at the time of request.
*   **calculated_needs**: Automatically derived nutritional needs.
*   **food_preference, allergies, medical_conditions, daily_routine, dietary_history**: In-depth personal details for accurate suggestion.
*   **description, status, request_date**: Metadata logging the request's state and time.
*   **user** *(Foreign Key)*: Links to the requesting User (`Login`).

### 1.6 DietPlanAssignment
Represents the mapping/assignment of a specific diet plan to satisfy a user's diet request.
*   **id** *(Primary Key)*: Unique identifier.
*   **status**: Lifecycle state of the assignment (e.g., suggested, selected).
*   **assigned_date, comments, rejection_reason**: Feedback and timing metadata.
*   **request** *(Foreign Key)*: Links to the originating `DietRequest`.
*   **diet_plan** *(Foreign Key)*: Links to the suggested/assigned `Dietplan`.
*   **nutritionist** *(Foreign Key)*: Links to the assigning Nutritionist (`Login`).

### 1.7 ChatMessage
Handles communications and chat messages concerning a specific diet plan assignment.
*   **id** *(Primary Key)*: Unique identifier.
*   **message, timestamp**: Content and execution time of the message.
*   **assignment** *(Foreign Key)*: Links to the context, `DietPlanAssignment`.
*   **sender** *(Foreign Key)*: Links to the message author (`Login`).

### 1.8 SubscriptionSettings
Stores global or tiered subscription pricing.
*   **id** *(Primary Key)*: Unique identifier.
*   **amount**: Global cost figure.

### 1.9 Payment
Records financial transactions related to a plan assignment.
*   **id** *(Primary Key)*: Unique identifier.
*   **amount, status, timestamp**: Transaction details.
*   **assignment** *(Foreign Key)*: Links to the paid `DietPlanAssignment`.
*   **user** *(Foreign Key)*: Links to the paying User (`Login`).

### 1.10 Feedback
Manages system or nutritionist feedback submitted by users.
*   **id** *(Primary Key)*: Unique identifier.
*   **name, email, subject, message, rating**: Content of the feedback.
*   **submitted_date, status**: Processing metadata.
*   **user** *(Foreign Key)*: Links back to the User (`Login`) creating it.

---

## 2. Core Relationships

1. **Authentication Core (`Login`)**:
   `Login` acts as the central hub for mapping roles. Every `UserRegistration` and `NutritionistRegistration` connects directly to a `Login` record. Most actions (Requests, Chat, Payments, Feedback) are directly tied to a user's `Login` ID.

2. **Plan Creation & Customization**:
   A `Nutritionist` (via `Login`) creates multiple `Dietplan` records (`1-to-many`). A `Dietplan` can be linked exclusively to a `User` (via `Login`) if the `is_custom` flag is raised, utilizing the `custom_for_user` foreign key.

3. **Request Lifecycle**:
   A `User` creates a `DietRequest`. A `Nutritionist` reviews this request and creates a `DietPlanAssignment`, which acts as a bridge connecting the `DietRequest` to an optimal `Dietplan`.

4. **Interaction & Billing**:
   *   Once a `DietPlanAssignment` exists, `User` and `Nutritionist` can exchange `ChatMessage` records structured under that assignment.
   *   A `Payment` is tied directly to the `DietPlanAssignment` and the `User` making the payment.
   *   `Feedback` can be organically submitted by a `User` and optionally tracked via their `Login`.
