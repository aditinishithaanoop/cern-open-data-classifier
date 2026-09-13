"""
Core physics utilities.

The one idea everything else in this project builds on: given two particles'
kinematics (transverse momentum, pseudorapidity, azimuthal angle), compute the
invariant mass of the two-particle system. This is the quantity that shows
resonance peaks (J/psi, Upsilon, Z boson, Higgs, ...) as bumps in a histogram
-- it's the single most useful number in a lot of collider physics analyses.

Background, briefly:
- pt   (transverse momentum): momentum component perpendicular to the beam line.
- eta  (pseudorapidity): encodes the angle to the beam line. eta=0 is
  perpendicular to the beam; large |eta| means close to the beam direction.
- phi  (azimuthal angle): angle around the beam line, in radians.

From (pt, eta, phi, mass) we reconstruct the full 4-momentum (E, px, py, pz),
then invariant mass of a two-particle system is:

    M = sqrt( (E1+E2)^2 - (px1+px2)^2 - (py1+py2)^2 - (pz1+pz2)^2 )

(using natural units where c = 1, energies/momenta in GeV).
"""

import numpy as np

MUON_MASS_GEV = 0.1057  # rest mass of a muon, in GeV/c^2
ELECTRON_MASS_GEV = 0.000511


def four_momentum(pt, eta, phi, mass):
    """
    Convert (pt, eta, phi, mass) into (E, px, py, pz).

    Accepts scalars or numpy arrays / pandas Series (vectorised).
    """
    pt = np.asarray(pt, dtype=float)
    eta = np.asarray(eta, dtype=float)
    phi = np.asarray(phi, dtype=float)

    px = pt * np.cos(phi)
    py = pt * np.sin(phi)
    pz = pt * np.sinh(eta)
    p2 = px**2 + py**2 + pz**2
    E = np.sqrt(p2 + mass**2)
    return E, px, py, pz


def invariant_mass(pt1, eta1, phi1, pt2, eta2, phi2, mass1=MUON_MASS_GEV, mass2=MUON_MASS_GEV):
    """
    Invariant mass of a two-particle system from each particle's (pt, eta, phi).

    Defaults assume both particles are muons (as in the CMS dimuon education
    dataset). Pass different mass1/mass2 for other particle types.
    """
    E1, px1, py1, pz1 = four_momentum(pt1, eta1, phi1, mass1)
    E2, px2, py2, pz2 = four_momentum(pt2, eta2, phi2, mass2)

    E = E1 + E2
    px = px1 + px2
    py = py1 + py2
    pz = pz1 + pz2

    m2 = E**2 - px**2 - py**2 - pz**2
    # Guard against tiny negative values from floating point error
    m2 = np.clip(m2, a_min=0.0, a_max=None)
    return np.sqrt(m2)
