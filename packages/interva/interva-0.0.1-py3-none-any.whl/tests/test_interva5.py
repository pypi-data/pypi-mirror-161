# -*- coding: utf-8 -*-

import pytest
from pandas import read_csv, DataFrame, Series, read_excel
from pkgutil import get_data
from io import BytesIO
from os.path import isfile

from interva.interva5 import InterVA5

@pytest.fixture
def example_va_data():
    va_data_csv = get_data("interva", "data/randomva5.csv")
    va_data = read_csv(BytesIO(va_data_csv))
    return va_data

@pytest.fixture
def example_va_ids():
    va_data_csv = get_data("interva", "data/randomva5.csv")
    va_data = read_csv(BytesIO(va_data_csv))
    va_ids = va_data.loc[:, "ID"]
    return va_ids

# run function tests
def test_run_write_without_directory_IO_error(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=True, directory=None, filename="VA5_result", output="extended", append=False)
    with pytest.raises(IOError):
        iv5out.run()

def test_run_incorrect_sci_shape(example_va_data):
    va_data = example_va_data
    probbase_xls = get_data("interva", "data/probbase.xls")
    probbase = read_excel(probbase_xls)
    probbaseV5 = probbase.to_numpy()
    probbase.drop([probbase.index[0]], inplace=True)
    probbase.drop([probbase.index[0]], inplace=True)
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False, sci=probbaseV5)
    with pytest.raises(IOError):
        iv5out.run()

def test_run_incorrect_data_last_col(example_va_data):
    va_data = example_va_data
    va_data.rename(columns={'i459o': 'i000a'}, inplace=True)
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    with pytest.raises(IOError):
        iv5out.run()

def test_run_invalid_malaria_indicator(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="m", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    with pytest.raises(IOError):
        iv5out.run()

def test_run_correct_va_input(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    iv5out.run()
    assert isinstance(iv5out.va_input, DataFrame)

def test_run_correct_id_output(example_va_data: DataFrame, example_va_ids: Series):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False, return_checked_data=True)
    run_output = iv5out.run()
    id_output = run_output["ID"]
    assert isinstance(id_output, Series)
    assert (id_output == example_va_ids).all()

def test_run_correct_VA5_output(example_va_data, example_va_ids):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False, return_checked_data=True)
    run_output = iv5out.run()
    va5_output = run_output["VA5"]
    # VA_result.columns = ["ID", "MALPREV", "HIVPREV", "PREGSTAT", "PREGLIK", 
    #                      "CAUSE1", "LIK1", "CAUSE2", "LIK2", "CAUSE3", "LIK3", 
    #                      "INDET", "COMCAT", "COMNUM", "WHOLEPROB"]
    assert isinstance(va5_output, DataFrame)
    assert (va5_output.loc[:, "ID"] == example_va_ids).all()
    assert (va5_output.loc[:, "MALPREV"] == "l").all()
    assert (va5_output.loc[:, "HIVPREV"] == "h").all()
    preg_stat_valid_values = ["n/a", "indeterminate", "Not pregnant or recently delivered", "Pregnancy ended within 6 weeks of death", "Pregnant at death"]
    assert (va5_output.loc[:, "PREGSTAT"].isin(preg_stat_valid_values)).all()
    cause_valid_values = [x for x in iv5out.causetextV5.iloc[3:64, 0]]
    cause_valid_values.append(" ")
    assert (va5_output.loc[:, "CAUSE1"].isin(cause_valid_values)).all()
    assert (va5_output.loc[:, "CAUSE2"].isin(cause_valid_values)).all()
    assert (va5_output.loc[:, "CAUSE3"].isin(cause_valid_values)).all()
    assert (va5_output.loc[:, "INDET"] <= 100).all()
    comcat_valid_values = [x for x in iv5out.causetextV5.iloc[64:70, 0]]
    comcat_valid_values.append("Multiple")
    assert (va5_output.loc[:, "COMCAT"].isin(comcat_valid_values)).all()
    assert (va5_output.loc[0, "WHOLEPROB"].index == iv5out.causetextV5.iloc[:, 0]).all()

def test_run_correct_malaria_output(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    run_output = iv5out.run()
    malaria_output = run_output["Malaria"]
    assert isinstance(malaria_output, str)
    assert malaria_output == "l"

def test_run_correct_hiv_output(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    run_output = iv5out.run()
    hiv_output = run_output["HIV"]
    assert isinstance(hiv_output, str)
    assert hiv_output == "h"

def test_run_correct_checked_data_output_if_true_return(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False, return_checked_data=True)
    run_output = iv5out.run()
    checked_data_output = run_output["checked_data"]
    assert isinstance(checked_data_output, DataFrame)
    assert (checked_data_output.columns == va_data.columns).all()

def test_run_correct_checked_data_output_if_false_return(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False, return_checked_data=False)
    run_output = iv5out.run()
    checked_data_output = run_output["checked_data"]
    assert isinstance(checked_data_output, str)
    assert checked_data_output == "return_checked_data = False"

# get hiv/malaria function tests
def test_get_hiv(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    assert iv5out.get_hiv() == "h"

def test_get_malaria(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    assert iv5out.get_malaria() == "l"

# set hiv/malaria function tests
def test_set_hiv_valid_change(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    assert iv5out.set_hiv("v") == "v"

def test_set_hiv_invalid_change(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    orig_hiv = iv5out.get_hiv()
    assert iv5out.set_hiv("m") == orig_hiv
    
def test_set_malaria_valid_change(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    assert iv5out.set_malaria("h") == "h"

def test_set_malaria_invalid_change(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    assert iv5out.set_malaria("m") == "l"

# get ids function tests
def test_get_ids_correct_output(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    ids_output = iv5out.get_ids()
    assert isinstance(ids_output, Series)
    assert ids_output.name == "ID"
    assert len(ids_output) == len(va_data)

# plot function tests
def test_plot_csmf():
    pass

# get csmf function tests
def test_get_csmf_shape(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    iv5out.run()
    csmf = iv5out.get_csmf(top=5)
    assert isinstance(csmf, Series)
    assert csmf.shape[0] == 5   # top 5 causes = 5 rows

def test_write_csmf(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    iv5out.run()
    iv5out.write_csmf(top=5, filename="csmf_top_5")
    assert isfile('csmf_top_5.csv')
    rowcount = 0
    for _ in open("csmf_top_5.csv"):
      rowcount = rowcount + 1
    assert rowcount == 5

def test_get_indiv_prob_top_none(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    run_output = iv5out.run()
    indiv_prob = iv5out.get_indiv_prob(top=0)
    assert isinstance(indiv_prob, DataFrame)
    assert (indiv_prob.loc[:, "ID"] == run_output["ID"]).all()
    assert indiv_prob.shape[1] == len(run_output["VA5"].loc[0, "WHOLEPROB"].iloc[3:64]) + 1 # length of prob_B + 1 (ID)

def test_get_indiv_prob_top_5(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    run_output = iv5out.run()
    indiv_prob = iv5out.get_indiv_prob(top=5, include_propensities=True)
    assert isinstance(indiv_prob, DataFrame)
    assert (indiv_prob.loc[:, "ID"] == run_output["ID"]).all()
    assert indiv_prob.shape[1] == 5*2 + 1   # 5 causes * 2 (for propensities) + 1 ID

def test_write_indiv_prob_top_5(example_va_data):
    va_data = example_va_data
    iv5out = InterVA5(va_data, hiv="h", malaria="l", write=False, directory="VA test", filename="VA5_result", output="extended", append=False)
    run_output = iv5out.run()
    iv5out.write_indiv_prob(top=5, filename="indiv_prob_top_5")
    assert isfile('indiv_prob_top_5.csv')
    rowcount = 0
    for _ in open("indiv_prob_top_5.csv"):
      rowcount = rowcount + 1
    assert rowcount == len(run_output["ID"]) + 1    # account for column headers
    