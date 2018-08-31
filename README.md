# js_accompany: A accompanying platform
A platform to think the accompanying of animators at J&amp;S Liège


## Setup dev environment
1. Install Django and its dependencies (pip the requirements)
2. Do the migrations
    1. Create the dabatase `./manage.py migrate`
    2. Prepare migrations `./manage.py makemigrations animation`
    3. Prepare for reversion `./manage.py createinitialrevision`
    4. Make data-model migrations `./manage.py migrate`
    5. Make data migrations `./manage.py loaddata migrations/fixture.json`
      
