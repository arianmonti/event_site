# Freevent
Freevent is a very small web application written in Flask. You can post and see parties, confrences and other kinds of event. Freevent does not use any Flask extension so it is so simple.

## Content

- [Dependencies](#dependencies)
    - [GNU-Linux](#gnu-linux)
 - [How to run](#run)




Dependencies
----
 Freevent dependecies:
|Language|Framework|Database|Datastore|
|-|-|-|-|
|Python|Flask|MySQL|Redis|

### GNU-Linux
- #### Python

    You can install Python from your package manager :
    
    ```bash
    sudo apt install python  ## Ubuntu, Debian, ...
    sudo dnf install python  ## Fedora
    sudo yum install python  ## RHEL, CentOS, ...
    sudo pacman -S python    ## Arch, Manjaro, ...
    ```
      
    Install packages from pip. Requirements listed in `requirements.txt`. But before install requirements, create and activate virtualenv.
    
    ```bash
    pip install virtualenv
    virtualenv venv # OR
    python -m virtualenv venv
    source venv/bin/activate
    ```
    and then install reuirements:
    ```bash
    pip install -r requirements.txt  # OR
    python -m pip install -r requirements.txt
    ```
    > Note: You can deactivate your virtualenv by running `deactivate` command.
    
    There is some problem with `mysqlclient` and you should install something like  `mysql-dev` to install it. Search and find the correct package.
 - #### MySQL
   Install from your package manager. You may find the correct package for your GNU/Linux distrobution by name `mysql` or `mariadb`. For example:
   ```bash
   sudo apt install mysql mysql-server     ## Ubuntu, Debian
   sudo dnf install mariadb mariadb-server ## Fedora
   ```
   Search and install the correct package and start it by running:
   ```bash
   sudo systemctl start mysql/mariadb
   ```
 - #### Redis
   Install from package manager and start Redis service.
   ```bash
   sudo [apt-dnf-yum-packman] [install / -S] redis &&
   sudo systemctl start redis
   ```
 
Run
---  
there is a `config.py.sample` in `app` directory. You should copy this file to `config.py` by running:
```bash
cp app/config.py.sample app/config.py
``` 
Edit `config.py` and write your information there.
Then create a user and database named that database you said in `config.py`
```SQL
ALTER USER 'USERNAME'@'host' IDENTIFIED BY 'PASSWORD';
CREATE DATABASE DATABASENAME;
```
and initialize the database by running
```bash
flask init-db ## OR
python -m flask init-db
```
and run this command to run flask.
```bash
flask run ## OR
python -m flask run
```
and check `127.0.0.1:5000/`. You can see Freevent. If you have an idea or find a bug, send a pull request. iff you like this application, Star!

