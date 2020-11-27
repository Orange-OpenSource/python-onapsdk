VES
###

Preparation for DMAAP tests
-------------------------

#. Check existing DMaap Services:

   .. code-block:: sh

        kubectl get service -n onap| grep mess
        message-router      NodePort        10.43.30.205        <none>      3905:31163/TCP,3904:32404/TCP

#. If the port of Ves Service is different than 3904 you can change it corresponding to the installation instruction.


Remove all events from DMaap
---------------------------

.. code:: Python

    from onapsdk.dmaap.dmaap import Dmaap
    response = Dmaap.reset_events()

Get all events from DMaap
-------------------------

.. code:: Python

    from onapsdk.dmaap.dmaap import Dmaap
    response = Dmaap.get_all_events()

Get events from specific topic from DMaap
-------------------------

.. code:: Python

    from onapsdk.dmaap.dmaap import Dmaap
    response = Dmaap.get_events_for_topic("fault")

Get all topics from DMaap
-------------------------

.. code:: Python

    from onapsdk.dmaap.dmaap import Dmaap
    response = Dmaap.get_all_topics()