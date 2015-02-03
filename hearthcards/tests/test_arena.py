import unittest
from ..arena import (draftable_cards, p_of_no_cards,
                     draft_e, partition_picks,
                     partition_by_rarity, CardPool,
                     REGULAR_TURN_P, SPECIAL_TURN_P)
from ..tags import Hero, Rarity


DRAFT_CARDS = draftable_cards()


class TestArenaFunctions(unittest.TestCase):

    def test_p_of_no_cards(self):
        # no chances for success, the probability of 0 sucesses is 1.0
        self.assertAlmostEqual(p_of_no_cards(20, 0, .5, 20, 0), 1.0)
        # only chances for sucess, the probability of 0 successes is 0.0
        self.assertAlmostEqual(p_of_no_cards(20, 20, .5, 20, 20), 0.0)
        # 50/50 shot of getting a success
        self.assertAlmostEqual(p_of_no_cards(20, 20, .5, 20, 0),
                               0.5 * 0.5 * 0.5)

    def test_partition_picks(self):
        def assert_pair_equal(tc, p, a, b):
            tc.assertEqual(p[0], a)
            tc.assertEqual(p[1], b)
        for draws in range(31):
            pair = partition_picks(draws)
            spec_picks = 0
            if draws == 0:
                spec_picks = 0
            elif draws < 10:
                spec_picks = 1
            elif draws < 20:
                spec_picks = 2
            elif draws < 30:
                spec_picks = 3
            elif draws == 30:
                spec_picks = 4
            assert_pair_equal(self, pair, draws - spec_picks, spec_picks)

    def test_pick_p(self):
        self.assertAlmostEqual(sum([v for _, v in REGULAR_TURN_P.items()]),
                               1.0)
        self.assertAlmostEqual(sum([v for _, v in SPECIAL_TURN_P.items()]),
                               1.0)

    def test_partition_by_rarity(self):
        neut_cards = [c for c in DRAFT_CARDS if c.hero is None]
        mage_cards = [c for c in DRAFT_CARDS if c.hero == Hero.MAGE]
        nr = partition_by_rarity(neut_cards)
        self.assertEqual(len(nr[Rarity.COMMON]), len([c for c in neut_cards
                         if c.rarity == Rarity.COMMON or
                         c.rarity == Rarity.FREE]))
        self.assertEqual(len(nr[Rarity.RARE]), len([c for c in neut_cards
                         if c.rarity == Rarity.RARE]))
        self.assertEqual(len(nr[Rarity.EPIC]), len([c for c in neut_cards
                         if c.rarity == Rarity.EPIC]))
        self.assertEqual(len(nr[Rarity.LEGENDARY]), len([c for c in neut_cards
                         if c.rarity == Rarity.LEGENDARY]))
        mr = partition_by_rarity(mage_cards)
        self.assertEqual(len(mr[Rarity.COMMON]), len([c for c in mage_cards
                         if c.rarity == Rarity.COMMON or
                         c.rarity == Rarity.FREE]))
        self.assertEqual(len(mr[Rarity.RARE]), len([c for c in mage_cards
                         if c.rarity == Rarity.RARE]))
        self.assertEqual(len(mr[Rarity.EPIC]), len([c for c in mage_cards
                         if c.rarity == Rarity.EPIC]))
        self.assertEqual(len(mr[Rarity.LEGENDARY]), len([c for c in mage_cards
                         if c.rarity == Rarity.LEGENDARY]))

    def test_card_pool(self):
        cp = CardPool(DRAFT_CARDS)
        starting_len = len(DRAFT_CARDS)
        self.assertEqual(len(cp), starting_len)
        cp.draw()
        self.assertEqual(len(cp), starting_len - 1)
        cp.replace_drawn()
        self.assertEqual(len(cp), starting_len)

    def test_expectation(self):
        mage_e = lambda pred: draft_e(Hero.MAGE, pred, 30, DRAFT_CARDS)
        ratio = lambda pred: mage_e(pred) / 90 * 100
        card_has_name = lambda n: lambda c: c.name == n

        self.assertAlmostEqual(
            ratio(card_has_name('bogus card name')), 0.0)

        self.assertAlmostEqual(
            ratio(card_has_name('Ancient of Lore')), 0.0)

        # free
        # http://www.arenavalue.com/card/NtZA26r/murloc-raider
        self.assertAlmostEqual(ratio(card_has_name('Murloc Raider')), 0.48, 2)

        # http://www.arenavalue.com/card/gd3juh1/arcane-intellect
        self.assertAlmostEqual(ratio(card_has_name('Arcane Intellect')),
                               1.23, 2)

        # common
        # http://www.arenavalue.com/card/HtpbR5L/undertaker
        self.assertAlmostEqual(ratio(card_has_name('Undertaker')), 0.48, 2)

        # http://www.arenavalue.com/card/4k3d8GQ/snowchugger
        self.assertAlmostEqual(ratio(card_has_name('Snowchugger')), 1.23, 2)

        # rare
        # http://www.arenavalue.com/card/pTN2IOu/target-dummy
        self.assertAlmostEqual(ratio(card_has_name('Target Dummy')), 0.288, 2)

        # http://www.arenavalue.com/card/IQco0uJ/unstable-portal
        self.assertAlmostEqual(ratio(card_has_name('Unstable Portal')),
                               0.396, 2)

        # epic
        # http://www.arenavalue.com/card/5ty510u/doomsayer
        self.assertAlmostEqual(ratio(card_has_name('Doomsayer')), 0.117, 2)

        # http://www.arenavalue.com/card/ialejFb/pyroblast
        self.assertAlmostEqual(ratio(card_has_name('Pyroblast')), 0.21, 2)

        # legendary
        # http://www.arenavalue.com/card/GiriWHg/ysera
        self.assertAlmostEqual(ratio(card_has_name('Ysera')), 0.02, 2)

        # http://www.arenavalue.com/card/eF0y9GC/archmage-antonidas
        self.assertAlmostEqual(ratio(card_has_name('Archmage Antonidas')),
                               0.03, 2)

        turn_rarity_expectations = ([
            mage_e(lambda c: c.rarity == Rarity.COMMON or
                   c.rarity == Rarity.FREE),
            mage_e(lambda c: c.rarity == Rarity.RARE),
            mage_e(lambda c: c.rarity == Rarity.EPIC),
            mage_e(lambda c: c.rarity == Rarity.LEGENDARY)])
        self.assertAlmostEqual(sum(turn_rarity_expectations) / 30.0, 1.0)


if __name__ == '__main__':
    unittest.main()
