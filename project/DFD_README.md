# Data Flow Diagrams (DFD)

This document contains the Data Flow Diagrams (DFD) for the AegisAI System at different levels. You can view these diagrams by natively reading this file on GitHub, or by pasting the Mermaid code blocks below into any Mermaid-compatible viewer (such as [Mermaid Live Editor](https://mermaid.live/) or Notion).

## Level 0 DFD (Context Diagram)

```mermaid
graph LR
    %% Entities
    USER[USER]
    POLICE[POLICE]
    ADMIN[ADMIN]
    
    %% Process
    SYS((AEGISAI SYSTEM))

    %% Flows from Entities to System
    USER -- Request --> SYS
    POLICE -- Request --> SYS
    ADMIN -- Request --> SYS

    %% Flows from System to Entities
    SYS -- Response --> USER
    SYS -- Response --> POLICE
    SYS -- Response --> ADMIN
```

## Level 1 DFD - USER

```mermaid
graph LR
    %% Entity
    USER[USER]
    
    %% Processes
    LOGIN((LOGIN))
    SUBMIT_REPORT((SUBMIT CYBER<br/>CRIME REPORT))
    UPLOAD_FILE((UPLOAD<br/>EVIDENCE FILE))
    VIEW_STATUS((VIEW REPORT<br/>STATUS))
    SUBMIT_FEEDBACK((SUBMIT<br/>FEEDBACK))

    %% Data Stores
    AUTH_USER[(AUTH USER)]
    CC_REPORT[(CYBER CRIME<br/>REPORT)]
    FILEDATA[(FILEDATA)]
    FEEDBACK[(FEEDBACK)]

    %% Edges
    USER --> LOGIN
    
    LOGIN -- REQUEST --> AUTH_USER
    AUTH_USER -- RESPONSE --> LOGIN

    LOGIN --> SUBMIT_REPORT
    SUBMIT_REPORT -- REQUEST --> CC_REPORT
    CC_REPORT -- RESPONSE --> SUBMIT_REPORT

    LOGIN --> UPLOAD_FILE
    UPLOAD_FILE -- REQUEST --> FILEDATA
    FILEDATA -- RESPONSE --> UPLOAD_FILE

    LOGIN --> VIEW_STATUS
    VIEW_STATUS -- REQUEST --> CC_REPORT
    CC_REPORT -- RESPONSE --> VIEW_STATUS

    LOGIN --> SUBMIT_FEEDBACK
    SUBMIT_FEEDBACK -- REQUEST --> FEEDBACK
    FEEDBACK -- RESPONSE --> SUBMIT_FEEDBACK
```

## Level 1 DFD - POLICE

```mermaid
graph LR
    %% Entity
    POLICE[POLICE]
    
    %% Processes
    LOGIN((LOGIN))
    VIEW_COMPLAINTS((VIEW ASSIGNED<br/>COMPLAINTS))
    UPDATE_STATUS((UPDATE CASE<br/>STATUS))

    %% Data Stores
    POLICE_REGISTER[(POLICE<br/>REGISTER)]
    CC_REPORT[(CYBER CRIME<br/>REPORT)]

    %% Edges
    POLICE --> LOGIN
    
    LOGIN -- REQUEST --> POLICE_REGISTER
    POLICE_REGISTER -- RESPONSE --> LOGIN

    LOGIN --> VIEW_COMPLAINTS
    VIEW_COMPLAINTS -- REQUEST --> CC_REPORT
    CC_REPORT -- RESPONSE --> VIEW_COMPLAINTS

    LOGIN --> UPDATE_STATUS
    UPDATE_STATUS -- REQUEST --> CC_REPORT
    CC_REPORT -- RESPONSE --> UPDATE_STATUS
```

## Level 1 DFD - ADMIN

```mermaid
graph LR
    %% Entity
    ADMIN[ADMIN]

    %% Processes
    LOGIN((LOGIN))
    MANAGE_USERS((MANAGE USERS))
    VIEW_ANALYTICS((VIEW SYSTEM<br/>ANALYTICS))
    MONITOR_LOGS((MONITOR<br/>THREAT LOGS))

    %% Data Stores
    AUTH_USER[(AUTH USER)]
    AUTH_PERMISSION[(AUTH<br/>PERMISSION)]
    THREAT_LOG_1[(THREAT LOG)]
    THREAT_LOGS_2[(THREAT LOGS)]

    %% Edges
    ADMIN --> LOGIN
    
    LOGIN -- REQUEST --> AUTH_USER
    AUTH_USER -- RESPONSE --> LOGIN

    LOGIN --> MANAGE_USERS
    MANAGE_USERS -- REQUEST --> AUTH_PERMISSION
    AUTH_PERMISSION -- RESPONSE --> MANAGE_USERS

    LOGIN --> VIEW_ANALYTICS
    VIEW_ANALYTICS -- REQUEST --> THREAT_LOG_1
    THREAT_LOG_1 -- RESPONSE --> VIEW_ANALYTICS

    LOGIN --> MONITOR_LOGS
    MONITOR_LOGS -- REQUEST --> THREAT_LOGS_2
    THREAT_LOGS_2 -- RESPONSE --> MONITOR_LOGS
```
