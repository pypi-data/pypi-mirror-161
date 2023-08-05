Paczka python której za bardzo nie da się zainstalować ani uruchomić. Służy do zajmowania nazw które
są zdefiniowane w ramach prywatnych repozytoriów Ampio w repozytorium PyPI. Ma to służyć
zabezpieczeniu przed atakom klasy _dependency injection_.

## Wykorzystanie

Nazwa wgrywanej paczki jest konfigurowalna.
```
PACKAGE_NAME=mypackage python setup.py sdist bdist_wheel
twine upload dist/*
```
