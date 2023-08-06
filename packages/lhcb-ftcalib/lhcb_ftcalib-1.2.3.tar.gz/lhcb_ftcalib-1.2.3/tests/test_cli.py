import os
import pytest
import numpy as np
import uproot
import pandas as pd
import argparse
import lhcb_ftcalib as ft
from lhcb_ftcalib.printing import FTCalibException, MissingFile, MissingTree, MissingBranch
from lhcb_ftcalib.TaggerCollection import TaggerCollection

from lhcb_ftcalib.__main__ import read_file, validate_ops, run, load_data


def delete_file(F):
    if os.path.exists(F):
        os.remove(F)
        print("Removed", F)


def tuple_is_healthy(path, expected_events, expected_branches):
    # Check if expected branches are in tuple, check if branch lengths are correct
    ttree = uproot.open(path)["TaggingTree"]
    available_keys = list(ttree.keys())
    for branch in expected_branches:
        assert branch in available_keys, f"Expected branch {branch} not found in tuple {path}"
        assert ttree[branch].num_entries == expected_events, f"Expected events: {expected_events}, actual number of events {ttree[branch].num_entries} in branch {path}:TaggingTree:{branch}"


def parse_args(argv):
    argv = argv.split(" ")

    parser = argparse.ArgumentParser(description="TEST")
    parser.add_argument("rootfile",  type=str)
    parser.add_argument("-t",         dest="taggers",   type=str, nargs="+", default=[])
    parser.add_argument("-SS",        dest="SStaggers", type=str, nargs="+", default=[])
    parser.add_argument("-OS",        dest="OStaggers", type=str, nargs="+", default=[])
    parser.add_argument("-id",        dest="id_branch", type=str)
    parser.add_argument("-mode",      dest="mode",      type=str, choices=["Bu", "Bd", "Bs"],)
    parser.add_argument("-tau",       dest="tau",       type=str)
    parser.add_argument("-tauerr",    dest="tauerr",    type=str)
    parser.add_argument("-timeunit",  dest="timeunit",  type=str, default="ns", choices=["ns", "ps", "fs"])
    parser.add_argument("-weights",   dest="weights",   type=str)
    parser.add_argument("-op",        dest="op",        type=str, required=True,  nargs='+', choices=["calibrate", "combine", "apply"])
    parser.add_argument("-write",     dest="write",     type=str)
    parser.add_argument("-selection", dest="selection", type=str)
    parser.add_argument("-input_cal", dest="input_cal", type=str)
    parser.add_argument("-plot",      dest="plot",       action="store_true")
    parser.add_argument("-n",         default=-1, dest="nmax")
    parser.add_argument("-skip",      default=0, dest="skipfirst")
    parser.add_argument("-keep_branches", dest="keep_branches", type=str)

    parser.add_argument("-fun",  type=str, dest="fun", nargs=2, default=["poly", 2])
    parser.add_argument("-link", type=str, dest="link", choices=["mistag", "logit", "rlogit", "probit", "rprobit", "cauchit", "rcauchit"], default="mistag")

    parser.add_argument("-i", action="store_true", dest="interactive")
    parser.add_argument("-filetype", type=str, default="root", choices=["root", "csv"], dest="filetype")
    return parser.parse_args(argv)


def test_prepare_cli_tests():
    if not os.path.exists("tests/cli"):
        os.mkdir("tests/cli")

    if not os.path.exists("tests/cli/toy_data.root"):
        poly1 = ft.PolynomialCalibration(2, ft.link.mistag)
        generator = ft.toy_tagger.ToyDataGenerator(0, 20)

        with uproot.recreate("tests/cli/toy_data.root") as File:
            File["BU_TOY"] = generator(
                N = 30000,
                func = poly1,
                params = [[0, 0, 0, 0],
                          [0.01, 0.3, 0.01, 0],
                          [0.01, 0, 0.01, 0.3]],
                osc = False, lifetime=0, DM=0, DG=0, Aprod=0,
                tagger_types=["OSMuon", "OSKaon", "VtxCh"])

            File["BD_TOY"] = generator(
                N = 30000,
                func = poly1,
                params = [[0, 0, 0, 0],
                          [0.01, 0.3, 0.01, 0],
                          [0.01, 0, 0.01, 0.3]],
                osc=True, lifetime=1.52, DM=0.5065, DG=0, Aprod=0,
                tagger_types=["OSMuon", "OSKaon", "VtxCh"])
            File["BU_TOY_SSOS"] = generator(
                N = 20000,
                func = poly1,
                params = [[0, 0, 0, 0],
                          [0.01, 0.3, 0.01, 0],
                          [0.01, 0, 0.01, 0.3],
                          [0, 0, 0, 0]],
                osc=False, lifetime=1.52, DM=0, DG=0, Aprod=0,
                tagger_types=["OSMuon", "OSKaon", "VtxCh", "OSKaon"])


def test_read_file():
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F} -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate")

    # Missing file exception
    with pytest.raises(MissingFile):
        read_file(args.rootfile + "MISSING",
                  TAGGERS = args.taggers,
                  ID      = args.id_branch,
                  WEIGHT  = args.weights)

    # Missing tree
    with pytest.raises(MissingTree):
        read_file(args.rootfile + ":MISSING",
                  TAGGERS = args.taggers,
                  ID      = args.id_branch,
                  WEIGHT  = args.weights)

    with pytest.raises(MissingBranch):
        read_file(args.rootfile,
                  TAGGERS = args.taggers,
                  ID      = args.id_branch + "MISSING",
                  WEIGHT  = args.weights)


def test_validate_ops():
    args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate")
    validate_ops(args)
    args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate combine")
    validate_ops(args)
    args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate combine calibrate")
    validate_ops(args)
    args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op apply")
    validate_ops(args)
    args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op apply combine")
    validate_ops(args)

    with pytest.raises(FTCalibException):
        args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op apply apply")
        validate_ops(args)
    with pytest.raises(FTCalibException):
        args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate calibrate")
        validate_ops(args)
    with pytest.raises(FTCalibException):
        args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op apply calibrate")
        validate_ops(args)
    with pytest.raises(FTCalibException):
        args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate apply")
        validate_ops(args)
    with pytest.raises(FTCalibException):
        validate_ops(args)
        args = parse_args("FILE -t TOY0 -id FLAV_DECAY -mode Bu -op calibrate combine calibrate calibrate")


def compare_dataframe_to_file(filename, key, df):
    assert os.path.exists(filename)
    fdata = uproot.open(filename)[key].arrays(library="pd")
    for branch in fdata.columns.values:
        if branch in df:
            print(f"Comparing branch {branch} ...")
            b1 = np.array(fdata[branch])
            b2 = np.array(df[branch])
            if not all(np.isclose(b1, b2)):
                print("FAIL")
                print("CLI ", b1[b1 != b2])
                print("API ", b2[b1 != b2])
                raise AssertionError
            print("PASSED")


def test_run_calibrate_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_Bu"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BU_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bu -op calibrate -write {testfile} -plot")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch)

    run(args, load_data(args, loadplan, "branches"), loadplan)

    # API
    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_Bu"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BU_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bu -op calibrate combine -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    combination = tc.combine_taggers("Combination", calibrated=True)
    combdata = combination.get_dataframe(calibrated=False)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_calibrate_Bu():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_calibrate_Bu"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BU_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bu -op calibrate combine calibrate -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BU_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
    tc.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    combination = tc.combine_taggers("Combination", calibrated=True)
    combination.calibrate()
    combdata = combination.get_dataframe(calibrated=False)
    combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_Bd"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate -tau TAU -timeunit ps -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau)

    run(args, load_data(args, loadplan, "branches"), loadplan)

    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.calibrate()
    apidata = tc.get_dataframe()
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_Bd_selection_vartype1():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_Bd_sel_v1"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate -tau TAU -timeunit ps -write {testfile} -selection \"TAU>0.5\"")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau,
                         SEL     = args.selection)

    run(args, load_data(args, loadplan, "branches"), loadplan)

    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    selection = df.TAU > 0.5
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.calibrate()
    apidata = tc.get_dataframe()
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_Bd_selection_vartype2():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_Bd_sel_v2"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate -tau TAU -timeunit ps -write {testfile} -selection \"eventNumber%2==0\"")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau,
                         SEL     = args.selection)

    run(args, load_data(args, loadplan, "branches"), loadplan)

    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")
    selection = df.eventNumber % 2 == 0
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.calibrate()
    apidata = tc.get_dataframe()
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_Bd"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate combine -tau TAU -timeunit ps -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.calibrate()
    combination = tc.combine_taggers("Combination", calibrated=True)
    apidata = tc.get_dataframe(calibrated=True)
    combdata = combination.get_dataframe(calibrated=False)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_calibrate_Bd():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_calibrate_Bd"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate combine calibrate -tau TAU -timeunit ps -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU"], library="pd")
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU)
    tc.calibrate()
    combination = tc.combine_taggers("Combination", calibrated=True)
    combination.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    combdata = combination.get_dataframe(calibrated=False)
    combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_calibrate_Bd_selection():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_calibrate_Bd_sel"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate combine calibrate -tau TAU -timeunit ps -selection eventNumber%2==0 -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau,
                         SEL     = args.selection)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")

    selection = df.eventNumber % 2 == 0
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.calibrate()
    combination = tc.combine_taggers("Combination", calibrated=True, next_selection=None)
    combination.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    combdata = combination.get_dataframe(calibrated=False)
    combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


def test_run_calibrate_combine_calibrate_Bd_double_selection():
    # Run CLI command without crashing, then do the same with the API and compare results
    # CLI
    testfile = "tests/cli/test_calibrate_combine_calibrate_Bd_sel"
    delete_file(testfile + ".json")
    delete_file(testfile + ".root")
    F = "tests/cli/toy_data.root"
    args = parse_args(f"{F}:BD_TOY -t TOY0 TOY1 TOY2 -id FLAV_DECAY -mode Bd -op calibrate combine calibrate -tau TAU -timeunit ps -selection eventNumber%2==0;eventNumber%3==2 -write {testfile}")

    loadplan = read_file(args.rootfile,
                         TAGGERS = args.taggers,
                         ID      = args.id_branch,
                         TAU     = args.tau,
                         SEL     = args.selection)

    run(args, load_data(args, loadplan, "branches"), loadplan)
    # API
    df = uproot.open(F)["BD_TOY"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA",
                                          "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "FLAV_DECAY", "TAU", "eventNumber"], library="pd")

    selection = df.eventNumber % 2 == 0
    comb_selection = df.eventNumber % 3 == 2
    tc = TaggerCollection()
    tc.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bd", tau_ps=df.TAU, selection=selection)
    tc.calibrate()
    combination = tc.combine_taggers("Combination", calibrated=True, next_selection=comb_selection)
    combination.calibrate()
    apidata = tc.get_dataframe(calibrated=True)
    combdata = combination.get_dataframe(calibrated=False)
    combdata_calib = combination.get_dataframe(calibrated=True)
    for v in combdata.columns.values:
        apidata[v] = combdata[v]
    for v in combdata_calib.columns.values:
        apidata[v] = combdata_calib[v]
    compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

    delete_file(testfile + ".json")
    delete_file(testfile + ".root")


# def test_run_calibrate_combine_calibrate_Bu_calibrate_combination():
#     # Run CLI command without crashing, then do the same with the API and compare results
#     # CLI

#     testfile = "tests/cli/test_calibrate_combine_calibrate_Bu_calibrate_combination"
#     delete_file(testfile + ".json")
#     delete_file(testfile + ".root")
#     F = "tests/cli/toy_data.root"
#     args = parse_args(f"{F}:BU_TOY_SSOS -SS TOY0 TOY1 -OS TOY2 TOY3 -id FLAV_DECAY -mode Bu -op calibrate combine calibrate -write {testfile}")

#     loadplan = read_file(args.rootfile,
#                          TAGGERS   = args.taggers,
#                          SSTAGGERS = args.SStaggers,
#                          OSTAGGERS = args.OStaggers,
#                          ID        = args.id_branch)

#     run(args, load_data(args, loadplan, "branches"), loadplan)

#     # API
#     df = uproot.open(F)["BU_TOY_SSOS"].arrays(["TOY0_ETA", "TOY1_ETA", "TOY2_ETA", "TOY3_ETA",
#                                                "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "TOY3_DEC",
#                                                "FLAV_DECAY"], library="pd")
#     ss = TaggerCollection()
#     ss.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
#     ss.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
#     ss.calibrate()
#     os = TaggerCollection()
#     os.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
#     os.create_tagger("TOY3", df.TOY3_ETA, df.TOY3_DEC, B_ID=df.FLAV_DECAY, mode="Bu")
#     os.calibrate()

#     sscomb = ss.combine_taggers("SS_Combination", calibrated=True)
#     sscomb.calibrate()
#     oscomb = os.combine_taggers("OS_Combination", calibrated=True)
#     oscomb.calibrate()

#     apidata = pd.concat([
#         ss.get_dataframe(calibrated=True),
#         os.get_dataframe(calibrated=True),
#         sscomb.get_dataframe(calibrated=False),
#         oscomb.get_dataframe(calibrated=False),
#         sscomb.get_dataframe(calibrated=True),
#         oscomb.get_dataframe(calibrated=True)], axis=1)

#     tuple_is_healthy(testfile + ".root", expected_events=len(apidata), expected_branches=[
#         "TOY0_OMEGA", "TOY1_OMEGA", "TOY2_OMEGA", "TOY3_OMEGA",
#         "TOY0_ETA", "TOY1_ETA", "TOY2_ETA", "TOY3_ETA",
#         "TOY0_DEC", "TOY1_DEC", "TOY2_DEC", "TOY3_DEC",
#         "TOY0_CDEC", "TOY1_CDEC", "TOY2_CDEC", "TOY3_CDEC",
#         "SS_Combination_DEC", "OS_Combination_DEC",
#         "SS_Combination_CDEC", "OS_Combination_CDEC",
#         "SS_Combination_ETA", "OS_Combination_ETA",
#         "SS_Combination_OMEGA", "OS_Combination_OMEGA", "ID"])
#     compare_dataframe_to_file(testfile + ".root", "TaggingTree", apidata)

#     # Calibrate and combine combinations
#     testfile_part2 = "tests/cli/test_calibrate_combine_calibrate_Bu_calibrate_combination_part2"
#     args = parse_args(f"{testfile}.root:TaggingTree -t SS_Comb OS_Comb -id ID -mode Bu -op combine calibrate -write {testfile_part2}")

#     loadplan = read_file(testfile + ".root",
#                          TAGGERS   = args.taggers,
#                          SSTAGGERS = args.SStaggers,
#                          OSTAGGERS = args.OStaggers,
#                          ID        = args.id_branch)

#     run(args, load_data(args, loadplan, "branches"), loadplan)

#     # API
#     df = uproot.open(testfile + ".root")["TaggingTree"].arrays(["OS_Combination_OMEGA", "SS_Combination_OMEGA",
#                                                                 "OS_Combination_DEC", "SS_Combination_DEC", "ID"], library="pd")
#     tc = TaggerCollection()
#     tc.create_tagger("SS_Combination", df.SS_Combination_OMEGA, df.SS_Combination_DEC, B_ID=df.ID, mode="Bu")
#     tc.create_tagger("OS_Combination", df.OS_Combination_OMEGA, df.OS_Combination_DEC, B_ID=df.ID, mode="Bu")

#     comb = tc.combine_taggers("Combination", calibrated=False)
#     comb.calibrate()

#     apidata = pd.concat([
#         tc.get_dataframe(calibrated=False),
#         comb.get_dataframe(calibrated=False),
#         comb.get_dataframe(calibrated=True)], axis=1)

#     tuple_is_healthy(testfile_part2 + ".root", expected_events=len(apidata), expected_branches=[
#         "Combination_DEC", "Combination_CDEC", "Combination_ETA", "Combination_OMEGA", "ID"])
#     compare_dataframe_to_file(testfile_part2 + ".root", "TaggingTree", apidata)

#     delete_file(testfile + ".json")
#     delete_file(testfile + ".root")
