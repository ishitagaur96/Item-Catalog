# Overview
Item Catalog application made with Flask

# Components
- Routing and Templating made with Flask
- Uses SQLAlchemy to communicate with the db
- RESTful API endpoints that return json files
- Uses Google Login to authenticate users
  - Any user:
     * can see all categories and items, and item details.
  - Registered users:
     * can create, update, and delete their own categories as well as items.

# How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd/vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run sudo pip install requests
7. Setup application database `python /item-catalog/database_setup.py`
8. *Insert fake data `python /item-catalog/database_init.py`
9. Run application using `python /item-catalog/application.py`
10. Access the application locally using http://localhost:8000

