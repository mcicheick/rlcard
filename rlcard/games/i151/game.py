'''
    File name: bridge/game.py
    Author: William Hale
    Date created: 11/25/2021
'''
import math
from typing import List

import numpy as np

from rlcard.games.i151.judger import I151Judger
from rlcard.games.i151.round import I151Round
from rlcard.games.i151.utils.action_event import ActionEvent, CallActionEvent, PlayCardAction
from rlcard.games.i151.utils.utils import CARD_LENGTH


class I151Game:
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, nb_players=2, initial_hand_size=8, allow_step_back=False, point_limit: int = 1):
        '''Initialize the class BridgeGame
        '''
        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState()
        self.judger: I151Judger = I151Judger(game=self)
        self.actions: [ActionEvent] = []  # must reset in init_game
        self.round: I151Round or None = None  # must reset in init_game
        self.num_players: int = nb_players
        self.initial_hand_size = min(initial_hand_size, math.floor(CARD_LENGTH / nb_players))
        self.point_limit = point_limit

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        board_id = self.np_random.choice(list(range(self.num_players)))
        self.actions: List[ActionEvent] = []
        self.round = I151Round(num_players=self.num_players, board_id=board_id, np_random=self.np_random,
                               point_limit=self.point_limit)
        for player_id in range(self.num_players):
            player = self.round.players[player_id]
            self.round.dealer.deal_cards(player=player, num=self.initial_hand_size)
        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def step(self, action: ActionEvent):
        ''' Perform game action and return next player number, and the state for next player
        '''
        # current_player_id = self.round.current_player_id
        # if self.round.counter > 1000:
        #     print(f'{current_player_id} plays {action} {self.round.players[current_player_id].hand} {self.round.dealer.table} {self.round.dealer.stock_pile}')
        if isinstance(action, CallActionEvent):
            self.round.make_call(action=action)
        elif isinstance(action, PlayCardAction):
            self.round.play_card(action=action)
        else:
            raise Exception(f'Unknown step action={action}')
        self.actions.append(action)
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def get_num_players(self) -> int:
        ''' Return the number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions() -> int:
        ''' Return the number of possible actions in the game
        '''
        return ActionEvent.get_num_actions()

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        return self.round.current_player_id

    def is_over(self) -> bool:
        ''' Return whether the current game is over
        '''
        return self.round.is_over()

    def get_state(self, player_id: int):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = dict()
        state['player_id'] = player_id
        state['current_player'] = self.round.current_player_id
        state['hand'] = self.round.players[player_id].hand
        state['table'] = self.round.dealer.table
        state['top_card'] = self.round.dealer.top_card
        state['asked'] = self.round.asked
        state['took'] = self.round.took
        state['take_two'] = self.round.take_two
        state['num_players'] = self.num_players
        state['num_cards'] = {}
        for i in range(self.num_players):
            state['num_cards'][i] = len(self.round.players[i].hand)
        state['legal_actions'] = self.judger.get_legal_actions()
        return state
