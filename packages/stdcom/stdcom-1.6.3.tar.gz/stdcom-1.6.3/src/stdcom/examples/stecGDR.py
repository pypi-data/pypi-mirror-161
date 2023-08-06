
from gdrGeneric import *
from pjaniceGeneric import *



if __name__ == "__main__":
    """
    bumped version
    """

    my_parser = argparse.ArgumentParser( description="Version 1.6.2 Stec Pjanice Python Version")
    # Add the arguments
    my_parser.add_argument('-p','--project', metavar='project', required=False)


    args = my_parser.parse_args()
    nextProject = args.project

    app = QApplication(sys.argv)
    if nextProject is not None :
        window = gdrGeneric(None,nextProject)
    else:
        window = gdrGeneric()

    window.setWindowTitle("Stec PJanice Viewer")

    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    if window.widgetPjanice.cBridge != None:
        window.widgetPjanice.cBridge.terminate()
