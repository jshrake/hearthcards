from numpy import random, cumsum
from random import choice
from .tags import Rarity
from scipy.stats import binom, hypergeom
from scipy.misc import comb
from numpy import nan_to_num
from . import carddef, locale, tags


'''
arena module for simulating arena drafts and calculating useful statistics
'''

# probability of rarity for a normal pick
NORMAL_PICK_P = {Rarity.COMMON: .9,
                 Rarity.RARE: .08,
                 Rarity.EPIC: .016,
                 Rarity.LEGENDARY: 0.004}

# probability of card rarities for a special (turns 1, 10, 20, 30) pick
SPECIAL_PICK_P = {Rarity.RARE: .8,
                  Rarity.EPIC: .16,
                  Rarity.LEGENDARY: .04}

# probability of obtaining a class card for a turn of a given rarity
CLASS_PICK_P = {Rarity.COMMON: .3,
                Rarity.RARE: .2,
                Rarity.EPIC: .3,
                Rarity.LEGENDARY: 0.08}


class CardPool(object):
    '''
    CardPool maintains a pool of hearthstone cards and offers
    2 functions: draw and replace_drawn.
    - draw selects a card from the pool with uniform probability
    and removes it from the pool of available cards to draw from
    - replace_drawn replaces all drawn cards back into the pool of
    cards to draw from
    '''
    def __init__(self, pool):
        self.initial = set(pool)
        self.avail = set(pool)

    def draw(self):  # (void) -> CardDef
        '''
        draw a random card without replacement
        '''
        c = choice(tuple(self.avail))
        self.avail.remove(c)
        return c

    def replace_drawn(self):  # (void) -> void
        '''
        replaces any drawn cards back into the available pool of cards
        to draw from
        '''
        self.avail = self.initial

    def __len__(self):  # (void) -> int
        '''
        number of cards available to draw from
        '''
        return len(self.avail)

    def __ior__(self, other):  # (CardPool) -> CardPool
        '''
        adds cards from the other CardPool to this CardPool
        '''
        self.initial |= other.initial
        self.avail |= other.initial
        return self

    def __iter__(self):
        return iter(self.avail)


def partition_by_rarity(cards):  # (list(CardDef)) -> {Rarity: CardPool}
    '''
    Returns a map from Rarirty to a list of CardDef objects from cards
    with the appropriate rarity
    '''
    t = {k: CardPool([c for c in cards if c.rarity == k])
         for k in list(Rarity)}
    # combine COMMON and FREE and delete FREE
    # this is convienent for the arena draft selection
    # where common and free cards are treated as the same
    # for the pick rarity
    t[Rarity.COMMON] |= t[Rarity.FREE]
    del t[Rarity.FREE]
    return t


def arena_draft(hero, card_pool):
    # (Class, list(CardDef)) -> list(list(CardDef, 3), 30)
    '''
    Returns a list of length 30 where each item is a sublist of 3 CardDef
    objects. The distribution of cards is chosen in a way to be mirror the
    the Hearthstone arena draft selection
    '''
    N = 30
    REG_N = 26
    SPEC_N = N - REG_N
    CARDS_PER_PICK = 3
    class_cards = [c for c in card_pool if c.player_class == hero]
    neutral_cards = [c for c in card_pool if c.player_class is None]
    class_cards_by_rarity = partition_by_rarity(class_cards)
    neut_cards_by_rarity = partition_by_rarity(neutral_cards)

    def draw_card(rarity):  # (Rarity) -> CardDef
        '''
        Given the rarity of this set of picks, returns a neutral or class
        CardDef with the appropriate probability
        '''
        cr = class_cards_by_rarity[rarity]
        nr = neut_cards_by_rarity[rarity]
        p = random.random()
        return (cr.draw() if p < CLASS_PICK_P[rarity] and
                len(cr) != 0 else nr.draw())

    def reset_pools():  # (void) -> void
        '''
        Calls replace_drawn on each CardPool in the class_cards_by_rarity
        and neut_cards_by_rarity dicts
        '''
        for _, card_pool in class_cards_by_rarity.items():
            card_pool.replace_drawn()
        for _, card_pool in neut_cards_by_rarity.items():
            card_pool.replace_drawn()

    #todo(jshrake): fix code duplication ahead
    draft = []
    '''REG_N regular picks with
    90.0% chance of COMMON or FREE
    08.0% chance of RARE
    01.6% chance of EPIC
    00.4% chance of LEGENDARY
    '''
    # rarity probabilities for normal pick
    norm_z = list(zip([Rarity.COMMON,    # < 90%
                       Rarity.RARE,      # < 98%
                       Rarity.EPIC,      # < 99.6%
                       Rarity.LEGENDARY  # < 100%
                       ],
                  cumsum([
                         NORMAL_PICK_P[Rarity.COMMON],
                         NORMAL_PICK_P[Rarity.RARE],
                         NORMAL_PICK_P[Rarity.EPIC],
                         NORMAL_PICK_P[Rarity.LEGENDARY]])))
    for rarity_p in random.random(REG_N):
        rarity = next(r for (r, w) in iter(norm_z) if rarity_p < w)
        draft.append([draw_card(rarity) for _ in range(CARDS_PER_PICK)])
        reset_pools()

    '''SPEC_N rare or better picks with
    80.0% chance of RARE
    16.0% chance of EPIC
    04.0% chance of LEGENDARY
    '''
    # rarity probabilities for special pick
    spec_z = list(zip([Rarity.RARE,      # < 80%
                       Rarity.EPIC,      # < 96%
                       Rarity.LEGENDARY  # < 100%
                       ],
                  cumsum([
                         SPECIAL_PICK_P[Rarity.RARE],
                         SPECIAL_PICK_P[Rarity.EPIC],
                         SPECIAL_PICK_P[Rarity.LEGENDARY]])))
    for rarity_p in random.random(SPEC_N):
        rarity = next(r for (r, w) in iter(spec_z) if rarity_p < w)
        draft.append([draw_card(rarity) for _ in range(CARDS_PER_PICK)])
        reset_pools()

    return draft


def pick_1_p(T1, S1, P1, T2, S2, P2):
    '''
    pick_1_p returns the probability of seeing 1 success in 3 turns under the
    following conditions: Consider two urns, U1 and U2, each containing a mix
    of red and blue balls. Suppose U1 contains S1 red balls, and T1-S1 blue
    balls, and U2 contains S2 red balls and T2-S2 blue balls. At each turn we
    select U1 with probability P1 or U2 with probability P2 = 1 - P1, and
    randomly pick a ball from the selected urn without replacement. What is the
    probability of selecting 1 red ball in 3 turns?
    '''
    # (int, int, float, int, int, float) -> float(0.0, 1.0)

    def hyper(M, n, N, k):
        constrained_k = max(min(k, min(n, N)), max(0, N - (M - n)))
        return nan_to_num(hypergeom(M=M, n=n, N=N).pmf(k=constrained_k))

    a = hyper(M=T1, n=S1, N=3, k=1)
    b = (hyper(M=T1, n=S1, N=2, k=1) *
         hyper(M=T2, n=T2 - S2, N=1, k=1) +
         hyper(M=T1, n=T1 - S1, N=2, k=2) *
         hyper(M=T2, n=S2, N=1, k=1))
    c = (hyper(M=T2, n=S2, N=2, k=1) *
         hyper(M=T1, n=T1 - S1, N=1, k=1) +
         hyper(M=T2, n=T2 - S2, N=2, k=2) *
         hyper(M=T1, n=S1, N=1, k=1))
    d = hyper(M=T2, n=S2, N=3, k=1)
    return (comb(3, 0) * P1 * P1 * P1 * a +
            comb(3, 1) * P1 * P1 * P2 * b +
            comb(3, 2) * P1 * P2 * P2 * c +
            comb(3, 3) * P2 * P2 * P2 * d)


def pick_0_p(T1, S1, P1, T2, S2):
    '''
    pick_0_p returns the probability of seeing 3 failures in 3 turns
    '''
    # (int, int, float, int, int, float) -> float(0.0, 1.0)
    P2 = 1.0 - P1

    def hyper(M, n, N, k):
        constrained_k = max(min(k, min(n, N)), max(0, N - (M - n)))
        return nan_to_num(hypergeom(M=M, n=n, N=N).pmf(k=constrained_k))

    a = hyper(M=T1, n=T1 - S1, N=3, k=3)
    b = (hyper(M=T1, n=T1 - S1, N=2, k=2) *
         hyper(M=T2, n=T2 - S2, N=1, k=1))
    c = (hyper(M=T2, n=T2 - S2, N=2, k=2) *
         hyper(M=T1, n=T1 - S1, N=1, k=1))
    d = hyper(M=T2, n=T2 - S2, N=3, k=3)
    return (comb(3, 0) * P1 * P1 * P1 * a +
            comb(3, 1) * P1 * P1 * P2 * b +
            comb(3, 2) * P1 * P2 * P2 * c +
            comb(3, 3) * P2 * P2 * P2 * d)


def pick_at_least_1_p(T1, S1, P1, T2, S2):
    '''
    pick_at_least_1_p returns the probability
    of seeing at lest 1 sucess in 3 turns
    '''
    # (int, int, float, int, int, float) -> float(0.0, 1.0)
    return 1.0 - pick_0_p(T1, S1, P1, T2, S2)


def partition_picks(N):  # (int(1, 30)) -> tuple(int(0,26), int(0,4))
    # the 4 special picks occur on pick 1, 10, 20, 30
    if N < 1 or N > 30:
        raise Exception("N must be greater than 0 and less than 30")
    elif N <= 1:
        return (N - 1, 1)
    elif N <= 10:
        return (N - 2, 2)
    elif N <= 20:
        return (N - 3, 3)
    elif N <= 30:
        return (N - 4, 4)


def draftable_cards(lang=locale.Locale.US):
    # Locale -> list(CardDef)
    '''
    Returns a list of arena draftable cards
    '''
    try:
        return draftable_cards.data
    except:
        draftable_cards.data = [c for c in carddef.card_db()[lang] if
                                c.is_collectible and
                                c.type != tags.CardType.HERO]
        return draftable_cards.data


def arena_probability(hero, predicate, N=30, card_pool=draftable_cards()):
    # (Class, ((CardDef) -> bool), int(0,30), list(CardDef)) -> ((int)->float)
    '''
    Returns the probability distribution for drafting k cards in the next
    N picks matching some predicate
    '''
    N_REG, N_SPEC = partition_picks(N)
    hero_pool = [c for c in card_pool if c.player_class == hero]
    neutral_pool = [c for c in card_pool if c.player_class is None]
    hero_by = partition_by_rarity(hero_pool)
    neut_by = partition_by_rarity(neutral_pool)
    inner_p = lambda m: sum([p * pick_at_least_1_p(len(hero_by[r]),
                            len([c for c in hero_by[r] if predicate(c)]),
                            CLASS_PICK_P[r],
                            len(neut_by[r]),
                            len([c for c in neut_by[r] if predicate(c)]))
        for r, p in m.items()])
    br = binom(N_REG, p=inner_p(NORMAL_PICK_P))
    bs = binom(N_SPEC, p=inner_p(SPECIAL_PICK_P))
    # probability of exactly k successes
    return lambda k: sum([br.pmf(k - i) * bs.pmf(i) for i in range(k + 1)])


def arena_expectation(hero, predicate, N=30, card_pool=draftable_cards()):
    p = arena_probability(hero, predicate, N, card_pool)
    return sum([p(k) * k for k in range(N + 1)])
