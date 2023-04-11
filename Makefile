DEST:=dest

venv: .venv/touchfile

.venv/touchfile: requirements-dev.txt
	test -d .venv || python3 -m venv .venv
	. .venv/bin/activate; pip3 install -Ur requirements-dev.txt
	touch .venv/touchfile

test: venv
	. .venv/bin/activate && \
	python3 -m pytest tests -vv

release: venv pre-release
	. .venv/bin/activate && \
	python3 scripts/release.py -u -d ${DEST} \
			service.subtitles.a4k \
			repository.ileodo-kodi-addons

publish: venv
	. .venv/bin/activate && \
	python3 scripts/publish.py \
			service.subtitles.a4k \
			repository.ileodo-kodi-addons

format: venv
	. .venv/bin/activate && \
	black . -l 88

pre-release: venv
	. .venv/bin/activate && \
	python3 -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]" && \
	python3 -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"

clean:
	rm -rf .venv
