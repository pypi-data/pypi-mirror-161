__version__ = '0.0.3'

from gym.envs.registration import register

register(
    id='CRN-v0',
    entry_point='cybergenetics.envs.crn:CRNWrapper',
)
