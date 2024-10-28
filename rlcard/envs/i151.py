'''
    File name: envs/i151.py
    Author: William Hale
    Date created: 11/26/2021
'''

from collections import OrderedDict

import numpy as np

from rlcard.envs import Env
from rlcard.games.i151 import Game
from rlcard.games.i151.game import I151Game
from rlcard.games.i151.utils.action_event import ActionEvent
from rlcard.games.i151.utils.parameters import CARD_LENGTH, POSSIBLE_ACTIONS

#   [] Why no_bid_action_id in bidding_rep ?
#       It allows the bidding always to start with North.
#       If North is not the dealer, then he must call 'no_bid'.
#       Until the dealer is reached, 'no_bid' must be the call.
#       I think this might help because it keeps a player's bid in a fixed 'column'.
#       Note: the 'no_bid' is only inserted in the bidding_rep, not in the actual game.
#
#   [] Why current_player_rep ?
#       Explanation here.
#
#   [] Note: hands_rep maintain the hands by N, E, S, W.
#
#   [] Note: trick_rep maintains the trick cards by N, E, S, W.
#      The trick leader can be deduced since play is in clockwise direction.
#
#   [] Note: is_bidding_rep can be deduced from bidding_rep.
#      I think I added is_bidding_rep before bidding_rep and thus it helped in early testing.
#      My early testing had just the player's hand: I think the model conflated the bidding phase with the playing phase in this situation.
#      Although is_bidding_rep is not needed, keeping it may improve learning.
#
#   [] Note: bidding_rep uses the action_id instead of one hot encoding.
#      I think one hot encoding would make the input dimension significantly larger.
#

DEFAULT_GAME_CONFIG = {
    'game_num_players': 2,
}


class I151Env(Env):
    ''' I151 Environment
    '''

    def __init__(self, config):
        self.name = 'i151'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config=config)
        self.i151PayoffDelegate = WeightedI151PayoffDelegate()
        self.i151StateExtractor = BasicHandI151StateExtractor()
        state_shape_size = self.i151StateExtractor.get_state_shape_size(game=self.game)
        self.state_shape = [[1, state_shape_size] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        return self.i151PayoffDelegate.get_payoffs(game=self.game)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        return self.game.round.get_perfect_information()

    def _extract_state(self, state):  # wch: don't use state 211126
        ''' Extract useful information from state for RL.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        return self.i151StateExtractor.extract_state(game=self.game)

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (ActionEvent): The action that will be passed to the game engine.
        '''
        return ActionEvent.from_action_id(action_id=POSSIBLE_ACTIONS[action_id])

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.
        '''
        raise NotImplementedError  # wch: not needed


class I151PayoffDelegate(object):

    def get_payoffs(self, game: I151Game):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError


class DefaultI151PayoffDelegate(I151PayoffDelegate):

    def __init__(self):
        pass

    def get_payoffs(self, game: I151Game):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        payoffs = [game.round.game_over * 1 if p.point == 0 else game.round.game_over * -1 for p in game.round.players]
        return np.array(payoffs)


class WeightedI151PayoffDelegate(I151PayoffDelegate):

    def __init__(self):
        pass

    def get_payoffs(self, game: I151Game):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        payoffs = [-p.weight for p in game.round.players]
        return np.array(payoffs)


class FlipI151PayoffDelegate(I151PayoffDelegate):

    def __init__(self):
        pass

    def get_payoffs(self, game: I151Game):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        payoffs = [game.round.game_over * 1 if p.point == 0 else 0 for p in game.round.players]
        return np.array(payoffs)


class I151StateExtractor(object):  # interface

    def get_state_shape_size(self, game: I151Game) -> int:
        raise NotImplementedError

    def extract_state(self, game: I151Game):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            game (I151Game): The game

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    @staticmethod
    def get_legal_actions(game: I151Game):
        ''' Get all legal actions for current state.

        Returns:
            (OrderedDict): A OrderedDict of legal actions' id.
        '''
        legal_actions = game.judger.get_legal_actions()
        legal_actions_ids = {POSSIBLE_ACTIONS.index(action_event.action_id): None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)


class DefaultI151StateExtractor(I151StateExtractor):

    def __init__(self):
        super().__init__()

    def get_state_shape_size(self, game: I151Game) -> int:
        state_shape_size = 0
        state_shape_size += game.num_players * CARD_LENGTH  # hands_rep_size
        state_shape_size += CARD_LENGTH  # table
        state_shape_size += CARD_LENGTH  # hidden_cards_rep_size
        state_shape_size += game.num_players  # current_player_rep_size
        state_shape_size += 2  # take state
        state_shape_size += 4  # ask state
        return state_shape_size

    def extract_state(self, game: I151Game):
        ''' Extract useful information from state for RL.

        Args:
            game (I151Game): The game

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player = game.round.get_current_player()
        current_player_id = current_player.player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(CARD_LENGTH, dtype=int) for _ in
                     range(game.num_players)]  # game.num_players * CARD_LENGTH
        for card in game.round.players[current_player_id].hand:
            hands_rep[current_player_id][card.card_id] = 1

        # construct table_rep
        table_rep = [np.zeros(CARD_LENGTH, dtype=int)]  # CARD_LENGTH
        for i in range(len(game.round.dealer.table)):
            table_rep[0][i] = (game.round.dealer.table[i].card_id + 1) / CARD_LENGTH

        # construct hidden_card_rep (during trick taking phase)
        hidden_cards_rep = np.zeros(CARD_LENGTH, dtype=int)  # CARD_LENGTH
        for player in game.round.players:
            if player.player_id != current_player_id:
                for card in player.hand:
                    hidden_cards_rep[card.card_id] = 1

        # construct current_player_rep
        current_player_rep = np.zeros(game.num_players, dtype=int)  # game.num_players
        current_player_rep[current_player_id] = 1
        take_rep = [1 if game.round.took else 0, 1 if game.round.take_two else 0]  # 2
        ask_rep = np.zeros(4, dtype=int)
        if game.round.asked >= 0:
            ask_rep[game.round.asked] = 1

        rep = []
        rep += hands_rep
        rep += table_rep
        rep.append(hidden_cards_rep)
        rep.append(current_player_rep)
        rep.append(take_rep)
        rep.append(ask_rep)

        obs = np.concatenate(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = game.get_state(game.round.current_player_id)
        return extracted_state


class SingleHandI151StateExtractor(I151StateExtractor):

    def __init__(self):
        super().__init__()

    def get_state_shape_size(self, game: I151Game) -> int:
        state_shape_size = 0
        state_shape_size += CARD_LENGTH  # hands_rep_size
        state_shape_size += CARD_LENGTH  # table
        state_shape_size += CARD_LENGTH  # hidden_cards_rep_size
        state_shape_size += game.num_players  # current_player_rep_size
        state_shape_size += 2  # take state
        state_shape_size += 4  # ask state
        return state_shape_size

    def extract_state(self, game: I151Game):
        ''' Extract useful information from state for RL.

        Args:
            game (I151Game): The game

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player = game.round.get_current_player()
        current_player_id = current_player.player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(CARD_LENGTH, dtype=int)]  # CARD_LENGTH
        for card in game.round.players[current_player_id].hand:
            hands_rep[0][card.card_id] = 1

        # construct table_rep
        table_rep = [np.zeros(CARD_LENGTH, dtype=int)]  # CARD_LENGTH
        for i in range(len(game.round.dealer.table)):
            table_rep[0][i] = (game.round.dealer.table[i].card_id + 1) / CARD_LENGTH

        # construct hidden_card_rep (during trick taking phase)
        hidden_cards_rep = np.zeros(CARD_LENGTH, dtype=int)  # CARD_LENGTH
        for player in game.round.players:
            if player.player_id != current_player_id:
                for card in player.hand:
                    hidden_cards_rep[card.card_id] = 1

        # construct current_player_rep
        current_player_rep = np.zeros(game.num_players, dtype=int)  # game.num_players
        current_player_rep[current_player_id] = 1
        take_rep = [1 if game.round.took else 0, 1 if game.round.take_two else 0]  # 2
        ask_rep = np.zeros(4, dtype=int)
        if game.round.asked >= 0:
            ask_rep[game.round.asked] = 1

        rep = []
        rep += hands_rep
        rep += table_rep
        rep.append(hidden_cards_rep)
        rep.append(current_player_rep)
        rep.append(take_rep)
        rep.append(ask_rep)

        obs = np.concatenate(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = game.get_state(game.round.current_player_id)
        return extracted_state


class BasicHandI151StateExtractor(I151StateExtractor):

    def __init__(self):
        super().__init__()

    def get_state_shape_size(self, game: I151Game) -> int:
        state_shape_size = 0
        state_shape_size += CARD_LENGTH  # hands_rep_size
        state_shape_size += CARD_LENGTH  # table
        # state_shape_size += CARD_LENGTH  # hidden_cards_rep_size
        # state_shape_size += game.num_players  # current_player_rep_size
        state_shape_size += 2  # take state
        state_shape_size += 4  # ask state
        return state_shape_size

    def extract_state(self, game: I151Game):
        ''' Extract useful information from state for RL.

        Args:
            game (I151Game): The game

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player = game.round.get_current_player()
        current_player_id = current_player.player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(CARD_LENGTH, dtype=int)]  # CARD_LENGTH
        for card in game.round.players[current_player_id].hand:
            hands_rep[0][card.card_id] = 1

        # construct table_rep
        table_rep = [np.zeros(CARD_LENGTH, dtype=int)]  # CARD_LENGTH
        for i in range(len(game.round.dealer.table)):
            table_rep[0][i] = (game.round.dealer.table[i].card_id + 1) / CARD_LENGTH

        # construct hidden_card_rep (during trick taking phase)
        # hidden_cards_rep = np.zeros(CARD_LENGTH, dtype=int)  # CARD_LENGTH
        # for player in game.round.players:
        #     if player.player_id != current_player_id:
        #         for card in player.hand:
        #             hidden_cards_rep[card.card_id] = 1

        # construct current_player_rep
        # current_player_rep = np.zeros(game.num_players, dtype=int)  # game.num_players
        # current_player_rep[current_player_id] = 1
        take_rep = [1 if game.round.took else 0, 1 if game.round.take_two else 0]  # 2
        ask_rep = np.zeros(4, dtype=int)
        if game.round.asked >= 0:
            ask_rep[game.round.asked] = 1

        rep = []
        rep += hands_rep
        rep += table_rep
        # rep.append(hidden_cards_rep)
        # rep.append(current_player_rep)
        rep.append(take_rep)
        rep.append(ask_rep)

        obs = np.concatenate(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = game.get_state(game.round.current_player_id)
        return extracted_state
