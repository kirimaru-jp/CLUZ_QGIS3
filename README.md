# CLUZ
CLUZ plugin for QGIS v3

CLUZ (Conservation Land-Use Zoning software) is a QGIS plug-in that allows users to design protected area networks
and other conservation landscapes and seascapes. It can be used for on-screen planning and also acts as a link for
the Marxan conservation planning software. It was developed by Bob Smith, from the Durrell Institute of Conservation
and Ecology (DICE), and funded by the UK Government's Darwin Initiative.

More details about CLUZ are available here http://anotherbobsmith.wordpress.com/software/cluz/


-----------------------------------------------------------

UPDATE: this update allow Marxan to be installed on any drive (not necessarily C, on Windows).

Briefly, we just need to switch to the drive where Marxan is installed before running Marxan, by executing:
batWriter.writerow([ os.path.splitdrive(marxanFullName)[0] ])
in the function "makeMarxanBatFile" of the file "cluz_functions5.py".

