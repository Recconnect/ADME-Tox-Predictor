.PHONY: deploy update restart logs

deploy:
	git pull origin master
	./venv/bin/pip install -r requirements.txt
	sudo systemctl daemon-reload
	sudo systemctl restart admetox-api admetox-ui
	sudo nginx -s reload

update:
	git pull origin master
	./venv/bin/pip install -r requirements.txt
	./venv/bin/python run_train.py
	sudo systemctl restart admetox-api admetox-ui

restart:
	sudo systemctl restart admetox-api admetox-ui

logs:
	journalctl -u admetox-api -f -n 50
