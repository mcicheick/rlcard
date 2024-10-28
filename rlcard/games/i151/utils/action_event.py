'''
    File name: bridge/utils/action_event.py
    Author: William Hale
    Date created: 11/25/2021
'''
from typing import List

from rlcard.games.i151.utils.i151_card import I151Card
from rlcard.games.i151.utils.parameters import *
from rlcard.games.i151.utils.utils import cards_to_action, action_to_cards


# ====================================
# Action_ids:
#       0 -> no_bid_action_id
#       1 to 35 -> bid_action_id (bid amount by suit or NT)
#       36 -> pass_action_id
#       37 -> dbl_action_id
#       38 -> rdbl_action_id
#       39 to 90 -> play_card_action_id
# ====================================


class ActionEvent(object):  # Interface

    draw_action_id = DRAW_ACTION
    pass_action_id = PASS_ACTION
    asked_action_start_id = ASKED_ACTION

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def from_action_id(action_id: int):
        if action_id == ActionEvent.pass_action_id:
            return PassAction()
        elif action_id == ActionEvent.draw_action_id:
            return DrawAction()
        elif action_id >= ActionEvent.asked_action_start_id:
            cards, ask = action_to_cards(action_id)
            return AskAction(cards=[I151Card.card(c) for c in cards], ask=ask)
        elif 0 <= action_id < ActionEvent.draw_action_id:
            cards, _ = action_to_cards(action_id)
            return PlayCardAction(cards=[I151Card.card(c) for c in cards])
        else:
            raise Exception(f'ActionEvent from_action_id: invalid action_id={action_id}')

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return AVAILABLE_ACTIONS_LENGTH


class CallActionEvent(ActionEvent):  # Interface
    pass


class PassAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.pass_action_id)

    def __str__(self):
        return "pass"

    def __repr__(self):
        return "pass"


class AskAction(CallActionEvent):

    def __init__(self, cards: List[I151Card], ask: int):
        action_id = cards_to_action(cards, ask)
        super().__init__(action_id=action_id)
        self.cards = cards
        self.ask = ask

    def __str__(self):
        return f'{[str(c) for c in self.cards]}:{I151Card.suits[self.ask]}'

    def __repr__(self):
        return f'{self.cards}->{I151Card.colors[self.ask]}'


class DrawAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.draw_action_id)

    def __str__(self):
        return "draw"

    def __repr__(self):
        return "draw"


class DoubleDrawAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.draw_action_id)

    def __str__(self):
        return "double_draw"

    def __repr__(self):
        return "double_draw"


class PlayCardAction(ActionEvent):

    def __init__(self, cards: List[I151Card]):
        play_card_action_id = cards_to_action(cards)
        super().__init__(action_id=play_card_action_id)
        self.cards: List[I151Card] = cards

    def __str__(self):
        return f"{[str(c) for c in self.cards]}"

    def __repr__(self):
        return f"{self.cards}"
