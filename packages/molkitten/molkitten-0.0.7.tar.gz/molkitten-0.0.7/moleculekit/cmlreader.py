# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from xml import sax
from moleculekit.molecule import Molecule
from moleculekit.readers import Topology, Trajectory


bondtypemap = {"S": "1", "D": "2", "T": "3"}


class CMLHandler(sax.ContentHandler):
    """Handle definition of CML file content."""

    def __init__(self):
        self.topo = None
        self.traj = None
        self.curelement = ""
        self.topologies = []

    def startElement(self, name, attributes):
        """Start XML element parsing"""
        if name == "cml:molecule":
            self.topo = Topology()
            self.traj = Trajectory()
        elif name == "cml:atom":
            self.topo.element.append(attributes["elementType"])
            self.topo.id.append(attributes["id"])
            if "formalCharge" in attributes:
                self.topo.formalcharge.append(attributes["formalCharge"])
            if "atomType" in attributes:
                self.topo.atomtype.append(attributes["atomType"])
            if "x2" in attributes:
                self.traj.coords.append([attributes["x2"], attributes["y2"], 0])
            if "x3" in attributes:
                self.traj.coords.append(
                    [attributes["x3"], attributes["y3"], attributes["z3"]]
                )
        elif name == "cml:bond":
            self.topo.bonds.append(attributes["atomRefs2"].split())
            self.topo.bondtype.append(bondtypemap[attributes["order"]])
        else:
            self.curelement = name

    def endElement(self, name):
        """End XML element parsing"""
        if name == "cml:molecule":
            self.topologies.append(self.topo)
        else:
            self.curelement = ""

    def characters(self, text):
        """Parse text data in XML"""
        if text.isspace():
            return


sax.make_parser()
handler = CMLHandler()
with open("test.cml") as f:
    sax.parseString(f.read(), handler)
