CPS
###

Create dataspace
----------------

.. code:: Python

    from onapsdk.cps import Dataspace
    dataspace: Dataspace = Dataspace.create(dataspace_name="test_dataspace")


Create schema set
----------------

.. code:: Python

    from onapsdk.cps import Dataspace, SchemaSet
    dataspace: Dataspace = Dataspace(name="test_dataspace")
    with Path("schema_set_zip_file.zip").open("rb") as zip_file:
        schema_set: SchemaSet = dataspace.create_schema_set("test_schemaset", zip_file)


Create anchor
-------------

.. code:: Python

    from onapsdk.cps import Anchor, Dataspace, SchemaSet
    dataspace: Dataspace = Dataspace(name="test_dataspace")
    schema_set: SchemaSet = dataspace.get_schema_set("test_schemaset")
    anchor: Anchor = dataspace.create_anchor(schema_set, "test_anchor")
