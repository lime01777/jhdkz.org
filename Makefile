PY=python

test:
	$(PY) manage.py test

urls:
	$(PY) manage.py show_urls | cat

route-audit:
	$(PY) manage.py route_audit || exit 1

import-redirects:
	$(PY) manage.py import_redirects $(FILE)


