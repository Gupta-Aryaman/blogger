<p align="center">
  <img width="50%" src="https://i.ibb.co/xqqt2Cm/blogger.png">
</p>

## Overview
<b><i>blogger</i></b> is web application made using flask (a microweb framework) and
connected to a sqlite database using sqlalchemy as an ORM (Object Relational Model). The web app contains basic functionalities such as
signing up a user, logging in, seeing another user’s profile, seeing your own profile, editing your own profile,
adding posts, following/unfollowing other users, interaction with other user’s posts et cetera.

## Requirements

* `python` (Python 3.7 up to 3.10 supported)
* `pip` (Python package manager)

## Setup
Create a virtual environment to run the web app prevent any issues (optional):

1) Open the project folder and right click there and click open terminal
2) Create a virtual environment there by using this command -
  ```
  python3 -m venv my-project-env
  ```
3) Activate virutal environment by using this command(on ubnutu) -
  ```
  source my-project-env/bin/activate
  ```


Now you are in a virtual environment!


4) Install all the packages listed in requirements.txt using this command - 
  ```
  pip install -r requirements.txt
  ```
5) To run the program write this command in terminal - 
  ```
  python app.py
  ```
6) The url on which the app is running will be shown as - `Running on http://127.0.0.1:5000`
7) Copy the url and paste it in the browser, if you see the login page the flask app is running successfully

## ER Diagram
![image](https://user-images.githubusercontent.com/34962578/221681295-60d7b295-4e23-4e84-a4bf-6eea695dee10.png)
