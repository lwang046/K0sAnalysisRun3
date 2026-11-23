"""Stub Run3 pileup reweighter.

Port full implementation from LukaLambrecht/K0sAnalysis
reweighting/pileup/pileupreweighter.py and wire Collisions24 PU profiles
before enabling PU weights in analysis/mcvsdata_fill.py (drop --nopileup).

Until then, mcvsdata_fill defaults to --nopileup / soft-skip.
"""


AVAILABLE = False  # flip True when Collisions24 profiles are wired


class PileupReweighter(object):
  def __init__(self, campaign, year):
    self.campaign = campaign
    self.year = year
    raise NotImplementedError(
      "Run3 PU reweighting not wired yet. Pass --nopileup to mcvsdata_fill, "
      "or port upstream reweighting/pileup with Collisions24 profiles."
    )

  def initsample(self, inputfile):
    pass

  def weight(self, ntrueint):
    return None

  def upweight(self, ntrueint):
    return None

  def downweight(self, ntrueint):
    return None
