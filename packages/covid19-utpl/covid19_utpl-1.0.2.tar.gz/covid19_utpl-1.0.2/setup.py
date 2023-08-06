# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['covid19_utpl', 'covid19_utpl.src']

package_data = \
{'': ['*'], 'covid19_utpl': ['data/*', 'img/*']}

setup_kwargs = {
    'name': 'covid19-utpl',
    'version': '1.0.2',
    'description': '',
    'long_description': '# Proyecto Final, Segundo Bimestre - PYTHON BÁSICO\n\n- **Vencimiento: Miércoles, 27 de julio**\n- **Calificación: .../10 (Auto califique su trabajo)**\n\n## Objetivos de aprendizaje\n- Aplicar nuevas habilidades a un problema del mundo real\n- Sintetizar las técnicas aprendidas\n\n## Herramientas\n- git\n- github\n- python\n- poetry\n- pandas\n- numpy\n- click\n- matplotlib\n\n\n## Organización de carpetas\n\nArchivos generados automáticamente por poetry\n\n```\ncovid19_utpl\n├── pyproject.toml              \n├── README.md                   # Documentación del proyecto    \n├── covid_19_utpl\n│    └── __init__.py\n│    └── main.py \n│    └── data\n│       └── vacunometro_cantones.csv\n│    └── img\n│        └── Vacunados_Canton.png\n│    └── src\n│       └── __init__.py\n│       └── conexion.py\n│       └── grafica.py\n│       └── listados.py\n│       └── vacunados.py\n```\n\n## Descripción\n\nCovid19_UTPL es una aplicacion desarrollada en Python que procesa informacion de la vacunacion del Ecuador, presentando informacion\ncomo seleccione el usuario ya sea por regiones, provincias o cantones, grafica cuantos han sido vacunados y las fechas que se ha desarrollado \nde las diversas dosis de vacunacion.\n\n\n## Versiones y evoluciones del producto\nVersión 1.0.1 Julio 2022\n- Creacion de menus\n- Obtencion de datos\n- Creacion de funciones\n\nVersión 1.0.2 Junio 2022\n- Guardado de graficas\n- Publicacion Pypi\n- Proyecto Final\n',
    'author': 'David Jimenez',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
