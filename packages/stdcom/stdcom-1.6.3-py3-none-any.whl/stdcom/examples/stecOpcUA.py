from frontendOPCUA import *

if __name__ == "__main__":
    """
    bumped version
    """
    if "--version" in sys.argv:
        print("1.2.3")
        sys.exit()

    show = True
    nextProject = False
    project = None

    app = QApplication(sys.argv)

    window = StecMultiverseOPCUA(project)
    window.setWindowTitle("Stec OPCUA Server")

    if '--hide' in sys.argv:
        print("Hidden Display")
        window.hide()
    else:
        window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    window.Terminate()

