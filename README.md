# Kanban

<h3>Usage</h3>

1)Download all the files.

2)Open the folder in VsCode.

3)Install the requirements using:

      pip install -r requirements.txt
      

4)Install MailHog from <a href="https://www.lullabot.com/articles/installing-mailhog-for-ubuntu#:~:text=Let's%20create%20a%20service%20file%20for%20MailHog%20and%20then%20register%20it.&text=Start%20the%20service%20to%20verify,the%20MailHog%20service%20is%20running.">here</a>.

5)Install Redis from <a href="https://redis.io/docs/getting-started/installation/install-redis-on-linux/">here</a>.

6)Install node using:
      sudo apt-install Node.js
      sudo apt-install npm

6)Run the commands in different terminals the following order:
 
       ~/go/bin/MailHog
      redis-server
      python3 main.py
      celery -A main.celery beat --loglevel=info
      celery -A main.celery worker --loglevel=info
      
7)To run the front-end, use the following commands:

      cd frontend
      npm run dev
      
8)The website can now be accessed using http://localhost:5750/
