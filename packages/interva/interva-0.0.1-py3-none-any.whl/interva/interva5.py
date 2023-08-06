# -*- coding: utf-8 -*-

"""
interva.interva5
-------------------

This module contains the class for the InterVA5 algorithm.
"""

from pandas import (DataFrame, Index, Series, read_csv, read_excel, to_numeric, 
                    isna, set_option)
from numpy import (ndarray, nan, nansum, nanmax, argsort, array, delete, where,
                   concatenate, copy)
from os import path, chdir, getcwd, mkdir
from logging import FileHandler, getLogger
from csv import writer
from time import time
from pkgutil import get_data
from io import BytesIO

from interva.data.causetext import CAUSETEXTV5
from vacheck.datacheck5 import datacheck5


class InterVA5:
    """InterVA5 algorithm for assigning cause of death.

    :param va_input: Verbal Autopsy data
    :type va_input: pandas data.frame or path to CSV file
    :param hiv: likelihood of HIV as a cause of death.  Possible values are
     "H" for high (~ 1:100 deaths), "L" for low (~ 1:1000), or "V" for very
     low (~ 1:10000)
    :type hiv: string
    :param malaria: likelihood of malaria as a cause of death.  Possible values are
     "H" for high (~ 1:100 deaths), "L" for low (~ 1:1000), or "V" for very
     low (~ 1:10000)
    :type malaria: string
    :param write: a logical value indicating whether the output should be written
     to the csv file indicated by the filename parameter.
    :type write: boolean
    :param directory: The directory to store the output from InterVA5.
     It should either be an existing valid directory, or a new folder to be created.
     If no path is given and the parameter for "write" is True, then
     the function stops and an error message is produced.
    :type directory: directory or string
    :param filename: the filename the user wishes to save the output.
     No extension needed. The output is in .csv format by default.
    :type filename: string
    :param output: the format of the output. Possible Values are 
     "classic": the same deliminated output format as InterVA5, or
     "extended": delimited output followed by full distribution of cause of death
     probability
    :type output: string
    :param append: a logical value indicating whether or not the new output should
     be appended to the existing file.
    :type append: boolean
    :param groupcode: a logical value indicating whether or not the group code will
     be included in the output causes.
    :type groupcode: boolean
    :param sci: an array containing the symptom-cause-information (aka Probbase)
     that InterVA uses to assign a cause of death.
    :type sci: pandas data.frame or numpy ndarray
    :param return_checked_data: a logical value indicating if the checked data
     (i.e., the data that have been modified by the consistency checks) should
     be returned.
    :type return_checked_data: boolean
    :param others: not used
    """

    def __init__(self, va_input, hiv: str, malaria: str, write: bool = True, 
                 directory = None, filename: str = "VA5_result", 
                 output: str = "classic", append: bool = False, 
                 groupcode: bool = False, sci = None, 
                 return_checked_data: bool = False, *others) -> dict:

        self.va_input = va_input
        self.hiv = hiv
        self.malaria = malaria
        self.write = write
        self.directory = directory
        self.filename = filename
        self.output = output
        self.append = append
        self.groupcode = groupcode
        self.sci = sci
        self.return_checked_data = return_checked_data

    def _check_data(self, va_input: Series, va_id: str, 
                    insilico_check: bool = False):
        """Run data check."""
        
        return datacheck5(va_input, va_id, insilico_check)
        

    def run(self):
        """Assign causes of death.
        
        :return: ids of VA input, VA results with cause assignments and
         likelihoods, likelihood of malaria and HIV as causes of death,
         and cleaned data from data consistency checks.
        :rtype: dictionary with keys ID (pandas.series), 
         VA_result (pandas data.frame), Malaria (str), HIV (str), and
         checked_data (pandas data.frame).
        """
        
        def va5(id, malprev, hivprev, pregstat, preglik, cause1, lik1, cause2, 
                lik2, cause3, lik3, indet, comcat, comnum, wholeprob, *others):
            return [id, str(malprev), str(hivprev), pregstat, preglik, 
                    cause1, lik1, cause2, lik2, cause3, lik3, indet, 
                    str(comcat), comnum, wholeprob]
                    
        def save_va5(x: list, filename: str, write: bool):
            if not write:
                return()
            del x[14]
            filename = filename + ".csv"
            with open(filename, 'a', newline="") as csvfile:
                csv_writer = writer(csvfile)
                csv_writer.writerow(x)
        
        def save_va5_prob(x: list, filename: str, write: bool):
            if not write:
                return()
            prob = x.pop(14)
            x = array(x)
            filename = filename + ".csv"
            x = concatenate((x, prob))
            with open(filename, 'a', newline="") as csvfile:
                csv_writer = writer(csvfile)
                csv_writer.writerow(x)
        
        logger = getLogger()
        file_handler = FileHandler("errorlogV5.txt", mode="a")
        logger.addHandler(file_handler)
        
        if not self.directory and self.write:
            raise IOError("error: please provide a directory (required when write = True)")
        if not self.directory:
            self.directory = getcwd()
        if not path.isdir(self.directory):
            mkdir(self.directory)
        globle_dir = getcwd()
        chdir(self.directory)
        
        probbaseV5 = None
        if self.sci is None:
            probbase_xls = get_data("interva", "data/probbase.xls")
            probbase = read_excel(probbase_xls)
            probbase.drop([probbase.index[0]], inplace=True)
            probbaseV5 = probbase.to_numpy()
        if self.sci is not None:
            validSCI = True
            if not isinstance(self.sci, DataFrame) and \
                not isinstance(self.sci, ndarray):
                validSCI = False
            if self.sci.shape[0] != 354 or self.sci.shape[1] != 87:
                validSCI = False
            if not validSCI:
                raise IOError \
                    ("Error: Invalid SCI (must be Pandas DataFrame or \
                     Numpy ndarray with 354 rows and 87 columns).")
            if isinstance(self.sci, DataFrame):
                self.sci = self.sci.to_numpy()
            probbaseV5 = self.sci
        self.probbaseV5Version = probbaseV5[0, 2]
        print(f"Using Probbase version: {self.probbaseV5Version}")
        causetextV5_horizontal = DataFrame(CAUSETEXTV5)
        self.causetextV5 = causetextV5_horizontal.transpose()
        if self.groupcode:
            # adding groupcode to cause
            for i in range(3, 64):
                cause = str(self.causetextV5.iloc[i, 0])
                code = str(self.causetextV5.iloc[i, 1])
                self.causetextV5.iloc[i, 1] = code + " " + cause
            self.causetextV5.drop(self.causetextV5.columns[0], axis=1, inplace=True)
        else:
            self.causetextV5.drop(self.causetextV5.columns[1], axis=1, inplace=True)
        if self.write:
            logger.info("Error & warning log built for InterVA5 %f \n", time())
        if isinstance(self.va_input, str) and self.va_input[-4:] == ".csv":
            self.va_input = read_csv(self.va_input)
        if "i183o" in self.va_input.columns:
            self.va_input.rename(columns={'i183o': 'i183a'}, axis='columns', 
                                 inplace=True)
            print("Due to the inconsistent names in the early version of " + 
                  "InterVA5, the indicator 'i183o' has been renamed as 'i183a'.")
        
        va_data = self.va_input
        va_input_names = va_data.columns
        id_inputs = va_data.iloc[:, 0]
        va_data = va_data.to_numpy()
        if va_data.shape[0] < 1:
            raise IOError("error: no data input")
        N = va_data.shape[0]
        S = va_data.shape[1]
        if S != probbaseV5.shape[0]:
            raise IOError \
                ("error: invalid data input format. Number of values incorrect")
        if va_input_names[S-1].lower() != "i459o":
            raise IOError("error: the last variable should be 'i459o'")
        va_data_csv = get_data("interva", "data/randomva5.csv")
        randomVA5 = read_csv(BytesIO(va_data_csv))
        valabels = randomVA5.columns
        count_changelabel = 0
        for i in range(S):
            input_col = va_input_names[i]
            std_col = valabels[i]
            if input_col.lower() != std_col.lower():
                logger.warning("Input column '{input_col}' does not match \
                        InterVA5 standard: '{std_col}'")
                count_changelabel = count_changelabel + 1
        if count_changelabel > 0:
            logger.warning("{count_changelabel} column names changed in input.\n" + 
                    "If the change is undesirable, please change in the input " +
                    "to match standard InterVA5 input format.")
            va_input_names = valabels
        prob_ncol = probbaseV5.shape[1]
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "I"] = 1
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "A+"] = 0.8
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "A"] = 0.5
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "A-"] = 0.2
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "B+"] = 0.1
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "B"] = 0.05
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "B-"] = 0.02
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "B -"] = 0.02
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "C+"] = 0.01
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "C"] = 0.005
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "C-"] = 0.002
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "D+"] = 0.001
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "D"] = 5e-04
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "D-"] = 1e-04
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "E"] = 1e-05
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == "N"] = 0
        probbaseV5[:,17:prob_ncol][probbaseV5[:,17:prob_ncol] == ""] = 0
        probbaseV5[0, 0:17] = 0
        Sys_Prior = copy(to_numeric(probbaseV5[0, :]))
        D = len(Sys_Prior)
        self.hiv = self.hiv.lower()
        self.malaria = self.malaria.lower()
        if self.hiv not in ['h', 'l', 'v'] or self.malaria not in ['h', 'l', 'v']:
            raise IOError("error: the HIV and Malaria indicator " +
                          "should be one of the three: 'h', 'l', 'v'")
        if self.hiv == "h":
            Sys_Prior[22] = 0.05
        if self.hiv == "l":
            Sys_Prior[22] = 0.005
        if self.hiv == "v":
            Sys_Prior[22] = 1e-05
        if self.malaria == "h":
            Sys_Prior[24] = 0.05
            Sys_Prior[44] = 0.05
        if self.malaria == "l":
            Sys_Prior[24] = 0.005
            Sys_Prior[44] = 1e-05
        if self.malaria == "v":
            Sys_Prior[24] = 1e-05
            Sys_Prior[44] = 1e-05
            
        ID_list = [nan for _ in range(N)]
        VA_result = [[] for _ in range(N)]
        if self.write and not self.append:
            header = ["ID", "MALPREV", "HIVPREV", "PREGSTAT", "PREGLIK", 
                            "CAUSE1", "LIK1", "CAUSE2", "LIK2", "CAUSE3", "LIK3", 
                            "INDET", "COMCAT", "COMNUM"]
            if self.output == "extended":
                header = header + list(self.causetextV5.iloc[:, 0])
            with open(self.filename + ".csv", 'w', newline="") as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(header)
        nd = max(1, round(N/100))
        np = max(1, round(N/10))
        
        if self.write:  
            logger.info("\n\n the following records are incomplete and " +
                "excluded from further processing: \n\n")
            
        first_pass = []
        second_pass = []
        errors = ""
        if self.return_checked_data:
            self.checked_data = [[] for _ in range(N)]
            # id_inputs declared & assigned above
        for i in range(N):
            k = i + 1
            if k % nd == 0:
                print(".", end="")
            if k % np == 0:
                print(round(k/N * 100), "% completed", sep="")
            if k == N:
                print("100% completed")
            index_current = str(id_inputs.iloc[i])
            va_data[i, :][va_data[i, :] == "n"] = "0"
            va_data[i, :][va_data[i, :] == "N"] = "0"
            va_data[i, :][va_data[i, :] == "y"] = "1"
            va_data[i, :][va_data[i, :] == "Y"] = "1"
            for j in range(va_data.shape[1]):
                if va_data[i, j] != "0" and va_data[i, j] != "1":
                    va_data[i, j] = nan

            input_current = copy(va_data[i, :])
            input_current[:][input_current[:] == "0"] = 0
            input_current[:][input_current[:] == "1"] = 1
            
            input_current[0] = 0
            if nansum(input_current[5:12]) < 1:
                if self.write:
                    errors = (errors + index_current + 
                              " Error in age indicator: Not Specified")
                continue
            if nansum(input_current[3:5]) < 1:
                if self.write:
                    errors = (errors + index_current + 
                              " Error in sex indicator: Not Specified")
                continue
            if nansum(input_current[20:328]) < 1:
                if self.write:
                    errors = (errors + index_current + 
                              " Error in indicators: No symptoms specified")
                continue
            
            input_current = Series(input_current, index=va_input_names)
            tmp = datacheck5(va_input=input_current, va_id=index_current)
            if self.return_checked_data:
                self.checked_data[i] = [id_inputs[i]] + list(tmp["output"][1:S])
            
            input_current = copy(tmp["output"])
            first_pass.append(tmp["first_pass"])
            second_pass.append(tmp["second_pass"])
            
            subst_vector = array([nan for _ in range(S)])
            subst_vector[probbaseV5[:, 5] == "N"] = 0
            subst_vector[probbaseV5[:, 5] == "Y"] = 1
            
            new_input = array([0 for _ in range(S)])
            for y in range(1,S):
                if not isna(input_current[y]):
                    if input_current[y] == subst_vector[y]:
                        new_input[y] = 1
            
            input_current[input_current == 0] = 1
            input_current[0] = 0
            input_current[isna(input_current)] = 0
            reproductiveAge = 0
            preg_state = " "
            lik_preg = " "
            if input_current[4] == 1 and (input_current[16:19].any() == 1):
                reproductiveAge = 1
            prob = copy(Sys_Prior[17:D])
            temp = where(new_input[1:len(input_current)] == 1)[0]
            for jj in range(len(temp)):
                temp_sub = temp[jj]
                for j in range(17, D):
                    prob[j-17] = prob[j-17] * probbaseV5[temp_sub + 1, j]
                if nansum(prob[0:3]) > 0:
                    prob[0:3] = prob[0:3] / nansum(prob[0:3])
                if nansum(prob[3:64]) > 0:
                    prob[3:64] = prob[3:64] / nansum(prob[3:64])
                if nansum(prob[64:70]) > 0:
                    prob[64:70] = prob[64:70] / nansum(prob[64:70])
            
            prob_names = self.causetextV5.iloc[:, 0].copy()
            prob_A = copy(prob[0:3])
            prob_B = copy(prob[3:64])
            prob_C = copy(prob[64:70])
            
            # Determine Preg_State and Likelihood
            if nansum(prob_A) == 0 or reproductiveAge == 0:
                preg_state = "n/a"
                lik_preg = " "
            if nanmax(prob_A) < 0.1 and reproductiveAge == 1:
                preg_state = "indeterminate"
                lik_preg = " "
            if where(prob_A == nanmax(prob_A))[0][0] == 0 and prob_A[0] >= 0.1 and reproductiveAge == 1:
                preg_state = "Not pregnant or recently delivered"
                lik_preg = round(prob_A[0]/nansum(prob_A) * 100)
            if where(prob_A == nanmax(prob_A))[0][0] == 1 and prob_A[1] >= 0.1 and reproductiveAge == 1:
                preg_state = "Pregnancy ended within 6 weeks of death"
                lik_preg = round(prob_A[1]/nansum(prob_A) * 100)
            if where(prob_A == nanmax(prob_A))[0][0] == 2 and prob_A[2] >= 0.1 and reproductiveAge == 1:
                preg_state = "Pregnant at death"
                lik_preg = round(prob_A[2]/nansum(prob_A) * 100)
            
            # Determine the output of InterVA
            prob_temp = copy(prob_B)
            prob_temp_names = prob_names.iloc[3:64].copy()
            top3 = []
            cause1 = lik1 = cause2 = lik2 = cause3 = lik3 = None
            indet = 0
            if nanmax(prob_temp) < 0.4:
                cause1 = lik1 = cause2 = lik2 = cause3 = lik3 = " "
                indet = 100
            if nanmax(prob_temp) >= 0.4:
                max1_loc = where(prob_temp == nanmax(prob_temp))[0][0]
                lik1 = round(nanmax(prob_temp) * 100)
                cause1 = prob_temp_names.iloc[max1_loc]
                prob_temp = delete(prob_temp, max1_loc)
                prob_temp_names.drop(prob_temp_names.index
                                     [max1_loc], inplace=True)
                top3.append(lik1)
                
                max2_loc = where(prob_temp == nanmax(prob_temp))[0][0]
                lik2 = round(nanmax(prob_temp) * 100)
                cause2 = prob_temp_names.iloc[max2_loc]
                if nanmax(prob_temp) < 0.5 * nanmax(prob_B):
                    lik2 = cause2 = " "
                prob_temp = delete(prob_temp, max2_loc)
                prob_temp_names.drop(prob_temp_names.index[max2_loc], inplace=True)
                top3.append(lik2)
                
                max3_loc = where(prob_temp == nanmax(prob_temp))[0][0]
                lik3 = round(nanmax(prob_temp) * 100)
                cause3 = prob_temp_names.iloc[max3_loc]
                if nanmax(prob_temp) < 0.5 * nanmax(prob_B):
                    lik3 = cause3 = " "
                top3.append(lik3)
                top3 = array([int(x) if x != " " else 0 for x in top3])
                indet = round(100 - nansum(top3))
            
            # Determine the Circumstances of Mortality CATegory (COMCAT) 
            # and probability
            prob_C_names = prob_names[64:70]
            comcat = ""
            comnum = None
            if nansum(prob_C) > 0:
                prob_C = prob_C / nansum(prob_C)
            if nanmax(prob_C) < 0.5:
                comcat = "Multiple"
                comnum = " "
            if nanmax(prob_C) >= 0.5:
                comcat = prob_C_names[where(prob_C == nanmax(prob_C))[0][0]]
                comnum = round(nanmax(prob_C) * 100)
            
            ID_list[i] = index_current
            combined_prob = Series(concatenate((prob_A, prob_B, prob_C)), index=prob_names)
            VA_result[i] = va5(index_current, self.malaria, self.hiv, preg_state, 
                               lik_preg, cause1, lik1, cause2, lik2, cause3, lik3, 
                               indet, comcat, comnum, wholeprob=combined_prob)
            if self.output == "classic":
                save_va5(VA_result[i].copy(), filename=self.filename, write=self.write)
            if self.output == "extended":
                save_va5_prob(VA_result[i].copy(), filename=self.filename, 
                              write=self.write)
        if self.write:
            logger.info("\n the following data discrepancies were identified and " +
                 "handled: \n" + str(first_pass) + "\nSecond pass\n" + 
                 str(second_pass))
        
        chdir(globle_dir)
        if not self.return_checked_data:
            self.checked_data = "return_checked_data = False"
        else:
            self.checked_data = DataFrame(self.checked_data)
            self.checked_data.columns = va_input_names
        
        ID_list = Series(ID_list, name="ID")
        nan_indices = where(ID_list.isna())[0]
        ID_list.drop(nan_indices, inplace=True)
        
        VA_result = DataFrame(VA_result)
        VA_result.columns = ["ID", "MALPREV", "HIVPREV", "PREGSTAT", "PREGLIK", 
                            "CAUSE1", "LIK1", "CAUSE2", "LIK2", "CAUSE3", "LIK3", 
                            "INDET", "COMCAT", "COMNUM", "WHOLEPROB"]
        VA_result.drop(nan_indices, axis=0, inplace=True)
        
        self.out = {"ID": ID_list,
                    "VA5": VA_result,
                    "Malaria": self.malaria,
                    "HIV": self.hiv,
                    "checked_data": self.checked_data}
        return self.out
         
    def get_hiv(self):
        """Get HIV parameter."""
        
        print(f"HIV parameter is {self.hiv}")
        return self.hiv

    def get_malaria(self):
        """Get malaria parameter."""
        
        print(f"Malaria parameter is {self.malaria}")
        return self.malaria

    def set_hiv(self, hiv_level):
        """Set HIV parameter."""
        
        hiv_lvl = hiv_level.lower()
        if hiv_lvl in ["h", "l", "v"]:
            self.hiv = hiv_lvl
        else:
            print(f"The provided HIV level \"{hiv_level}\" is invalid.")
        return self.hiv
        print(f"HIV parameter is {self.hiv}")

    def set_malaria(self, malaria_level):
        """Set malaria parameter."""
        
        malaria_lvl = malaria_level.lower()
        if malaria_lvl in ["h", "l", "v"]:
            self.malaria = malaria_lvl
        else:
            print(f"The provided malaria level \"{malaria_level}\" is invalid.")
        return self.malaria
        print(f"Malaria parameter is {self.malaria}")

    def get_ids(self):
        """Return pandas series of ID column in data."""
        
        va_df = self.va_input
        if isinstance(va_df, str) and va_df[-4:] == ".csv":
            va_df = read_csv(va_df)
        return va_df.loc[:, "ID"]

    def plot_csmf(self, top: int = 10, file: str = None):
        """Plot cause-specific mortality fraction (CSMF)."""
        pass

    def get_csmf(self, top: int = 10, groupcode: bool = False):
        """Return top causes in cause-specific mortality fraction (CSMF).
        
        :param top: number of top causes in the CSMF to be determined.
        :type top: integer
        :param groupcode: a logical value indicating whether or not the
         group code will be included in the cause names.
        :type groupcode: boolean
        :return: the top causes in CSMF with their values.
        :rtype: pandas.series
        """
        
        va = self.out["VA5"]
        set_option("display.max_rows", None)
        set_option("display.max_columns", None)
        
        # for future compatibility with non-standard input
        causenames = causeindex = []
        for i in range(va.shape[0]):
            if va.loc[i, "WHOLEPROB"] is not None:
                causenames = va.loc[i, "WHOLEPROB"].index
                causeindex = [x for x in range(len(causenames))]
                break
        include_probAC = False
        
        if self.groupcode:
            temp_names = ["" for _ in range(len(causenames))]
            for i in range(len(causenames)):
                if i <= 2 or i >= 64:
                    temp_names[i] = causenames[i]
                else:
                    cause_with_code = causenames[i]
                    temp_names[i] = cause_with_code.split(" ", 1)[1]
            causenames = Index(temp_names)
        
        # fix for removing the first 3 preg related death in standard input
        if ("Not pregnant or recently delivered" in causenames[0] and
            "Pregnancy ended within 6 weeks of death" in causenames[1] and
            "Pregnant at death" in causenames[2] and
            "Culture" in causenames[64] and
            "Emergency" in causenames[65] and
            "Health" in causenames[66] and
            "Inevitable" in causenames[67] and
            "Knowledge" in causenames[68] and
            "Resources" in causenames[69]):
            del causeindex[64:70]
            del causeindex[0:3]
            causenames = causenames.delete([0, 1, 2, 64, 65, 66, 67, 68, 69])
            include_probAC = True
            
        causetextV5_horizontal = DataFrame(CAUSETEXTV5)
        self.causetextV5 = causetextV5_horizontal.transpose()
        if groupcode:
            temp_names = ["" for _ in range(len(causenames))]
            for i in range(len(causenames)):
                if i <= 2 or i >= 64:
                    temp_names[i] = causenames[i]
                else:
                    cause = str(self.causetextV5.iloc[i, 0])
                    code = str(self.causetextV5.iloc[i, 1])
                    temp_names[i] = code + " " + cause
            causenames = Index(temp_names)
        
        # Check if there is a valid va object
        if len(va) < 1:
            print("No va5 object found")
            return()
        # Initialize the population distribution
        dist = None
        for i in range(len(va)):
            if va.iloc[i, 14] is not None:
                dist = [[0 for _ in range(len(va.iloc[i, 14]))]]
                break
        undeter = 0
        
        # Pick not simply the top # causes,
        # but the top # causes reported by InterVA5
        for i in range(len(va)):
            if va.iloc[i, 14] is None:  #wholeprob exists
                continue
            this_dist_copy = va.iloc[i, 14].copy()
            this_dist = this_dist_copy.to_numpy()
            if include_probAC:
                this_dist[0:3] = 0
                this_dist[64:70] = 0
            if max(this_dist) < 0.4:
                this_undeter = 1 if sum(this_dist) == 0 else sum(this_dist)
                undeter = undeter + this_undeter
            else:
                cutoff_3 = this_dist[argsort(-this_dist)][2]
                cutoff_2 = this_dist[argsort(-this_dist)][1]
                cutoff_1 = this_dist[argsort(-this_dist)][0]
                cutoff = min(max(cutoff_1 * 0.5, cutoff_3), max(cutoff_1 * 0.5, cutoff_2))
                
                undeter = undeter + sum(this_dist[where(this_dist < cutoff)[0]])
                this_dist[where(this_dist < cutoff)[0]] = 0
                if va.iloc[i, 14] is not None:
                    if i == 0:
                        dist = this_dist
                    else:
                        dist = dist + this_dist
        
        dist = Series(dist)
        dist_cod = None
        # Normalize the probability for CODs
        if undeter > 0:
            dist_cod = dist.iloc[causeindex].copy()
            dist_cod.loc[causeindex[len(causeindex)-1]+1] = undeter
            dist_cod = dist_cod / dist_cod.sum()
            dist_cod.index = causenames.append(Index(["Undetermined"]))
        else:
            dist_cod = dist.iloc[causeindex].copy()
            dist_cod = dist_cod / dist_cod.sum()
            dist_cod.index = causenames
        if (isna(dist_cod).sum() == len(dist_cod)).all():
            dist_cod[isna(dist_cod)] = 0
            
        dist_cod_sorted = dist_cod.copy()
        dist_cod_sorted.sort_values(ascending=False, inplace=True)
        # show causes with top non-zero values
        show_top = 0
        while dist_cod_sorted[show_top] > 0 and show_top < top:
            show_top = show_top + 1
        if show_top == top:
            a = dist_cod_sorted[show_top]
            b = dist_cod_sorted[show_top-1]
            while show_top < len(dist_cod_sorted) and (abs(a-b) < (a+b) * 1e-7):
                show_top = show_top + 1
                a = dist_cod_sorted[show_top]
                b = dist_cod_sorted[show_top-1]
        top_csmf = dist_cod_sorted.head(show_top)
        return(top_csmf)

    def write_csmf(self, top: int = 10, groupcode: bool = False,
                   filename: str = "csmf"):
        """Write cause-specific mortality fraction (CSMF) to CSV file.
        
        :param top: number of top causes in the CSMF to be determined.
        :type top: integer
        :param filename: the filename the user wishes to save the CSMF. 
         No extension needed. The output is in .csv format by default.
        :type filename: string
        """
        
        set_option("display.max_rows", None)
        set_option("display.max_columns", None)
        csmf = self.get_csmf(top=top, groupcode=groupcode)
        filename = filename + ".csv"
        csmf.to_csv(filename, header=False)

    def get_indiv_prob(self, top: int = 0, include_propensities = False):
        """Get individual causes of death distribution.
        
        :param top: number of top causes to be determined. If top is 0 or none,
         all propensities and no top causes will be be returned.
        :type top: integer
        :param include_propensities: a logical value indicating whether the
         propensities of top causes should be included. If top is 0 or none,
         this boolean is automatically set to true.
        :return: the individual causes of death distribution.
        :rtype: pandas data.frame
        """
        
        VA5 = self.out["VA5"]
        num_indiv = VA5.shape[0]
        cod_list = [[] for _ in range(num_indiv)]
        column_names = []
        if top == 0 or top is None:
            column_names = VA5.loc[0, "WHOLEPROB"].iloc[3:64].index
        else:
            for i in range(top):
                name = "CAUSE" + str(i+1)
                column_names.append(name)
                if include_propensities:
                    prob = "PROPENSITY" + str(i+1) + ""
                    column_names.append(prob)
            
        for indiv in range(num_indiv):
            wholeprob = VA5.loc[indiv, "WHOLEPROB"]
            prob_B = wholeprob.iloc[3:64].copy()
            
            if top == 0 or top is None:
                cod_list[indiv] = prob_B
            if top > 0:
                prob_temp = prob_B.to_numpy()
                prob_temp_names = prob_B.index
                for cause_num in range(top):
                    if cause_num == 0:
                        max_loc = where(prob_temp == nanmax(prob_temp))[0][0]
                        cause = cod_list[indiv] = [prob_temp_names[max_loc]]
                        if include_propensities:
                            if cause == " ":
                                cod_list[indiv].append(" ")
                            else:
                                cod_list[indiv].append(nanmax(prob_temp))
                        prob_temp = delete(prob_temp, max_loc)
                    if cause_num > 0:
                        max_loc = where(prob_temp == nanmax(prob_temp))[0][0]
                        cause = ""
                        if nanmax(prob_temp) < 0.5 * nanmax(prob_B):
                            cause = " "
                        else:
                            cause = prob_temp_names[max_loc]
                        cod_list[indiv].append(cause)
                        if include_propensities:
                            if cause == " ":
                                cod_list[indiv].append(" ")
                            else:
                                cod_list[indiv].append(nanmax(prob_temp))
                        prob_temp = delete(prob_temp, max_loc)
        cod_df = DataFrame(cod_list, columns=column_names)
        cod_df.insert(loc=0, column='ID', value=self.out["ID"])
        return cod_df

    def write_indiv_prob(self, top: int = 0, include_propensities: bool = False, 
                         filename: str = "indiv_prob"):
        """Write individual cause of death distribution to CSV file.
        
        :param top: number of top causes to be determined. If top is 0 or none,
         no causes and all propensities will be be displayed.
        :type top: integer
        :param include_propensities: a logical value indicating whether the
         propensities of top causes should be included. If top is 0 or none,
         this boolean is automatically set to true.
        :type include_propensities: boolean
        :param filename: the filename the user wishes to save the individual
         cause distribution. No extension needed. The output is in .csv 
         format by default.
        :type filename: string
        """
        
        set_option("display.max_rows", None)
        set_option("display.max_columns", None)
        indiv_prob = self.get_indiv_prob(top, include_propensities)
        filename = filename + ".csv"
        indiv_prob.to_csv(filename, index=False)


def get_example_input() -> DataFrame:
    """
    Get an example input.

    :return: 200 records of sample input.
    :rtype: pandas.DataFrame
    """

    example_input_bytes = get_data(__name__, "data/randomva5.csv")
    example_input = read_csv(BytesIO(example_input_bytes))
    return example_input


def get_probbase(version: str = "19") -> DataFrame:
    """
    Get the probbase (the source of the data consistency checks).

    :param version: Probbase version
    :type version: str
    :return: 200 records of sample input.
    :rtype: pandas.DataFrame
    """

    if version == "19":
        probbase_bytes = get_data(__name__, "data/probbaseV5_19.csv")
        probbase = read_csv(BytesIO(probbase_bytes))
        # note: version 19 does not have first row included in v18
    else:
        probbase_xls = get_data("interva", "data/probbase.xls")
        probbase = read_excel(probbase_xls)
        # note: drop first row so it matches the input
        probbase.drop([probbase.index[0]], inplace=True)

    return probbase
