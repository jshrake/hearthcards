from random import choice
from .tags import Rarity
from scipy.stats import binom, hypergeom
from scipy.misc import comb
from numpy import clip, floor, cumsum, random, sqrt
from . import carddef, locale, tags


'''
arena module for simulating arena drafts and calculating useful statistics
'''

# probability of card rarity for a regular turn
REGULAR_TURN_P = {Rarity.COMMON: .9,
                  Rarity.RARE: .08,
                  Rarity.EPIC: .016,
                  Rarity.LEGENDARY: 0.004}

# probability of card rarity for a special turn (turns 1, 10, 20, 30)
SPECIAL_TURN_P = {Rarity.RARE: .8,
                  Rarity.EPIC: .16,
                  Rarity.LEGENDARY: .04}

# probability of obtaining a class card on a turn of a given rarity
HERO_CARD_P = {Rarity.COMMON: .3,
               Rarity.RARE: .18,
               Rarity.EPIC: .3,
               Rarity.LEGENDARY: 0.07}


def draftable_cards(lang=locale.Locale.US):
    # Locale -> list(CardDef)
    '''
    Returns a list of arena draftable cards. Caches after the first call
    since carddef.card_db() is an expensive call
    '''
    try:
        return draftable_cards.data[lang]
    except:
        db = carddef.card_db()
        draftable_cards.data = {lang: [c for c in cl if
                                       c.is_collectible and
                                       c.type != tags.CardType.HERO]
                                for lang, cl in db.items()}
        return draftable_cards.data[lang]


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
    t = {r: CardPool([c for c in cards if c.rarity == r])
         for r in list(Rarity)}
    # combine COMMON and FREE and delete FREE
    # this is convienent for the arena draft selection
    # where common and free cards are treated as the same
    # for the pick rarity
    t[Rarity.COMMON] |= t[Rarity.FREE]
    del t[Rarity.FREE]
    return t


def arena_draft(hero, card_pool):
    # (Hero, list(CardDef)) -> list(list(CardDef, 3), 30)
    '''
    Returns a list of length 30 where each item is a sublist of 3 CardDef
    objects. The distribution of cards is chosen in a way to be mirror the
    the Hearthstone arena draft selection
    '''
    N = 30
    REG_N = 26
    SPEC_N = N - REG_N
    CARDS_PER_PICK = 3
    class_cards = [c for c in card_pool if c.hero == hero]
    neutral_cards = [c for c in card_pool if c.hero is None]
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
        return (cr.draw() if p <= HERO_CARD_P[rarity] and
                len(cr) > 0 else nr.draw())

    def reset_pools():  # (void) -> void
        '''
        Calls replace_drawn on each CardPool in the class_cards_by_rarity
        and neut_cards_by_rarity dicts
        '''
        for _, card_pool in class_cards_by_rarity.items():
            card_pool.replace_drawn()
        for _, card_pool in neut_cards_by_rarity.items():
            card_pool.replace_drawn()

    # todo(jshrake): fix code duplication ahead
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
                         REGULAR_TURN_P[Rarity.COMMON],
                         REGULAR_TURN_P[Rarity.RARE],
                         REGULAR_TURN_P[Rarity.EPIC],
                         REGULAR_TURN_P[Rarity.LEGENDARY]])))
    for rarity_p in random.random(REG_N):
        rarity = next(r for (r, w) in iter(norm_z) if rarity_p <= w)
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
                         SPECIAL_TURN_P[Rarity.RARE],
                         SPECIAL_TURN_P[Rarity.EPIC],
                         SPECIAL_TURN_P[Rarity.LEGENDARY]])))
    for rarity_p in random.random(SPEC_N):
        rarity = next(r for (r, w) in iter(spec_z) if rarity_p <= w)
        draft.append([draw_card(rarity) for _ in range(CARDS_PER_PICK)])
        reset_pools()

    return draft


def partition_picks(N):  # (int(1, 30)) -> tuple(int(0,26), int(0,4))
    # the 4 special picks occur on pick 1, 10, 20, 30
    '''
    Returns a tuple(# regular picks remaining, # of special picks remaining)
    given N total picks remaining
    ---------
    examples:
    - partition_picks(30) -> (26, 0)
    - partition_picks(10) -> (9, 1)
    - partition_picks(1) -> (0, 1)
    '''
    if N == 0:
        return (0, 0)
    else:
        special_picks = int(floor(N / 10)) + 1
        return (N - special_picks, special_picks)


def p_of_no_cards(T1, S1, P1, T2, S2):
    '''
    p_of_no_cards returns the probability of seeing 3 failures in 3 turns
    Consider two urns, U1 and U2, each containing a mix
    of red and blue balls. Suppose U1 contains S1 red balls, and T1-S1 blue
    balls, and U2 contains S2 red balls and T2-S2 blue balls. At each turn we
    select U1 with probability P1 or U2 with probability P2 = 1 - P1, and
    randomly pick a ball from the selected urn without replacement. What is the
    probability of selecting 0 red ball in 3 turns?
    '''
    # (int, int, float, int, int, float) -> float(0.0, 1.0)

    # probability of picking k succeses in N draws with n/M successes
    def hyper(M, n, N, k):
        # no successes? probability of 0 cards is 1.0!
        if n == 0:
            return 1.0
        # more picks than total cards? probability is 0.0 :(
        elif N > M:
            return 0.0
        else:
            return hypergeom(M=M, n=n, N=N).pmf(k=k)
    u1_p3 = hyper(M=T1, n=S1, N=3, k=0)
    u1_p2_u2_p1 = (hyper(M=T1, n=S1, N=2, k=0) * (T2 - S2) / T2)
    u2_p2_u1_p1 = (hyper(M=T2, n=S2, N=2, k=0) * (T1 - S1) / T1)
    u2_p3 = hyper(M=T2, n=S2, N=3, k=0)
    # the combs are the number of ways to arrange the urns
    # such that each arrangement is identifiable
    P2 = 1.0 - P1
    return clip(comb(3, 0) * pow(P1, 3) * u1_p3 +  # 111
                comb(3, 1) * pow(P1, 2) * P2 * u1_p2_u2_p1 +  # 112, 121, 211
                comb(3, 2) * P1 * pow(P2, 2) * u2_p2_u1_p1 +  # 122, 212, 221
                comb(3, 3) * pow(P2, 3) * u2_p3, 0.0, 1.0)  # 222


def p_of_at_least_one_card(T1, S1, P1, T2, S2):
    '''
    p_of_at_least_one_card returns the probability
    of seeing at least one card matching the predicate
    in an arena draft turn (pick)
    '''
    # (int, int, float, int, int, float) -> float(0.0, 1.0)
    return 1.0 - p_of_no_cards(T1, S1, P1, T2, S2)


def p_of_successful_turn(hero, predicate, card_pool=draftable_cards()):
    hero_pool = [c for c in card_pool if c.hero == hero]
    neutral_pool = [c for c in card_pool if c.hero is None]
    hero_by = partition_by_rarity(hero_pool)
    neut_by = partition_by_rarity(neutral_pool)
    return lambda m: clip(sum([p * p_of_at_least_one_card(len(hero_by[r]),
                          len([c for c in hero_by[r] if predicate(c)]),
                          HERO_CARD_P[r],
                          len(neut_by[r]),
                          len([c for c in neut_by[r] if predicate(c)]))
        for r, p in m.items()]), 0.0, 1.0)


def p_of_successful_regular_turn(hero, predicate, card_pool=draftable_cards()):
    return p_of_successful_turn(hero, predicate, card_pool)(REGULAR_TURN_P)


def p_of_successful_special_turn(hero, predicate, card_pool=draftable_cards()):
    return p_of_successful_turn(hero, predicate, card_pool)(SPECIAL_TURN_P)


def draft_p(hero, predicate, N=30, card_pool=draftable_cards()):
    # (Hero, ((CardDef) -> bool), int(0,30), list(CardDef)) -> ((int)->float)
    '''
    Returns the probability distribution that the arena draft process generates
    k successful turns with N turns remaining. A turn is considered a succeses
    if at least one of the three cards satisfies the predicate
    '''
    N_REG, N_SPEC = partition_picks(N)
    p_of_success = p_of_successful_turn(hero, predicate, card_pool)
    br = binom(N_REG, p=p_of_success(REGULAR_TURN_P))
    bs = binom(N_SPEC, p=p_of_success(SPECIAL_TURN_P))
    return lambda k: clip(
        sum([br.pmf(k - i) * bs.pmf(i) for i in range(k + 1)]), 0.0, 1.0)


def draft_e(hero, predicate, N=30, card_pool=draftable_cards()):
    '''
    Expected value
    '''
    p = draft_p(hero, predicate, N, card_pool)
    return sum([p(k) * k for k in range(N + 1)])


def draft_var(hero, predicate, N=30, card_pool=draftable_cards()):
    '''
    Variance
    '''
    p = draft_p(hero, predicate, N, card_pool)
    return (sum([p(k) * pow(k, 2) for k in range(N + 1)]) -
            pow(draft_e(hero, predicate, N, card_pool), 2))


def draft_sd(hero, predicate, N=30, card_pool=draftable_cards()):
    '''
    Standard deviation
    '''
    return sqrt(draft_var(hero, predicate, N, card_pool))
