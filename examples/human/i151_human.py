''' A toy example of playing against rule-based bot on UNO
'''

import rlcard
from rlcard import models
from rlcard.agents.human_agents.i151_human_agent import HumanAgent

# Make environment
env = rlcard.make('i151')
human_agent = HumanAgent(env.num_actions)
cfr_agent = models.load('i151-rule-v1').agents[0]
env.set_agents([
    human_agent,
    cfr_agent,
])

print(">> I151 rule model V1")

while (True):
    print(">> Start a new game")
    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action

    print('===============     Result     ===============')
    print(payoffs)
    if payoffs[0] > 0:
        print('You win!')
    else:
        print('You lose!')
    print('')
    input("Press any key to continue...")
