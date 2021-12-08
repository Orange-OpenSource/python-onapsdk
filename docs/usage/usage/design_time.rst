Design time
###########

Onboard a Vendor
----------------

.. code:: Python

   from onapsdk.vendor import Vendor
   vendor = Vendor(name="myVendor")
   vendor.onboard()

Onboard a VSP
-------------

You will need the package of the VSP to onboard.

.. code:: Python

   from onapsdk.sdc.vendor import Vendor
   from onapsdk.sdc.vsp import Vsp

   # We assume here that the Vendor has been already onboarded
   vendor = Vendor(name="myVendor")
   vendor.onboard()
   vsp = Vsp(name="myVSP", vendor=vendor, package=open(PATH_TO_PACKAGE, 'rb'))
   vsp.onboard()

Create new VSP version
----------------------

You will need the package of the VSP to update.

.. code:: Python

   from onapsdk.sdc.vendor import Vendor
   from onapsdk.sdc.vsp import Vsp

   # We assume here that the Vendor has been already onboarded
   vsp = Vsp(name="myVSP")
   vsp.create_new_version()
   vsp.update_package(open(PATH_TO_PACKAGE, 'rb'))
   vsp.onboard()

Onboard a VF
------------

.. code:: Python

   from onapsdk.sdc.vsp import Vsp
   from onapsdk.sdc.vf import Vf

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")
   vf = Vf(name="myVF", vsp=vsp)
   vf.onboard()

Onboard a VF with properties assignement
----------------------------------------

.. code:: Python

   from onapsdk.sdc.properties import Property
   from onapsdk.sdc.vsp import Vsp
   from onapsdk.sdc.vf import Vf

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")
   property_1 = Property(
      name="prop1",
      property_type="string",
      value="test"
   )
   property_2 = Property(
      name="prop2",
      property_type="integer"
   )
   vf = Vf(name="myVF",
           vsp=vsp,
           properties=[
              property_1,
              property_2
           ],
           inputs=[property_1])
   vf.onboard()

Onboard a VF with Deployment Artifact
-------------------------------------

.. code:: Python

   from onapsdk.sdc.properties import Property
   from onapsdk.sdc.vsp import Vsp
   from onapsdk.sdc.vf import Vf

   logger.info("******** Onboard Vendor *******")
   vendor = Vendor(name="my_Vendor")
   vendor.onboard()

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")

   logger.info("******** Onboard VF *******")
   vf = Vf(name="myVF")
   vf.vsp = vsp
   vf.create()

   logger.info("******** Upload Artifact *******")
   vf.add_deployment_artifact(artifact_type="CONTROLLER_BLUEPRINT_ARCHIVE",
                              artifact_name="CBA.zip",
                              artifact_label="vfwcds",
                              artifact="dir/CBA_enriched.zip")

   vf.onboard()

Onboard a VF with it's component's property input
-------------------------------------------------

.. code:: Python

   from onapsdk.sdc.properties import ComponentProperty
   from onapsdk.sdc.vsp import Vsp
   from onapsdk.sdc.vf import Vf
   from onapsdk.sdc.vfc import Vfc

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")

   vfc = Vfc(name="AllottedResource")

   logger.info("******** Onboard VF *******")
   vf = Vf(name="myVF")
   vf.vsp = vsp
   vf.create()
   vf.add_resource(vfc)
   vfc_comp = vf.get_component(vfc)
   comp_prop = vfc_comp.get_property("min_instances")
   comp_prop.value = "test"
   vf.declare_input(comp_prop)

   vf.onboard()

Onboard a PNF with VSP
----------------------
.. code:: Python

   from onapsdk.sdc.pnf import Pnf
   from onapsdk.sdc.vendor import Vendor

   logger.info("******** Onboard Vendor *******")
   vendor = Vendor(name="my_Vendor")
   vendor.onboard()

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")

   logger.info("******** Onboard PNF *******")
   pnf = PNF(name="myPNF")
   pnf.vsp = vsp
   pnf.onboard()

Onboard a PNF with Deployment Artifact (without VSP)
----------------------------------------------------
.. code:: Python

   from onapsdk.sdc.vendor import Vendor
   from onapsdk.sdc.pnf import Pnf

   logger.info("******** Onboard Vendor *******")
   vendor = Vendor(name="my_Vendor")
   vendor.onboard()

   logger.info("******** Onboard PNF *******")
   pnf = Pnf(name=PNF, vendor=vendor)
   pnf.create()

   logger.info("******** Upload Artifact *******")
   pnf.add_deployment_artifact(artifact_type=ARTIFACT_TYPE,
                               artifact_name=ARTIFACT_NAME,
                               artifact_label=ARTIFACT_LABEL,
                               artifact=ARTIFACT_FILE_PATH)
   pnf.onboard()

Onboard a Service
-----------------

.. code:: Python

   from onapsdk.sdc.vf import Vf
   from onapsdk.sdc.service import Service

   # We assume here that the VF has been already onboarded
   vf = Vf(name="myVF")
   service = Service(name="myService", resources=[vf])
   service.onboard()

Onboard a Service with properties assignement
---------------------------------------------

.. code:: Python

   from onapsdk.sdc.properties import Property
   from onapsdk.sdc.vf import Vf
   from onapsdk.sdc.service import Service

   # We assume here that the VF has been already onboarded
   vf = Vf(name="myVF")
   property_1 = Property(
      name="prop1",
      property_type="string",
      value="test"
   )
   property_2 = Property(
      name="prop2",
      property_type="integer",
      declare_input=True
   )
   service = Service(name="myService",
                     resources=[vf],
                     properties=[
                        property_1,
                        property_2
                     ],
                     inputs=[property_1])
   service.onboard()

Onboard a Service with Nested inputs
------------------------------------

.. code:: Python

   from onapsdk.sdc.properties import NestedInput
   from onapsdk.sdc.vf import Vf
   from onapsdk.sdc.service import Service

   # We assume here that the VF has been already onboarded
   vf = Vf(name="myVF")
   inp = vf.get_input("input_name_we_want_to_declare_in_service")
   service = Service(name="myService",
                     resources=[vf],
                     inputs=[NestedInput(vf, inp)])
   service.onboard()

Onboard a Service with VL
-------------------------

.. code:: Python

   from onapsdk.sdc.vl import VL
   from onapsdk.sdc.service import Service

   # No VF needed, but you need to be sure that Vl with given
   # name exists in SDC
   vl = Vl(name="Generic NeutronNet")
   service = Service(name="myServiceWithVl", resources=[vl])
   service.onboard()

Onboard a Service with custom category
--------------------------------------

.. code:: Python

   from onapsdk.sdc.category_management import ServiceCategory
   from onapsdk.sdc.vf import Vf
   from onapsdk.sdc.service import Service

   # Let's create a custom category
   CATEGORY_NAME = "Python ONAP SDK category"
   ServiceCategory.create(name=CATEGORY_NAME)

   # We assume here that the VF has been already onboarded
   # Create a service with category we created few lines above
   vf = Vf(name="myVF")
   service = Service(name="myService", resources=[vf], category=CATEGORY_NAME)
   service.onboard()

Onboard an Artifact for an embedded VF
--------------------------------------

All SDC artifact types are supported

.. code:: Python

   from onapsdk.service import Service

   # We assume here that the Service has been already onboarded
   # with a Vnf
   service = Service(name="myService")
   # We load artifact data
   data = open("{}/myArtifact.yaml".format(os.path.dirname(os.path.abspath(__file__))), 'rb').read()
   # We add the artifact to the service Vnf
   #
   svc.add_artifact_to_vf(vnf_name="myVnf",
                          artifact_type="DCAE_INVENTORY_BLUEPRINT",
                          artifact_name="myArtifact.yaml",
                          artifact=data)

Onboard a Service with Deployment Artifact
------------------------------------------

.. code:: Python

   from onapsdk.sdc.service import Service

   svc = Service(name="myService")

   logger.info("******** Upload Artifact *******")
   svc.add_deployment_artifact(artifact_type="OTHER",
                              artifact_name="eMBB.zip",
                              artifact_label="embbcn",
                              artifact="dir/eMBB.zip")

   svc.onboard()

Onboard a Service with a CBA blueprint for Macro Instantiation
--------------------------------------------------------------

.. code:: Python

   from onapsdk.sdc.service import Service, ServiceInstantiationType

   # Set CBA variables and artifact level
   # Must match to values in the CBA TOSCA.meta file
   SDNC_TEMPLATE_NAME = "vFW-CDS"
   SDNC_TEMPLATE_VERSION = "1.0.0"
   SDNC_ARTIFACT_NAME = "vnf"

   svc = Service(name="myService",
                 instantiation_type=ServiceInstantiationType.MACRO)

   svc.create()

   logger.info("*** add a VF, which includes a CBA blueprint ***")
   svc.add_resource(vf)

   logger.info("******** Set SDNC properties for VF ********")
   component = svc.get_component(vf)
   prop = component.get_property("sdnc_model_version")
   prop.value = SDNC_TEMPLATE_NAME
   prop = component.get_property("sdnc_artifact_name")
   prop.value = SDNC_ARTIFACT_NAME
   prop = component.get_property("sdnc_model_name")
   prop.value = SDNC_TEMPLATE_NAME
   prop = component.get_property("controller_actor")
   prop.value = "CDS"
   prop = component.get_property("skip_post_instantiation_configuration")
   prop.value = False

   logger.info("******** Onboard Service *******")
   svc.checkin()
   svc.onboard()
