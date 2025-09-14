# TaskScedulerCF7
This is my final project for CF7. It is a task scheduling application running server side. Using it you can create your own tasks and notes in order to keep track of your assignments.
Frameworkd used: Flask (Python), SQLite
 
SQLite – for the database (sqlite3 is in the standard library, and you’re using tasks.db).

gunicorn – a WSGI HTTP server for deploying the Flask app in production.

packaging – a utility library (not directly used in your code, but installed as a dependency, often for version handling).


-How to build the application:

1. Create a VM: ```python -m venv venv```
2. Activate ```venv\Scripts\Activate``` -> (venv) appears
3. Install Flask: ```pip install flask```
4. Run Server: ```python app.py```

-Deployment of the application
1) It is deployed via https://render.com/ as a webservice.
2) Render builds the app and installs prerequisites through the requirements.txt in main repository.
3) Render deploys the application at https://taskscedulercf7.onrender.com/


