# Project Architecture and Diagrams

This document outlines the high-level architecture, entity-relationship models, system use cases, and class structures of the **Dietary Management System**.

## 1. System Architecture Diagram

This flowchart visualizes the underlying software architecture and the logical progression of data between the frontend user interface, backend Django server, internal algorithms, and the database.

```mermaid
flowchart TD
    subgraph Client [Client Side / Browser]
        UI[Web Templates / HTML CSS JS]
    end

    subgraph Django_Backend [Django Server]
        URL[URL Routing / urls.py]
        Views[View Functions / views.py]
        Models[Data Models / models.py]
        Utils[ML Algorithm & Logic / utils.py]
    end
    
    subgraph Data_Layer [Data & Storage]
        DB[(SQLite Database)]
        CSV[Datasets: diet_recommendations.csv, calories.csv]
    end

    Client -- HTTP Request --> URL
    URL --> Views
    Views -- Queries --> Models
    Views -- Context --> UI
    Views -- Triggers KNN --> Utils
    Models <--> DB
    Utils -- Reads History --> CSV
```

---

## 2. Entity-Relationship (ER) Diagram

The ER Diagram defines the relational structure of the database tables and how the entities connect via foreign keys.

```mermaid
erDiagram
    LOGIN ||--o| USER_REGISTRATION : "has profile"
    LOGIN ||--o| NUTRITIONIST_REGISTRATION : "has profile"
    LOGIN ||--o{ DIETPLAN : "creates / custom assigned"
    LOGIN ||--o{ DIET_REQUEST : "submits"
    LOGIN ||--o{ FEEDBACK : "gives"
    LOGIN ||--o{ PAYMENT : "makes"
    
    DIET_REQUEST ||--o{ DIET_ASSIGNMENT : "receives"
    DIETPLAN ||--o{ DIET_ASSIGNMENT : "is applied to"
    LOGIN ||--o{ DIET_ASSIGNMENT : "nutritionist assigns"
    
    DIET_ASSIGNMENT ||--o{ CHAT_MESSAGE : "contains"
    LOGIN ||--o{ CHAT_MESSAGE : "sends"
    
    DIET_ASSIGNMENT ||--o{ PAYMENT : "unlocks chat for"

    LOGIN {
        int id PK
        string email
        string password
        string status
        string usertype
    }
    
    DIET_REQUEST {
        int id PK
        int user_id FK
        float height
        float weight
        string health_goal
        string calculated_needs
        string status
    }
    
    DIETPLAN {
        int id PK
        string dietplan_name
        string category
        int calories
        boolean is_custom
        int loginid FK
    }
    
    DIET_ASSIGNMENT {
        int id PK
        int request_id FK
        int diet_plan_id FK
        int nutritionist_id FK
        string status
    }
    
    CHAT_MESSAGE {
        int id PK
        int assignment_id FK
        int sender_id FK
        string message
    }
```

---

## 3. Use Case Diagram

The Use Case diagram visualizes the primary interactions each system actor (User, Nutritionist, Admin) has with the application's features.

```mermaid
flowchart LR
    %% Actors
    Admin((Admin))
    User((User))
    Nutritionist((Nutritionist))

    %% User Cases
    subgraph System Actions
        UC1([Register & Manage Profile])
        UC2([Request Custom Diet])
        UC3([Get Calorie Predictions])
        UC4([Pay Subscription])
        
        NC1([Evaluate Diet Requests])
        NC2([Build / Assign Diet Plans])
        NC3([Chat via Assignment])
        
        AC1([Approve / Reject Users])
        AC2([Manage platform Subscriptions])
        AC3([View System Feedbacks & Payments])
    end

    %% Connections
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> NC3

    Nutritionist --> NC1
    Nutritionist --> NC2
    Nutritionist --> NC3

    Admin --> AC1
    Admin --> AC2
    Admin --> AC3
```

---

## 4. Class Diagram

The Class Diagram demonstrates the internal structure of the Python backend models (`models.py`) and their property distributions.

```mermaid
classDiagram
    class Login {
        +EmailField email
        +CharField password
        +CharField status
        +CharField usertype
    }

    class UserRegistration {
        +CharField name
        +BigIntegerField phone
        +IntegerField age
        +FloatField height
        +FloatField weight
        +CharField health_goal
        +ForeignKey loginid
    }

    class NutritionistRegistration {
        +CharField username
        +CharField qualification
        +CharField experience
        +ForeignKey loginid
    }

    class Dietplan {
        +CharField dietplan
        +CharField category
        +TextField breakfast
        +TextField lunch
        +TextField dinner
        +PositiveIntegerField calories
        +BooleanField is_custom
        +ForeignKey loginid
    }

    class DietRequest {
        +FloatField height
        +FloatField weight
        +CharField calculated_needs
        +CharField food_preference
        +CharField status
        +ForeignKey user
        +latest_assignment() property
    }

    class DietPlanAssignment {
        +CharField status
        +TextField comments
        +DateTimeField assigned_date
        +ForeignKey request
        +ForeignKey diet_plan
        +ForeignKey nutritionist
    }

    class ChatMessage {
        +TextField message
        +DateTimeField timestamp
        +ForeignKey assignment
        +ForeignKey sender
    }

    class Payment {
        +FloatField amount
        +CharField status
        +DateTimeField timestamp
        +ForeignKey assignment
        +ForeignKey user
    }

    Login "1" -- "1" UserRegistration
    Login "1" -- "1" NutritionistRegistration
    Login "1" -- "*" DietRequest
    Login "1" -- "*" Dietplan
    DietRequest "1" -- "*" DietPlanAssignment
    Dietplan "1" -- "*" DietPlanAssignment
    DietPlanAssignment "1" -- "*" ChatMessage
    DietPlanAssignment "1" -- "*" Payment
```
