# AI NOVEL WEBSITE : 
   This is a Novel website where users could read novels and create them also . It has a recommendation system and create novels using AI

## Features
 - User Authentication (JWT and google Oauth)
 - Story Creation using AI
 - free & premium tier
 - Streaming AI response
 - CORS
 - Webhook (for getting response from Payment Provider)

## Tech Stack
 **Backend**: Django,Django Rest Framework
 **AI**: Gemini API /
 **Frontend**: React 
 **Database**: PostgresSQL("For storing Novel data" & "more making LLM memory")
 **Deployment**: Render

## Installation
    git clone https://github.com/REE-TISH/Socin_Backend.git
    cd Socin_backend
    python -m venv venv
    venv\scripts\activate
    pip install -r ..\requirements.txt
## Run Locally
    (You must be in the same folder as manage.py file OR Follow the above steps properly and do this right away)
    python manage.py migrate
    python manage.py runserver
