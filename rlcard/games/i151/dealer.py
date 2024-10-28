'''
    File name: bridge/dealer.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

import numpy as np

from rlcard.games.i151.player import I151Player
from rlcard.games.i151.utils.i151_card import I151Card


class I151Dealer:
    ''' Initialize a I151Dealer dealer class
    '''

    def __init__(self, np_random):
        ''' set shuffled_deck, set stock_pile, set table
        '''
        self.np_random = np_random
        self.shuffled_deck: List[
            I151Card] = I151Card.get_deck()  # keep a copy of the shuffled cards at start of new hand
        self.np_random.shuffle(self.shuffled_deck)
        self.stock_pile: List[I151Card] = self.shuffled_deck.copy()
        self.table: List[I151Card] = []

    def deal_cards(self, player: I151Player, num: int):
        ''' Deal some cards from stock_pile to one player

        Args:
            player (I151Player): The BridgePlayer object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())

    def take(self, player: I151Player, nb_cards=1):
        '''Take nb_cards for player'''
        while nb_cards > 0 and len(self.stock_pile) > 0:
            player.hand.append(self.stock_pile.pop())
            nb_cards -= 1
        while nb_cards > 0 and len(self.table) > 0:
            player.hand.append(self.table.pop(0))
            nb_cards -= 1

    def played(self, player: I151Player, cards: List[I151Card]):
        '''Add played card to table and remove from player hand'''
        for card in cards:
            self.table.append(card)
            player.remove_card_from_hand(card)

    @property
    def top_card(self) -> I151Card or None:
        if len(self.table) == 0:
            return None
        return self.table[-1]


if __name__ == '__main__':
    _np_random = np.random.RandomState()
    dealer = I151Dealer(_np_random)
    _player = I151Player(0, _np_random)
    dealer.deal_cards(_player, 30)
    print(_player.hand)
    dealer.played(_player, _player.hand[0:2])
    dealer.take(_player, 2)
    print(dealer.table)
    dealer.take(_player, 1)
    print(_player.hand)
    print(dealer.table)
    print(dealer.stock_pile)
