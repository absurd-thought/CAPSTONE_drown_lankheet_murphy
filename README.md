# And That Means Comfort: Optimizing Airbnb Listings
#### by Gretchyn Drown, Paul Lankheet, and Patrick Murphy

## About
This Capstone project for the University of Michigan’s Master of Applied Data Science program aims to help Airbnb hosts maximize their booking opportunities by optimizing home attributes, descriptive terms, and pricing for their property. You can see this project in action [here]().

_Data access statement:_ Data is public domain and may be obtained from [Inside Airbnb](http://insideairbnb.com/get-the-data/). It is used under a [Creative Commons](https://creativecommons.org/licenses/by/4.0/) license.

_License:_ Use and distribution of all elements herein subject to [MIT Licensing](https://choosealicense.com/licenses/mit/).

_Built with_ [AWS](https://aws.amazon.com/), [MySQL](https://www.mysql.com/), [Python](https://www.python.org/), and [streamlit.io](https://streamlit.io/).

## Getting started
* Ensure that you have the latest version of Python installed. Use the code below to install the libraries needed for this project:
```
pip install -r --upgrade requirements.txt
```
* You will need to have a MySQL database on AWS; follow [this tutorial](https://aws.amazon.com/getting-started/hands-on/create-mysql-db/).


## Connecting to your database
* Create a secretsfile.py file that contains your personal information for your AWS database and ensure that it is located in the same directory as your Jupyter notebook. Use the following code, replacing the strings with your actual information:
```
secrets = {}
secrets['DATABASE_ENDPOINT'] = 'my_aws_database_url'
secrets['DATABASE_USER'] = 'my_username'
secrets['DATABASE_PASSWORD'] = 'my_password'
secrets['DATABASE_PORT'] = 'my_port'
secrets['DATABASE_NAME'] = 'my_db_name'
```
Now you can run the .py file.

## Creating and hosting your streamlit.io app
* Download the folder <streamlit> from the repository.
* Open the command line and navigate to where you saved <streamlit.py>.
* Run the following command:
```
streamlit run streamlit.py
```
* To host your app on AWS, follow [this guide](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3), modifying as necessary.

## You’re good to go!
