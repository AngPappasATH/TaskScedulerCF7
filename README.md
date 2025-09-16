# TaskScedulerCF7
This is my final project for CF7. It is a task scheduling application running server side. Using it you can create your own tasks and notes in order to keep track of your assignments.
Frameworkd used: Flask (Python), SQLite
 

-How to build the application:

1. Create a VM: ```python -m venv venv```
2. Activate ```venv\Scripts\Activate``` -> (venv) appears
3. Install Flask: ```pip install flask```
4. Run Server: ```python app.py```

-Deployment of the application
1) It is deployed via https://render.com/ as a webservice.
2) Render builds the app and installs prerequisites through the requirements.txt in main repository.
3) Render deploys the application at https://taskscedulercf7.onrender.com/


