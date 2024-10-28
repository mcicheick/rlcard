'''
    File name: bridge/utils/bridge_card.py
    Author: William Hale
    Date created: 11/25/2021
'''

from termcolor import colored

from rlcard.games.base import Card
from rlcard.games.i151.utils.parameters import *


class I151Card(Card):
    real_colors = ['black', 'red', 'red', 'black']
    colors = ['♦', '♣', '♥', '♠']
    suits = COLORS
    ranks = NUMBERS

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> [Card]:
        return _deck.copy()

    @property
    def is_queen(self):
        return self.rank_index == QUEEN

    @property
    def is_eight(self):
        return self.rank_index == EIGHT

    @property
    def is_as(self):
        return self.rank_index == AS

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        self.suit_index = I151Card.suits.index(self.suit)
        self.rank_index = I151Card.ranks.index(self.rank)
        self.color = I151Card.colors[self.suit_index]
        self.card_id = len(I151Card.suits) * self.rank_index + self.suit_index

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.color}'

    @staticmethod
    def print_cards(cards):
        ''' Print out card in a nice form

        Args:
            card (str or list): The string form or a list of a UNO card
            wild_color (boolean): True if assign collor to wild cards
        '''
        if isinstance(cards, str):
            cards = [cards]
        if not cards:
            print('None', end='')
        else:
            for i, card in enumerate(cards):
                rank, suit = card[0], card[1]

                if suit in ['S', 'C']:
                    print(colored(card, 'black'), end='')
                elif suit in ['D', 'H']:
                    print(colored(card, 'red'), end='')
                else:
                    print(suit, end='')
                if i < len(cards) - 1:
                    print(', ', end='')


# deck is always in order from 2C, ... KC, AC, 2D, ... KD, AD, 2H, ... KH, AH, 2S, ... KS, AS
_deck = [I151Card(suit=suit, rank=rank) for rank in
         I151Card.ranks for suit in I151Card.suits]  # want this to be read-only
