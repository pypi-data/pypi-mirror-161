# BinTViewVariable

How to push the library to PYPI
Source: https://proglib.io/p/kak-opublikovat-svoyu-python-biblioteku-na-pypi-2020-01-28
1. Поменять версию библиотеки в setup.py
2. `python setup.py sdist` - Развёртываем пакет
3. `twine upload dist/*` - развёртываем пакет на PyPI
4. `pip install LibBinTViewVariable --upgrade`  - Обновляем наш пакет на стороне потребителя 