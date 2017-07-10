#!/usr/bin/python3
"""Use case rover's collision detection."""

from engine.particlefilter import ParticleFilter
from model.substitution import Substitution

print("PF")
engine = ParticleFilter(configfile="../config/rover.yaml")
S = engine.substitute('dmin', best=0.76)
print("- results:\n{}".format(S))
print("- best: {}".format(S.best()))

# print model and substitution tree with highest utility
engine.model.write_dot("uc_rover_config-rover", 'pdf')
S.best().write_dot("uc_rover_config-rover_substitution", 'pdf')
