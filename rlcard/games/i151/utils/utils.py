'''
    File name: bridge/utils/utils.py
    Author: William Hale
    Date created: 11/26/2021
'''
import itertools
import math
from typing import List

from rlcard.games.i151.utils.i151_card import I151Card
from rlcard.games.i151.utils.parameters import *


def cards_to_vector(cards: List[I151Card]) -> np.ndarray:  # Note: not used ??
    plane = np.zeros(CARD_LENGTH, dtype=int)
    for card in cards:
        plane[card.card_id] = 1
    return plane


def _encode(n, v=None):
    if n == -1 and v is not None and v >= 0:
        return ASKED_ACTION + v
    elif n == -1 and v < 0:
        return PASS_ACTION
    if v is None:
        v = []
    d = len(v)
    if d == 0:
        return DRAW_ACTION
    b = np.asarray([math.pow(CARD_COLOR_LENGTH, d - i - 1) for i in range(d)], dtype=np.int32)
    s = int(math.pow(CARD_COLOR_LENGTH, d))
    return int(np.sum(b * v)) + s + n * SLOT_LENGTH


def cards_to_action(cards: List[I151Card], ask=None):
    if len(cards) == 0:
        return _encode(-1, v=ask)
    number = cards[0].rank_index
    colors = [c.suit_index for c in cards]
    return _encode(number, colors)


def action_to_cards(action_id):
    action = np.squeeze(action_id)
    asked = _get_asked(action_id)
    if asked > -1:
        return [], asked
    elif action == PASS_ACTION or action == DRAW_ACTION:
        return [], -1
    number = _get_number(action)
    colors = _get_colors(action)
    return (CARD_COLOR_LENGTH * number) + np.array(colors), -1


def _get_asked(action_id):
    if action_id < ASKED_ACTION:
        return -1
    return int(action_id - ASKED_ACTION)


def _get_number(action):
    return int(action / SLOT_LENGTH)


def _get_dim(action):
    if action % SLOT_LENGTH == 0:
        return 0
    return int(math.log(action % SLOT_LENGTH, 4))


def _get_colors(action):
    d = _get_dim(action)
    if d == 0:
        return None
    value = action % SLOT_LENGTH
    value = value - math.pow(CARD_COLOR_LENGTH, d)
    colors = [int(value / math.pow(4, d - i) % CARD_COLOR_LENGTH) for i in range(1, d + 1)]
    return colors


def available_actions(hand, top_card=-1, asked=-1, took=False):
    actions = np.array([])
    hand.sort()
    hand = np.array(hand)
    eight_indexes = np.where((hand // CARD_COLOR_LENGTH).astype(int) == EIGHT)[0]
    non_eights_indexes = np.where((hand // CARD_COLOR_LENGTH).astype(int) != EIGHT)[0]
    top_card_number = top_card // CARD_COLOR_LENGTH
    if top_card == -1:
        for c in hand[non_eights_indexes]:
            actions = np.append(actions, cards_to_action([I151Card.card(c)], -1))
        for i in range(0, len(eight_indexes)):
            for cards in itertools.combinations(hand[eight_indexes], i + 1):
                actions = np.append(actions, cards_to_action([I151Card.card(c) for c in cards], -1))
    else:
        if top_card_number == EIGHT:
            if asked != -1:
                same_colors_indexes = np.where((hand[non_eights_indexes] % CARD_COLOR_LENGTH) == asked)[0]
                for c in hand[same_colors_indexes]:
                    actions = np.append(actions, cards_to_action([I151Card.card(c)], -1))
                for i in range(0, len(eight_indexes)):
                    for cards in itertools.combinations(hand[eight_indexes], i + 1):
                        actions = np.append(actions, cards_to_action([I151Card.card(c) for c in cards], -1))
            else:
                for i in range(CARD_COLOR_LENGTH):
                    actions = np.append(actions, cards_to_action([], i))
        else:
            if top_card_number != AS:
                same_color_indexes = \
                    np.where((hand[non_eights_indexes] % CARD_COLOR_LENGTH) == int(top_card % CARD_COLOR_LENGTH))[0]
                for c in hand[same_color_indexes]:
                    actions = np.append(actions, cards_to_action([I151Card.card(c)], -1))

            same_number_indexes = np.where((hand // CARD_COLOR_LENGTH) == top_card_number)[0]
            for i in range(0, len(same_number_indexes)):
                for cards in itertools.combinations(hand[same_number_indexes], i + 1):
                    for perm in itertools.permutations([I151Card.card(c) for c in cards]):
                        actions = np.append(actions, cards_to_action(perm, -1))

            for i in range(0, len(eight_indexes)):
                for cards in itertools.combinations(hand[eight_indexes], i + 1):
                    actions = np.append(actions, cards_to_action([I151Card.card(c) for c in cards], -1))
    # if top_card != -1 and (top_card_number != EIGHT or asked != -1):
    #     # if not len(actions):
    #     if not took:
    #         actions = np.append(actions, DRAW_ACTION)
    #     else:
    #         actions = np.append(actions, PASS_ACTION)
    return actions.astype(int)
