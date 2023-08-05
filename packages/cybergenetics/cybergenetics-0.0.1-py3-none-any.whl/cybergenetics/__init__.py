from gym.envs.registration import register

register(
    id='CRN-v0',
    entry_point='cybergenetics.envs:CRNEnv',
)
