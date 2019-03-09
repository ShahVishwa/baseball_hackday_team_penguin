# commands to activate python3 virtual environment and setup flask debugging environment
INVENV = . env/bin/activate ; export FLASK_DEBUG=1 ;

# run the flask server
run: install
	#($(INVENV) python3 -m smtpd -n -c DebuggingServer localhost:1029)
	($(INVENV) python3 src/application.py)&

# install the site's flask based server
install:
	python3 -m venv env
	$(INVENV) pip3 install -r requirements.txt

# updates the reqirements
dist:	env
	$(INVENV) pip freeze > requirements.txt

# removes compiled and installed code
clean:
	rm -f *.pyc */*.pyc
	rm -rf __pycache__ */__pycache__
	rm -rf env
	rm -rf .DS_Store
	rm -rf src/.DS_Store
