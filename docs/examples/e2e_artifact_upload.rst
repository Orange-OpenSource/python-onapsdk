E2E Upload of an artifact
#####################################


.. code:: Python

    import os
    import logging

    from onapsdk.sdc.vsp import Vsp
    from onapsdk.sdc.vf import Vf
    from onapsdk.sdc.service import Service

    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    fh = logging.StreamHandler()
    fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)



    # Create required A&AI resources
    VF_NAME = "my_VF"
    SERVICENAME = "artifact_SERVICE"

    ARTIFACT_NAME = "clampnode"
    ARTIFACT_TYPE = "DCAE_INVENTORY_BLUEPRINT"
    ARTIFACT_FILE_PATH = "{os.path.dirname(os.path.abspath(__file__))}/my_ArtifactFile.yaml"


    logger.info("*******************************")
    logger.info("******** SERVICE DESIGN *******")
    logger.info("*******************************")

    logger.info("******** Get VF *******")
    Vf = vf(VF_NAME)
    vf.onboard()

    logger.info("******** Create Service *******")
    svc = Service(name=SERVICENAME)
    svc.create()
    svc.add_resource(vf)

    logger.info("******** Extract Artifact Data *******")
    data = open(ARTIFACT_FILE_PATH).read()

    logger.info("******** Upload Artifact *******")
    svc.add_artifact_to_vf(vnf_name=VF_NAME, 
                           artifact_type=ARTIFACT_TYPE,
                           artifact_name=ARTIFACT_NAME,
                           artifact=data)
    
    logger.info("******** Distribute Service *******")
    svc.checkin()
    svc.certify()
    svc.distribute()

