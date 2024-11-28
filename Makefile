runimg:
	@docker run --rm --name ppid -it -p 8080:8080 -v $$(pwd):/app/ --env-file dot-env-template ppid
buildimg:
	@docker build -t ppid	.
init:
	@./manage.py seeder
runlocal:
	@./manage.py runserver 0.0.0.0:8080
initconfig:
	@./manage.py runscript initconfig
initdev:
	@./manage.py runscript initdev
push:
	@git push origin main
clearpyc:
	@find . -name "*.pyc" -exec rm -f {} \;
