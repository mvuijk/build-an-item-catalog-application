
# **build-an-Item-Catalog-Application**
### **About this project**
In this project, we have build a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.

### **How to Run?**
#### PreRequisites:
  * [Python3](https://www.python.org/)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)
  * [Google+ ID](https://accounts.google.com/)

#### Setup Project:

Before we can start the application, there are several steps that we should take to make sure that everything  is downloaded in order to run the web application.

1. Install Vagrant and VirtualBox if you have not done so already. Instructions on how to do so can be found on the websites as well as in the Udacity [course materials](https://www.udacity.com/wiki/ud088/vagrant).
2. If you don't have a [Google+](https://accounts.google.com/) account than create one
3. Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
4. Launch the Vagrant VM (by typing vagrant up in the directory fullstack/vagrant from the terminal). You can find further instructions on how to do so [here](https://www.udacity.com/wiki/ud088/vagrant).
5. Clone [this repository](https://github.com/mvuijk/build-an-item-catalog-application.git) to your `/vagrant` folder.

Now that the VM is running and the nessacary application folder available we need to create the database first.

6. Run `databaseSetup.py` from the application folder.

```
    $ python3 databaseSetup.py
```

7. There is also a `loadData.py` file in the application folder. When you run this testdata will be loaded to the database. You can also start with an empty database.

```
    $ python3 loadData.py
```

Next step is to start the web application.

8. Run `catalogApp.py` to start the web application. The ouput should look like this:

```
    * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: 925-200-313
```

8. Open a browser an type the folowing URL [localhost:8000](http://localhost:8000/).