pipen# Robo Rally

Robo Rally game helper for remote play during pandemic times

## Submit Issues

Please submit issues via GitHub: https://github.com/mylollc/roborally/issues

## Installation (local)

1. Install Python 3.8+ from [http://python.org]()
2. Install _pipenv_ via `pip install pipenv`
3. From the _/src_ directory, run `pipenv install --dev`
4. Set the environment variables:
    * __FLASK_APP__ to "app.py"
    * __PYTHONPATH__ to the _/src__ directory under the repo location
5. From the _/src/ui_ directory, run `pipenv run flask run`
6. Open a browser and go to [http://localhost:5000]()

## Installation (Amazon EC2)

Setting up the EC2 key
```
You should have access to the Lastpass credential AWS Key - roborally - probably received an email
You can ssh to ec2-user@roborally.mylio-internal.com using that key
Ports 22 (ssh), 80, and 443 are open to public access

Got it, but I get this when trying to ssh:
scottwalker@scottsmacbookpro ~ % ssh ec2-user@roborally.mylio-internal.com
The authenticity of host 'roborally.mylio-internal.com (13.57.7.175)' can't be established.
ED25519 key fingerprint is SHA256:ahIISaopVvC78jASEI6ZmoGHsrpuuPXDRWVFV0mA5xs.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'roborally.mylio-internal.com' (ED25519) to the list of known hosts.

ec2-user@roborally.mylio-internal.com: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).

You'll need to use that key
Download the key to your machine then use ssh -i <PATH-TO-KEY> ec2-user@roborally.mylio-internal.com

Oh duh...but I don't see a key file in the lastpass entry..double duh, it's it's own entry. Clearly I need more :coffee:

Hah. No worries. +1 for more coffee
You'll probably want to create the file ~/.ssh/roborally and it should contain the contents of that entry

Yup, did that

Pro tip move - add this to your ~/.ssh/config
Host roborally
  Hostname roborally.mylio-internal.com
  User ec2-user
  IdentityFile ~/.ssh/roborally
Then you can just ssh roborally
```

Note: It is expected that the app will run under _~/git/roborally_ as the user _ec2-user_

1. Install and configure git
    1. `sudo yum install git`
    2. Create a new SSH key with `ssh-keygen -t ed25519`
    3. Go to the Github website and add this key for the repo
    4. Test it with `ssh -T git@github.com`
    5. Create and go into _~/git/roborally_
    6. Clone the repo with `git clone git@github.com:mylollc/roborally.git`


2. Configure the Roborally app
    1. `cd roborally`
    2. Install the Python packages: `pipenv install`
    3. Create this directory if it does not exist: _~/git/roborally/src/ui/static/images/avatars_


3. Set up NGINX:
    1. Install with `sudo amazon-linux-extras install nginx1`
    2. Copy _/resources/ec2/nginx.conf_ from the repo to _/etc/nginx_
    3. Run with `sudo systemctl start`
    4. `sudo systemctl enable nginx` to have it run on restart


4. Have Roborally run as a service:
    1. Copy _/resources/ec2/roborally.service_ to _/etc/systemd/system_
    2. Create a _www-data_ system group and add ec2-user - TBD, but you can look it up
    3. `sudo systemctl daeomon-reload`
    4. Run with `sudo systemctl start roborally.service`
    5. `sudo systemctl enable roborally` to have it run on restart

5. You should be able to access via _http://roborally.mylio-internal.com/_

## Development Environments
This assumes you already have Python installed and the prioper path variables updated.

### Pycharm Pro
1. Install Pycharm Pro. The commmunity edition does not have the flask or DB functionality that is needed.
2. Set the interpeter
3. Create a pipenv environment with this interpreter
4. Install the pipenv package file
5. Create a normal flask run config
6. Create a debug flask run config https://www.jetbrains.com/help/pycharm/run-debug-configuration-flask-server.html

### VS Code
1. Install VS Code
2. Install these extensions:
    * Python
    * Python Environment Manager
    * SQLite
3. Install `pipenv` with `pip install --user pipenv`
4. Create a pipenv environment via `pipenv --python <verion>` where <version> is like 3.X.
5. Install dependencies via `pipenv install --dev`
6. Go to _File > Preferences > Settings> then search for "venv path". Enter the path outputed from Step 4.
7. Edit __settings.json__ and add:
```
  "terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}/src",
  },
```
8. Install db