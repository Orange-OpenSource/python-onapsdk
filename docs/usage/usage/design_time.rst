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

   from onapsdk.vendor import Vendor
   from onapsdk.vsp import Vsp

   # We assume here that the Vendor has been already onboarded
   vendor = Vendor(name="myVendor")
   vendor.onboard()
   vsp = Vsp(name="myVSP", vendor=vendor, package=open(PATH_TO_PACKAGE, 'rb'))
   vsp.onboard()

Onboard a VF
------------

.. code:: Python

   from onapsdk.vsp import Vsp
   from onapsdk.vf import Vf

   # We assume here that the VSP has been already onboarded
   vsp = Vsp(name="myVSP")
   vf = Vf(name="myVF", vsp=vsp)
   vf.onboard()

Onboard a Service
-----------------

.. code:: Python

   from onapsdk.vf import Vf
   from onapsdk.service import Service

   # We assume here that the VF has been already onboarded
   vf = Vf(name="myVF")
   service = Service(name="myService", resources=[vf])
   service.onboard()
