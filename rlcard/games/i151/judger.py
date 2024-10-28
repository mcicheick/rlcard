'''
    File name: bridge/judger.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import I151Game

from rlcard.games.i151.utils.action_event import *
from rlcard.games.i151.utils.move import *
from rlcard.games.i151.utils.utils import available_actions


class I151Judger:
    '''
        Judger decides legal actions for current player
    '''

    def __init__(self, game: 'I151Game'):
        ''' Initialize the class BridgeJudger
        :param game: BridgeGame
        '''
        self.game: I151Game = game
        self.actionExtractor: ActionExtractor = DefaultActionExtractor()
        # self.actionExtractor: ActionExtractor = MinimalActionExtractor()

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions: List[ActionEvent] = []
        if not self.game.is_over():
            current_player = self.game.round.get_current_player()
            # hand, top_card=-1, asked=-1, took=False
            hand = [c.card_id for c in current_player.hand]
            top_card = -1 if not self.game.round.dealer.top_card else self.game.round.dealer.top_card.card_id
            actions = self.actionExtractor.available_actions(hand, top_card=top_card, asked=self.game.round.asked,
                                                             took=self.game.round.took)
            legal_actions = [ActionEvent.from_action_id(action) for action in actions]
        return legal_actions


class ActionExtractor:

    def available_actions(self, hand, top_card, asked, took) -> List[int]:
        actions = available_actions(hand, top_card, asked, took)
        return actions


class DefaultActionExtractor(ActionExtractor):

    def available_actions(self, hand, top_card, asked, took) -> List[int]:
        top_card_number = top_card // CARD_COLOR_LENGTH
        actions = available_actions(hand, top_card, asked, took)
        if top_card != -1 and (top_card_number != EIGHT or asked != -1):
            if not took:
                actions = np.append(actions, DRAW_ACTION)
            else:
                actions = np.append(actions, PASS_ACTION)
        return actions


class MinimalActionExtractor(ActionExtractor):

    def available_actions(self, hand, top_card, asked, took) -> List[int]:
        top_card_number = top_card // CARD_COLOR_LENGTH
        actions = available_actions(hand, top_card, asked, took)
        if top_card != -1 and (top_card_number != EIGHT or asked != -1):
            if not len(actions):
                if not took:
                    actions = np.append(actions, DRAW_ACTION)
                else:
                    actions = np.append(actions, PASS_ACTION)
        return actions
