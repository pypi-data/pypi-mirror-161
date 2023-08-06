# -*- coding: utf-8 -*-

"""Non-graphical part of the Crystal Builder step in a SEAMM flowchart
"""

try:
    import importlib.metadata as implib
except Exception:
    import importlib_metadata as implib
import io
import logging
import pprint

import CifFile

import crystal_builder_step
import molsystem
import seamm
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: 'job' and 'printer'. 'job' send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# 'printer' sends output to the file 'step.out' in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Crystal Builder")


class CrystalBuilder(seamm.Node):
    """
    The non-graphical part of a Crystal Builder step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : CrystalBuilderParameters
        The control parameters for Crystal Builder.

    See Also
    --------
    TkCrystalBuilder,
    CrystalBuilder, CrystalBuilderParameters
    """

    def __init__(self, flowchart=None, title="Crystal Builder", extension=None):
        """A step for Crystal Builder in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
            flowchart: seamm.Flowchart
                The non-graphical flowchart that contains this step.

            title: str
                The name displayed in the flowchart.
            extension: None
                Not yet implemented
        """
        logger.debug("Creating Crystal Builder {}".format(self))

        super().__init__(
            flowchart=flowchart,
            title="Crystal Builder",
            extension=extension,
            logger=logger,
        )  # yapf: disable

        self.parameters = crystal_builder_step.CrystalBuilderParameters()

    @property
    def version(self):
        """The semantic version of this module."""
        return crystal_builder_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return crystal_builder_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
            P: dict
                An optional dictionary of the current values of the control
                parameters.
        Returns
        -------
            description : str
                A description of the current step.
        """
        if not P:
            P = self.parameters.values_to_dict()

        aflow_prototype = P["AFLOW prototype"]
        data = crystal_builder_step.prototype_data[aflow_prototype]

        cell = data["cell"]
        sites = data["sites"]
        is_common = False
        for prototype, aflow in crystal_builder_step.common_prototypes.items():
            if aflow == aflow_prototype:
                is_common = True
                break

        if is_common:
            text = "Building a {prototype} system"
        elif data["strukturbericht"] is not None:
            text = (
                "Building a system with the Struktubericht designation: "
                f"{data['strukturbericht']}"
            )
        else:
            text = f"Building a system with the AFLOW prototype {aflow_prototype}"

        text += "\n"

        text += f"\n            exemplar structure: {data['prototype']}"
        text += f"\n                         notes: {data['description']}"
        text += f"\n                Pearson symbol: {data['pearson_symbol']}"
        if data["strukturbericht"] is not None:
            text += f"\n   Strukturbericht designation: {data['strukturbericht']}"
        text += f"\n               number of atoms: {data['n_atoms']}"
        text += f"\n               AFLOW prototype: {aflow_prototype}"
        text += "\n"

        label = "cell"
        for name, param0 in cell:
            value = P[name]
            text += f"\n                    {label:4} {name:>5}: {value}"
            label = " "

        text += "\n"

        label = "sites"
        coordinates = self.parameters["coordinates"].get()
        elements = self.parameters["elements"].get()
        for site_data, symbol, xyz in zip(sites, elements, coordinates):
            site, mult, symbol0, x0, unfix_x, y0, unfix_y, z0, unfix_z = site_data
            x, y, z = xyz
            site = f"{mult}{site}"
            x = x[0:6] + ("*" if unfix_x else " ")
            y = y[0:6] + ("*" if unfix_y else " ")
            z = z[0:6] + ("*" if unfix_z else " ")

            text += (
                f"\n                   {label:6} {site:>4}: {symbol:2s} {x:6s} {y:6s} "
                f"{z:6s}"
            )
            label = " "

        return self.header + "\n" + __(text, **P, indent=4 * " ").__str__()

    def run(self):
        """Run a Crystal Builder step.

        Returns
        -------

        next_node : seamm.Node
            The next node object in the flowchart.

        """

        next_node = super().run(printer)

        # Get the system
        system, configuration = self.get_system_configuration(None)

        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )
        self.logger.debug(f"Dereferenced values:\n{pprint.pformat(P)}")

        # Print what we are doing -- getting formatted values for printing
        PP = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data, formatted=True, units=False
        )
        self.logger.debug(f"Formatted values:\n{pprint.pformat(PP)}")
        printer.important(__(self.description_text(PP), indent=self.indent))

        # Create the configuration from the cif file for the prototype
        aflow_prototype = P["AFLOW prototype"]

        package = self.__module__.split(".")[0]
        files = [p for p in implib.files(package) if aflow_prototype in str(p)]
        if len(files) == 0:
            raise RuntimeError(f"Could not find prototype '{aflow_prototype}'!")
        path = files[0]
        data = path.read_text()

        data = self.fix_coordinates(data, P["coordinates"])

        configuration.from_cif_text(data)

        # Now set the cell parameters. If unmentioned the lattice parameters
        # get the previous value, e.g. a, a, c. The angles are those of the
        # prototype if not mentioned.
        a0, b0, c0, alpha0, beta0, gamma0 = configuration.cell.parameters

        data = crystal_builder_step.prototype_data[aflow_prototype]
        cell = data["cell"]
        sites = data["sites"]

        tmp = {
            "a": None,
            "b": None,
            "c": None,
            "alpha": alpha0,
            "beta": beta0,
            "gamma": gamma0,
        }
        tmp0 = {**tmp}
        i = 0
        for name, param0 in cell:
            tmp0[name] = param0
            i += 1
            if name in ("a", "b", "c"):
                tmp[name] = P[name].to("Å").magnitude
            else:
                tmp[name] = P[name].to("degree")
            # Fill in any that were skipped ...
        last = None
        new_cell = []
        for name, param in tmp.items():
            if param is not None:
                last = param
            new_cell.append(last)

        self.logger.debug(f"cell = {new_cell}")
        configuration.cell.parameters = new_cell

        # And the elements for the sites. Note that symmetry has been lowered
        # to P1
        symbols = []
        for site_data, symbol in zip(sites, P["elements"]):
            site, mult = site_data[0:2]
            if self.is_expr(symbol):
                symbol = self.get_variable(symbol)
            symbols.extend([symbol] * mult)
        self.logger.debug(f"symbols = {symbols}")
        atnos = molsystem.elements.to_atnos(symbols)
        column = configuration.atoms.get_column("atno")
        column[0:] = atnos

        # Find the symmetry and set to the conventional cell. Maybe atoms have
        # changed? Seems safe...
        configuration.symmetrize(symprec=0.0001)

        # Requested citations for the AFLOW protoype library
        self.references.cite(
            raw=self._bibliography["MEHL2017S1"],
            alias="MEHL2017S1",
            module="crystal_builder_step",
            level=1,
            note="Citation for the AFLOW library of prototype, part 1.",
        )
        self.references.cite(
            raw=self._bibliography["HICKS2019S1"],
            alias="HICKS2019S1",
            module="crystal_builder_step",
            level=1,
            note="Citation for the AFLOW library of prototype, part 2.",
        )

        # And citation for the structure itself:
        self.references.cite(
            raw=self._bibliography[aflow_prototype],
            alias=aflow_prototype,
            module="crystal_builder_step",
            level=1,
            note="Citation for the crystal strcuture of the prototype",
        )

        return next_node

    def fix_coordinates(self, text, coordinates):
        """Change the coordinates in the CIF file."""

        cif = CifFile.ReadCif(io.StringIO(text))

        data_blocks = [*cif.keys()]
        data_block = cif[data_blocks[0]]

        xs = []
        ys = []
        zs = []
        for tmp in coordinates:
            x, y, z = tmp
            xs.append(float(x))
            ys.append(float(y))
            zs.append(float(z))

        data_block["_atom_site_fract_x"] = xs
        data_block["_atom_site_fract_y"] = ys
        data_block["_atom_site_fract_z"] = zs

        return cif.WriteOut()
