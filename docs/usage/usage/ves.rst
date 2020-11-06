VES
###

Preparation for VES tests
-------------------------

To enable CDS Enrichment in an ONAP Frankfurt environment the NodePort 30449
for the CDS Blueprint Processor API service needs to be opened

#. Check existing VES Services:

   .. code-block:: sh

        kubectl get service -n onap|grep ves
        xdcae-ves-collector       NodePort       10.43.48.246    <none>     8443:30417/TCP

#. If the port of Ves Service is different than 30417 you can change it corresponding to the installation instruction.


Send event to Ves Collector
---------------------------

.. code:: Python

    from onapsdk.ves.ves import Ves
    response = Ves.send_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,
        version="v7"
    )

Send event batch to Ves Collector
-------------------------

.. code:: Python

    from onapsdk.ves.ves import Ves
    response = Ves.send_batch_event(
        basic_auth={'username': 'sample1', 'password': 'sample1'},
        json_event=event,
        version="v7"
    )
