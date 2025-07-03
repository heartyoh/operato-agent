install:
	pip install pip-tools
	pip-sync requirements.txt

dev-install:
	pip install pip-tools
	pip-sync dev-requirements.txt

update:
	pip-compile requirements.in
	pip-compile dev-requirements.in 
