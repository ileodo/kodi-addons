venv: .venv/touchfile

.venv/touchfile: requirements-dev.txt
	test -d .venv || python3 -m venv .venv
	. .venv/bin/activate; pip3 install -Ur requirements-dev.txt
	touch .venv/touchfile

test: venv
	source .venv/bin/activate && \
	python3 -m pytest tests

release: venv
	source .venv/bin/activate && \
    python3 release.py -u -d dest \
    	service.subtitles.a4k \
    	repository.ileodo-kodi-addons

publish: venv
	source .venv/bin/activate && \
	python3 publish.py \
		service.subtitles.a4k \
		repository.ileodo-kodi-addons

clean:
	rm -rf .venv