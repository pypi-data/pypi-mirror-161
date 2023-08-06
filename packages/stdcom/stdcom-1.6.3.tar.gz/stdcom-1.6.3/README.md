Name stdcom
===========

Files
-----

* stdcom.py
* stdcomq5.py
* frontendOPCUA.py
* frontend.py
* __init__.py
* ipportdialog.py
* pjaniceGeneric.py
* pjanice.py
* stdcomqt5treeewidget.py
* stdcomqt5widget.py
* stec-configure.py




Description
-----------
stdcom provides a connection to Stec, Multiverse that is running the NextStep plugin.  It allows python3 users the ability to act on and react to any action made on the Multiverse platorm.
It allows usees to Subscribe from Python 3 moudles and interact with Multiverse just as they were writing C++ plugins.

stdcomqt5  is a PyQt5 version  that can be used in the PyQt5 enviroment, and has all the multi threading precautions built into it.

Changes
-------
1.0.2 fixed \ accidently in main
1.0.3 changed the name of Multiverse to stdcomPyQt  
1.0.4 fix a bug created by documentation in the subscription Data() function
1.0.5 added a QTree widget so it can me attached to Multiverse stdcomqt5 class
1.4   OPC Server Added
1.5   pjanice Added
1.5.01 fixed a few bugs in stdcomqt5 for descriptipons, and added return back ability of our  new subscriptiopns.
pjanice and also now do static tags, what this means if for debugging, tags and descriptions can now be done with pjanice.
   
1.6.2 added GDR and postgres connection    

stdcom.py Example:
------------------

cBridge = None

if __name__ == "__main__":
    from time import sleep
    import sys
    if "--version" in sys.argv :
        print("0.0.1")
        sys.exit()



    def _AddNames(lnames):
        for i in range(0, len(lnames)):
            item = str(lnames[i])
            print(item)
        print("Press Enter to exit...")


    def _AddValues(sub):
        name = sub.Name()
        data = sub.Data()
        for each in data:
            print(">>>>>> ", data)
        print("Press Enter to exit...")


    # this could be argv but we will weld it for now
    XHOST = "192.168.199.7"  # we talk to ourself
    XPORT = int(4897)  # service port for NextStep plugin

    XSUBS = ["Scanner1.moisture", "Scannner1.basiswt"]
    s1 = [11110, 0, 10, 100]
\
    try:
        cBridge = stdcom(XHOST,
                        XPORT)  # start the ball rolling make the communication class if it fails we will die a death in lib
        cBridge.SetCallbacks(_AddValues, _AddNames)
        cBridge.NamesOn()  # tell the communication class to turn all the names so we can get every name across Multiverse
        cBridge.AddSubscriptions(XSUBS)  # add our subscriptions to multiverse

        for i in range(0, len(XSUBS)):
            cBridge.UpdateAsFloat(XSUBS[i], s1, 0)



    except:
        print("Check IP or Ensure NextStep Plugin is running")

    sleep(1)
    cBridge.terminate()


