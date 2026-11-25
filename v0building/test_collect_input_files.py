#!/usr/bin/env python3
"""Unit tests for v0builder multi-file / filelist input resolution."""
from __future__ import annotations

import os
import tempfile
import unittest

from v0builder import (
  _accumulate_hist,
  _hist_for_write,
  _read_filelist,
  collect_input_files,
)


class CollectInputFilesTest(unittest.TestCase):
  def test_single_root(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = os.path.join(tmp, "a.root")
      open(root, "wb").close()
      self.assertEqual(collect_input_files([root]), [os.path.abspath(root)])

  def test_filelist(self):
    with tempfile.TemporaryDirectory() as tmp:
      f1 = os.path.join(tmp, "one.root")
      f2 = os.path.join(tmp, "two.root")
      open(f1, "wb").close()
      open(f2, "wb").close()
      flist = os.path.join(tmp, "files.txt")
      with open(flist, "w", encoding="utf-8") as fh:
        fh.write("# comment\n")
        fh.write("\n")
        fh.write(f1 + "\n")
        fh.write("file:" + f2 + "\n")
      got = collect_input_files([flist])
      self.assertEqual(got, [os.path.abspath(f1), os.path.abspath(f2)])

  def test_filelist_relative_to_list_dir(self):
    with tempfile.TemporaryDirectory() as tmp:
      f1 = os.path.join(tmp, "rel.root")
      open(f1, "wb").close()
      flist = os.path.join(tmp, "list.txt")
      with open(flist, "w", encoding="utf-8") as fh:
        fh.write("rel.root\n")
      self.assertEqual(_read_filelist(flist), [os.path.abspath(f1)])

  def test_glob_and_dedup(self):
    with tempfile.TemporaryDirectory() as tmp:
      f1 = os.path.join(tmp, "a.root")
      f2 = os.path.join(tmp, "b.root")
      open(f1, "wb").close()
      open(f2, "wb").close()
      got = collect_input_files([os.path.join(tmp, "*.root"), f1])
      self.assertEqual(got, [os.path.abspath(f1), os.path.abspath(f2)])

  def test_multi_args(self):
    with tempfile.TemporaryDirectory() as tmp:
      f1 = os.path.join(tmp, "a.root")
      f2 = os.path.join(tmp, "b.root")
      open(f1, "wb").close()
      open(f2, "wb").close()
      self.assertEqual(
        collect_input_files([f1, f2]),
        [os.path.abspath(f1), os.path.abspath(f2)],
      )

  def test_root_url_passthrough(self):
    url = "root://eosuser.cern.ch//eos/user/x/y/z.root"
    self.assertEqual(collect_input_files([url]), [url])

  def test_missing_raises(self):
    with self.assertRaises(FileNotFoundError):
      collect_input_files(["/no/such/file.root"])

  def test_accumulate_hist_sums_to_numpy(self):
    import numpy as np
    import uproot

    with tempfile.TemporaryDirectory() as tmp:
      p1 = os.path.join(tmp, "h1.root")
      p2 = os.path.join(tmp, "h2.root")
      edges = np.linspace(0, 10, 11)
      with uproot.recreate(p1) as f:
        f["hCounter"] = np.histogram([1, 2, 3], bins=edges)
      with uproot.recreate(p2) as f:
        f["hCounter"] = np.histogram([1, 1, 2], bins=edges)
      acc = None
      with uproot.open(p1) as f:
        acc = _accumulate_hist(acc, f["hCounter"])
      with uproot.open(p2) as f:
        acc = _accumulate_hist(acc, f["hCounter"])
      written = _hist_for_write(acc)
      self.assertIsNotNone(written)
      values, out_edges = written
      np.testing.assert_allclose(out_edges, edges)
      np.testing.assert_allclose(values, [0, 3, 2, 1, 0, 0, 0, 0, 0, 0])


if __name__ == "__main__":
  unittest.main()
