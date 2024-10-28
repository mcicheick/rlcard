'''
    File name: bridge/player.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

import numpy as np

from rlcard.games.i151.utils.i151_card import I151Card
from rlcard.games.i151.utils.parameters import WEIGHTS


class I151Player:

    def __init__(self, player_id: int, np_random):
        ''' Initialize a BridgePlayer player class

        Args:
            player_id (int): id for the player
        '''
        if player_id < 0 or player_id > 3:
            raise Exception(f'I151Player has invalid player_id: {player_id}')
        self.np_random = np_random
        self.player_id: int = player_id
        self.hand: List[I151Card] = []
        self.points = []

    @property
    def point(self):
        return np.sum(self.points)

    @property
    def weight(self):
        return np.sum([WEIGHTS[c.card_id] for c in self.hand])

    def remove_card_from_hand(self, card: I151Card):
        self.hand.remove(card)

    def remove_cards_from_hand(self, cards: List[I151Card]):
        for card in cards:
            self.remove_card_from_hand(card)

    def __str__(self):
        return f'player-{self.player_id}'
