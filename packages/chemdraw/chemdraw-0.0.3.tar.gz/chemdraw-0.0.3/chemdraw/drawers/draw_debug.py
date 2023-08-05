
import plotly.graph_objs as go

from chemdraw.objects.bonds import Bond
from chemdraw.objects.atoms import Atom
from chemdraw.objects.molecule import Molecule


class ConfigDrawerDebug:
    def __init__(self, parent):
        self.parent = parent

        self._debug = False
        self.show_center_point = False
        self.show_molecule_vector = False
        self.show_bond_vector = False
        self.show_bond_perpendicular = False
        self.show_atom_vector = False

    def __repr__(self):
        return f"show: {self.debug}"

    @property
    def debug(self) -> bool:
        """ Turn on all debugging."""
        return self._debug

    @debug.setter
    def debug(self, option: bool):
        self._debug = option
        self.show_center_point = option
        self.show_molecule_vector = option
        self.show_bond_vector = option
        self.show_bond_perpendicular = option
        self.show_atom_vector = option


def draw_debug(fig: go.Figure, config: ConfigDrawerDebug, molecule: Molecule, atoms: list[Atom], bonds: list[Bond]) \
        -> go.Figure:
    if config.show_center_point:
        fig.add_trace(go.Scatter(x=[molecule.coordinates[0]], y=[molecule.coordinates[1]],
                                 mode="markers", marker=dict(color="orange", size=15)))
    if config.show_molecule_vector:
        fig.add_annotation(
            x=molecule.coordinates[0] + molecule.vector[0]*1.5,
            y=molecule.coordinates[1] + molecule.vector[1]*1.5,
            ax=molecule.coordinates[0],
            ay=molecule.coordinates[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=2,
            arrowwidth=2,
            arrowcolor="orange",
            width=2
        )
    if config.show_bond_vector:
        fig = _add_bond_vectors(fig, bonds)
    if config.show_bond_perpendicular:
        fig = _add_bond_perpendicular(fig, bonds)
    if config.show_atom_vector:
        fig = _add_atom_vector(fig, atoms)

    return fig


def _add_bond_vectors(fig: go.Figure, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        fig.add_annotation(
            x=bond.center[0] + bond.vector[0],
            y=bond.center[1] + bond.vector[1],
            ax=bond.center[0],
            ay=bond.center[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="green"
        )

    return fig


def _add_bond_perpendicular(fig: go.Figure, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        fig.add_annotation(
            x=bond.center[0] + bond.perpendicular[0],
            y=bond.center[1] + bond.perpendicular[1],
            ax=bond.center[0],
            ay=bond.center[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="blue"
        )

    return fig


def _add_atom_vector(fig: go.Figure, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        fig.add_annotation(
            x=atom.coordinates[0] + atom.vector[0],
            y=atom.coordinates[1] + atom.vector[1],
            ax=atom.coordinates[0],
            ay=atom.coordinates[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="red"
        )

    return fig
