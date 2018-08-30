# js_accompany: A accompanying platform
A platform to think the accompanying of animators at J&amp;S Liège


## Setup dev environment
1. Install Django 2.1
2. Do the migrations
    1. Create the dabatase `python manage.py migrate`
    2. Prepare migrations `python manage.py makemigrations animation`
    3. Make data-model migrations `python manage.py migrate`
    4. Make data migrations `./manage.py loaddata migrations/fixture.json`
      
