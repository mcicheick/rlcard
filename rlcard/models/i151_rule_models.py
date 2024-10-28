''' I151 rule models
'''

import numpy as np

import rlcard
from rlcard.models.model import Model


class I151RuleAgentV1(object):
    ''' I151 Rule agent version 1
    '''

    def __init__(self):
        self.use_raw = False

    def step(self, state):
        ''' Predict the action given raw state. A naive rule. Choose the color
            that appears least in the hand from legal actions. Try to keep wild
            cards as long as it can.

        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''

        legal_actions = state['raw_legal_actions']
        # state = state['raw_obs']
        if 'draw' in legal_actions:
            return 'draw'

        # Without wild-4, we randomly choose one
        action = np.random.choice(legal_actions)
        return action

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []


class I151ModelV1(Model):
    ''' UNO Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('i151')

        rule_agent = I151RuleAgentV1()
        self.rule_agents = [rule_agent for _ in range(env.num_players)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.rule_agents

    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        return True
