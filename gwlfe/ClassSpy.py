import inspect
import pandas as pd

class ClassSpy(object):
    def __init__(self):
        self.__dict__["sets"] = []
        self.__dict__["gets"] = []

    def __setattr__(self, key, value):
        caller = inspect.currentframe().f_back
        self.sets.append([key, caller.f_code.co_filename.split("\\")[-1] ,caller.f_lineno])
        self.__dict__[key] = value

    # def __getattribute__(self, item):
    #     if(item != "__dict__" and item != "sets"):
    #         caller = inspect.currentframe().f_back
    #         object.__getattribute__(self, "gets").append([item, caller.f_code.co_filename.split("\\")[-1] ,str(caller.f_lineno))])
    #         return object.__getattribute__(self, item)
    #     else:
    #         return object.__getattribute__(self, item)

    def variable_file_usages(self):
        sets = pd.DataFrame.from_records(self.sets,columns=("Variable","File","Line Number"))
        grouped_sets = sets.groupby(by="File")
        for key, item in grouped_sets:
            print(key)
            print(item)

    def unique_variable_file_usages(self):
        sets = pd.DataFrame.from_records(self.sets, columns=("Variable", "File", "Line Number")).drop_duplicates()
        grouped_sets = sets.groupby(by=["File"])
        for key, item in grouped_sets:
            not_file = sets.loc[~sets["File"]==key]

            print(key)
            print(item)
