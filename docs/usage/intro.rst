Introduction
############

It *should* be simple to use.
Once you have installed the Python module, few lines of code are needed to
onboard a Service:

.. code:: Python

   from onapsdk.vf import Vf
   from onapsdk.service import Service

   # We assume here that the VF has been already onboarded
   vf = VF(name="myVF")
   service = Service(name="myService", resources=[vf])
   service.onboard()
