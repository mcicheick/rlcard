'''
    File name: bridge/utils/move.py
    Author: William Hale
    Date created: 11/25/2021
'''

#
#   These classes are used to keep a move_sheet history of the moves in a round.
#

from rlcard.games.i151.utils.action_event import ActionEvent, PassAction, DrawAction, DoubleDrawAction, AskAction, PlayCardAction
from rlcard.games.i151.utils.i151_card import I151Card

from rlcard.games.i151.player import I151Player


class I151Move(object):  # Interface
    pass


class PlayerMove(I151Move):  # Interface

    def __init__(self, player: I151Player, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action


class CallMove(PlayerMove):  # Interface

    def __init__(self, player: I151Player, action: ActionEvent):
        super().__init__(player=player, action=action)


class DealHandMove(I151Move):

    def __init__(self, dealer: I151Player, shuffled_deck: [I151Card]):
        super().__init__()
        self.dealer = dealer
        self.shuffled_deck = shuffled_deck

    def __str__(self):
        shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
        return f'{self.dealer} deal shuffled_deck=[{shuffled_deck_text}]'


class MakePassMove(CallMove):

    def __init__(self, player: I151Player):
        super().__init__(player=player, action=PassAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeDrawMove(CallMove):

    def __init__(self, player: I151Player):
        super().__init__(player=player, action=DrawAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeDoubleDrawMove(CallMove):

    def __init__(self, player: I151Player):
        super().__init__(player=player, action=DoubleDrawAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeAskMove(CallMove):

    def __init__(self, player: I151Player, ask_action: AskAction):
        super().__init__(player=player, action=ask_action)
        self.action = ask_action  # Note: keep type as BidAction rather than ActionEvent

    def __str__(self):
        return f'{self.player} asks {self.action}'


class PlayCardMove(PlayerMove):

    def __init__(self, player: I151Player, action: PlayCardAction):
        super().__init__(player=player, action=action)
        self.action = action  # Note: keep type as PlayCardAction rather than ActionEvent

    @property
    def cards(self):
        return self.action.cards

    def __str__(self):
        return f'{self.player} plays {self.action}'
