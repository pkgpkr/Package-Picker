# Architecture

## Diagrams

![Pipeline Tests](./img/diagram.png)

## Interface definition

### Query engine

```eval_rst
month_calculation
----------------------
.. automodule:: scraper.month_calculation
   :members:
   :undoc-members:

github
----------------------
 .. automodule:: scraper.github
    :members:
    :undoc-members:

npm
----------------------
 .. automodule:: scraper.npm
    :members:
    :undoc-members:

psql
----------------------
 .. automodule:: scraper.psql
    :members:
    :undoc-members:

pypi
----------------------
 .. automodule:: scraper.pypi
    :members:
    :undoc-members:
```

### Recommender model

```eval_rst
database
----------------------
 .. automodule:: model.database
    :members:
    :undoc-members:
```

### Web service

```eval_rst

webservice.views
-------------------------------
.. automodule:: webservice.views
   :members:
   :undoc-members:



webservice.recommender_service
-------------------------------

.. automodule:: webservice.recommender_service
   :members:
   :undoc-members:


webservice.github_util
-------------------------------

 .. automodule:: webservice.github_util
    :members:
    :undoc-members:
```
