CDS
###

Preparation for CDS tests
-------------------------

To enable CDS Enrichment in an ONAP Frankfurt environment the NodePort 30449
for the CDS Blueprint Processor API service needs to be opened

#. Check existing CDS Services:

   .. code-block:: sh

      ubuntu@control01:~$ kubectl get service -n onap|grep cds-blueprints-processor-http
      cds-blueprints-processor-http      ClusterIP  10.43.101.198   <none>  8080/TCP

#. Change NodePort to CDS cds-blueprints-processor-http

   Add the "nodePort" under "ports" section
   and change "type" from "ClusterIP" to "NodePort"

   .. code-block:: sh

      ubuntu@control01:~$ kubectl edit service cds-blueprints-processor-http -n onap

      apiVersion: v1
      kind: Service
      metadata:
        creationTimestamp: "2020-07-23T02:57:36Z"
        labels:
          app: cds-blueprints-processor
          chart: cds-blueprints-processor-6.0.0
          heritage: Tiller
          release: onap
        name: cds-blueprints-processor-http
        namespace: onap
        resourceVersion: "10256"
        selfLink: /api/v1/namespaces/onap/services/cds-blueprints-processor-http
        uid: 6f065c03-4563-4d64-b6f5-a8892226c909
      spec:
        clusterIP: 10.43.101.198
        ports:
        - name: blueprints-processor-http
          nodePort: 30449	-> add line
          port: 8080
          protocol: TCP
          targetPort: 8080
        selector:
          app: cds-blueprints-processor
          release: onap
        sessionAffinity: None
        type: ClusterIP -> change to NodePort
      status:
        loadBalancer: {}

#. Verify NodePort to CDS cds-blueprints-processor-http

   .. code-block:: sh

      ubuntu@control01:~$ kubectl get service -n onap|grep cds-blueprints-processor-http
      cds-blueprints-processor-http      NodePort    10.43.101.198   <none> 8080:30449/TCP

#. Load ModelType via Bootstrap

   .. code-block:: sh

      curl --location --request POST 'http://<k8s-host>:30449/api/v1/blueprint-model/bootstrap' \
      --header 'Content-Type: application/json' \
      --header 'Authorization: Basic Y2NzZGthcHBzOmNjc2RrYXBwcw==' \
      --data-raw '{
      "loadModelType" : true,
      "loadResourceDictionary" : false,
      "loadCBA" : false
      }'


Load blueprint from file
------------------------

.. code:: Python

    from onapsdk.cds import Blueprint
    blueprint = Blueprint.load_from_file("<< path to CBA file >>")

Enrich blueprint and save
-------------------------

.. code:: Python

    enriched_blueprint = blueprint.enrich()
    enriched_blueprint.save("<< path to dest file >>")

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
