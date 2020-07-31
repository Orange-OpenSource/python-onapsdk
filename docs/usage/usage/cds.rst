CDS
###

Load blueprint from file
------------------------

.. code:: Python

    from onapsdk.cds import Blueprint
    blueprint = Blueprint.load_from_file("<< path to CBA file >>")

Enrich blueprint
----------------

.. code:: Python

    enriched_blueprint = blueprint.enrich()

Publish blueprint
-----------------

.. code:: Python

    enriched_blueprint.publish()

Generate data dictionary from blueprint
---------------------------------------

.. code:: Python

    blueprint.get_data_dictionaries().save_to_file("<< path to dest file >>")

Load data dictionary set from file
----------------------------------

.. code:: Python

    from onapsdk.cds import DataDictionarySet
    dd_set = DataDictionarySet.load_from_file("<< path to dd file >>")

Upload data dictionary set
--------------------------

.. code:: Python
    
    dd_set.upload()
