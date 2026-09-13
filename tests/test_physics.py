"""
Tests for src/physics.py.

The key test here is deliberately NOT just "call the function and check it
doesn't crash" -- it checks the output against a case worked out by hand,
independently of the code. If you change the implementation later, this is
what tells you whether you broke the physics.

Hand-derived case:
Two muons, both with eta=0 (moving purely in the transverse plane), same pt,
travelling in exactly opposite directions (phi differs by pi). Then:

    px1 = pt,  py1 = 0,  pz1 = 0,  E1 = sqrt(pt^2 + m^2)
    px2 = -pt, py2 = 0,  pz2 = 0,  E2 = E1  (same pt and mass)

Sum: px = 0, py = 0, pz = 0, E = 2*E1
So invariant mass M = E = 2 * sqrt(pt^2 + m^2)

This is a closed-form result we can check the code against directly.
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.physics import invariant_mass, four_momentum, MUON_MASS_GEV


def test_invariant_mass_back_to_back_muons():
    pt = 20.0  # GeV, arbitrary but realistic for LHC muons
    m = MUON_MASS_GEV

    expected = 2 * math.sqrt(pt**2 + m**2)

    computed = invariant_mass(
        pt1=pt, eta1=0.0, phi1=0.0,
        pt2=pt, eta2=0.0, phi2=math.pi,
    )

    assert math.isclose(float(computed), expected, rel_tol=1e-9), (
        f"expected {expected}, got {computed}"
    )


def test_four_momentum_energy_momentum_relation():
    # For any single particle, E^2 - p^2 should equal mass^2 (basic
    # relativistic energy-momentum relation) -- a good sanity check that's
    # independent of the invariant_mass function itself.
    pt, eta, phi, mass = 15.0, 1.2, 0.7, MUON_MASS_GEV
    E, px, py, pz = four_momentum(pt, eta, phi, mass)
    m2_recovered = E**2 - (px**2 + py**2 + pz**2)
    assert math.isclose(m2_recovered, mass**2, abs_tol=1e-9)


def test_invariant_mass_is_symmetric():
    # Swapping particle 1 and particle 2 should give the same mass.
    a = invariant_mass(30.0, 0.5, 0.1, 25.0, -0.3, 2.0)
    b = invariant_mass(25.0, -0.3, 2.0, 30.0, 0.5, 0.1)
    assert math.isclose(float(a), float(b), rel_tol=1e-9)


if __name__ == "__main__":
    test_invariant_mass_back_to_back_muons()
    test_four_momentum_energy_momentum_relation()
    test_invariant_mass_is_symmetric()
    print("All tests passed.")
