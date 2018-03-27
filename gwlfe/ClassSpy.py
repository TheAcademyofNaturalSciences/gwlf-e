import inspect
import pandas as pd
import csv
from graphviz import Digraph
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


class ClassSpy(object):
    def __init__(self):
        self.__dict__["sets"] = []
        self.__dict__["gets"] = []

    def __setattr__(self, key, value):
        caller = inspect.currentframe().f_back
        if (type(value) == np.ndarray):
            self.sets.append([key, type(value).__name__ + str(value.shape), caller.f_code.co_filename.split("\\")[-1],
                              caller.f_lineno])
            self.__dict__[key] = ArraySpy(value, key, self.__dict__["gets"], self.__dict__["sets"])
        elif (type(value) != int and type(value) != np.float64 and type(value) != float):
            print(type(value))  # just in case this type would need a custom method like numpy arrays
            self.sets.append([key, type(value).__name__, caller.f_code.co_filename.split("\\")[-1], caller.f_lineno])
            self.__dict__[key] = value
        else:
            self.sets.append([key, type(value).__name__, caller.f_code.co_filename.split("\\")[-1], caller.f_lineno])
            self.__dict__[key] = value

    def __getattribute__(self, item):
        if (item != "__dict__" and item != "sets" and item != "gets"):
            caller = inspect.currentframe().f_back
            object.__getattribute__(self, "gets").append(
                [item, caller.f_code.co_filename.split("\\")[-1], str(caller.f_lineno)])
            return object.__getattribute__(self, item)
        else:
            return object.__getattribute__(self, item)

    def __del__(self):
        print("sets: " + str(len(self.sets)))
        print("gets: " + str(len(self.gets)))
        with open("sets.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows([["Variable", "Type", "File", "LineNo"]])
            writer.writerows(self.sets)
        with open("gets.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows([["Variable", "File", "LineNo"]])
            writer.writerows(self.gets)


class ArraySpy(np.ndarray):
    def __new__(cls, input_array, name, gets_in, sets_in):
        obj = np.asarray(input_array).view(cls)
        obj.name = name
        obj.gets = gets_in
        obj.sets = sets_in
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.info = getattr(obj, 'info', None)

    def __getitem__(self, item):
        # print(self.name + "[" + str(item) + "]")
        attr = np.ndarray.__getitem__(self, item)
        if issubclass(type(attr), np.ndarray):  # handle multi dimensional arrays
            return ArraySpy(attr, self.name, self.gets, self.sets)
        else:
            caller = inspect.currentframe().f_back
            object.__getattribute__(self, "gets").append(
                [self.name, caller.f_code.co_filename.split("\\")[-1], str(caller.f_lineno)])
            return attr

    def __setitem__(self, key, value):
        # print(self.name,value)
        caller = inspect.currentframe().f_back
        self.sets.append(
            [self.name, type(value).__name__, caller.f_code.co_filename.split("\\")[-1], caller.f_lineno])
        np.ndarray.__setitem__(self, key, value)


def variable_file_usages(self):
    sets = pd.DataFrame.from_records(self.sets, columns=("Variable", "File", "Line Number"))
    grouped_sets = sets.groupby(by="File")
    for key, item in grouped_sets:
        print(key)
        print(item)


def sets_to_csvs(sets, gets):
    sets = sets.drop_duplicates()
    gets = gets.drop_duplicates()

    variables = pd.concat([sets[["Variable", "File", "LineNo"]], gets]).drop_duplicates(subset=("Variable",))

    # edge connection csv
    variable_edges = pd.merge(sets, gets, how='outer', on=("LineNo", "File"), suffixes=('_set', '_get'))
    try:
        old_edges = pd.read_csv("connections.csv")
        variable_edges = pd.concat([variable_edges, old_edges]).drop_duplicates().reset_index(drop=True)
    except:
        print("no previous connections.csv")
    variable_edges.to_csv("connections.csv", index=False)

    # variables csv
    # add colors
    variable_colors = {
        "ndarray": "#FFFFFF",
        "ndarray(0L, 17L)": "#7073B6",
        "ndarray(0L,)": "#D75F05",
        "ndarray(12L, 31L)": "#B8EA7B",
        "ndarray(12L, 3L)": "#694176",
        "ndarray(12L,)": "#A3D467",
        "ndarray(15L, 12L)": "#D0F89F",
        "ndarray(15L, 12L, 31L)": "#e3ffc1",
        "ndarray(15L, 12L, 3L)": "#E1CDE6",
        "ndarray(15L, 16L)": "#ED8E1E",
        "ndarray(15L, 16L, 3L)": "#C29CCD",
        "ndarray(15L,)": "#78A24C",
        "ndarray(16L, 12L)": "#E9A800",
        "ndarray(16L, 15L, 12L, 31L)": "#FEDBA8",
        "ndarray(16L, 3L)": "#B087BF",
        "ndarray(16L,)": "#B77013",
        "ndarray(2L,)": "#61C5A4",
        "ndarray(31L,)": "#88B153",
        "ndarray(3L, 16L)": "#B087BF",
        "ndarray(3L,)": "#823F89",
        "ndarray(50L, 12L, 31L)": "#ff9e54",
        "ndarray(5L,)": "#3F70AC",
        "ndarray(6L,)": "#E72B99",
        "ndarray(9L,)": "#FFFE21",
    }
    variables_with_type_array = sets[sets["Type"].str.match("ndarray")]
    variables_with_type_array["Color"] = variables_with_type_array["Type"].map(variable_colors)

    variables = pd.merge(variables, variables_with_type_array[["Variable", "Color"]], how='outer', on=("Variable"))

    # change shape of inputs
    variables_read_from_parser = variable_edges.query(
        'File == "parser.py" & Variable_get != Variable_get & (Type == "float" | Type == "int" | Type == "str" | Type == "unicode")')  # a != a will return false for NaN
    variables_read_from_parser["Shape"] = "parallelogram"
    variables_read_from_parser.rename(columns={"Variable_set": "Variable"}, inplace=True)
    variables_read_from_parser.drop(columns=["File", "LineNo", "Variable_get"], inplace=True)
    # print(variables_read_from_parser[variables_read_from_parser["Variable"] == "AvSeptPhos"])
    # inputs = pd.merge(variables, variables_read_from_parser[["Variable", "Shape"]], how='outer')

    # change shape of outputs
    variables_written_to_output = variable_edges.query(
        'File == "WriteOutputFiles.py" & Variable_set != Variable_set & LineNo > 776')  # a != a will return false for NaN
    variables_written_to_output["Shape"] = "septagon"
    variables_written_to_output.rename(columns={"Variable_get": "Variable"}, inplace=True)
    variables_written_to_output.drop(columns=["File", "LineNo", "Variable_set"], inplace=True)
    # outputs = pd.merge(variables, variables_written_to_output[["Variable", "Shape"]], how='outer')

    # inputs.update(outputs)

    variables_with_shapes = pd.concat([variables_read_from_parser, variables_written_to_output])
    variables_with_shapes = variables_with_shapes.groupby('Variable').agg({
        'Shape': 'last',  # TODO: this should change the shape of Variables that are both an input and output
    }).reset_index()

    variables = pd.merge(variables, variables_with_shapes, how='outer')

    values = {'Color': "#000000", 'Shape': "box"}
    variables = variables.fillna(value=values)  # fill with defaults

    try:
        old_variables = pd.read_csv("variables.csv")
        variables = pd.concat([variables[["Variable", "Color", "Shape"]], old_variables]).drop_duplicates(
            keep='first').reset_index(
            drop=True)
    except IOError:
        print("no previous variables.csv")

    variables[["Variable", "Color", "Shape"]].to_csv("variables.csv",
                                                     index=False)  # only write out Variable/Color/Shape


def variable_connected_to_output(output_variable):
    graph = nx.DiGraph()
    variable_edges = pd.read_csv("connections.csv")
    complete_edges = variable_edges[variable_edges['Variable_set'].notnull() & variable_edges['Variable_get'].notnull()]
    for index, row in complete_edges.iterrows():
        graph.add_edge(row[4], row[0])
    reversed = nx.reverse(graph)

    variable_decendents = list(nx.descendants(reversed, output_variable))
    variable_decendents.append(output_variable)
    variable_graph(variable_decendents)


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def output_intersection():
    graph = nx.DiGraph()
    variables = pd.read_csv("variables.csv")
    variable_edges = pd.read_csv("connections.csv")
    complete_edges = variable_edges[variable_edges['Variable_set'].notnull() & variable_edges['Variable_get'].notnull()]
    for index, row in complete_edges.iterrows():
        graph.add_edge(row[4], row[0])
    reversed = nx.reverse(graph)

    outputs = variables[variables["Shape"] == "septagon"]
    inputs = variables[variables["Shape"] == "parallelogram"]
    inputs = list(inputs["Variable"])  # strip out the extra information
    intersections = []
    for index, output_1 in outputs.iterrows():
        row = []
        for index, output_2 in outputs.iterrows():
            # print(output_1[0],output_2[0])
            all_intersections = intersection(nx.descendants(reversed, output_1[0]),
                                             nx.descendants(reversed, output_2[0]))
            row.append([value for value in all_intersections if value not in inputs])
        intersections.append([output_1[0]] + row)

    with open('intersections.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list(outputs["Variable"]))
        for row in intersections:
            writer.writerow(row)
    # variable_decendents.append(output_variable)
    # variable_graph(variable_decendents)


def variables_connected_to_output():
    graph = nx.DiGraph()
    variable_edges = pd.read_csv("connections.csv")
    complete_edges = variable_edges[variable_edges['Variable_set'].notnull() & variable_edges['Variable_get'].notnull()]
    for index, row in complete_edges.iterrows():
        graph.add_edge(row[4], row[0])

    reversed = nx.reverse(graph)

    # get all the outputs
    variables = pd.read_csv("variables.csv")
    variables_connected = set()
    for index, row in variables[variables["Shape"] == "septagon"].iterrows():
        for descendant in list(nx.descendants(reversed, row[0])):
            variables_connected.add(descendant)

    print("Variables used in output: " + str(len(variables_connected)) + " (out of " + str(len(variables)) + ")")
    variable_graph(list(variables_connected))


def variable_graph(variable_subset=None):
    dot = Digraph(comment='The Round Table', strict=True, engine="dot")
    # splines="true"
    # overlap_scaling = '10'
    dot.attr(overlap="scale", rankdir='LR', size='180,180')
    # dot.format = 'svg'
    variable_edges = pd.read_csv("connections.csv")

    variables = pd.read_csv("variables.csv", usecols=("Variable", "Color", "Shape"))

    if (variables.isnull().values.any()):
        print(variables[variables.isnull().values])
        raise AssertionError("not all boxes are complete")

    complete_edges = variable_edges[variable_edges['Variable_set'].notnull() & variable_edges['Variable_get'].notnull()]
    for index, row in complete_edges.iterrows():
        # with dot.subgraph(name=key, node_attr={'shape': 'box'},body="test") as c:
        if (type(variable_subset) == list):  # add the edge if it is in the subset, or if we weren't passed a subset
            if (row[0] not in variable_subset or row[4] not in variable_subset):
                continue
        if (row[4] != "NYrs" and row[4] != "Area" and row[4] != "DimYrs" and row[4] != "WxYrs"):
            try:
                variable_entry = variables[variables["Variable"] == row[0]].iloc[0]
                if (variable_entry["Color"] == "#000000"):
                    dot.attr('node', color=variable_entry["Color"], style='solid')
                else:
                    dot.attr('node', color=variable_entry["Color"], style='filled')
                dot.attr('node', shape=variable_entry["Shape"])
                dot.node(row[0])
            except IndexError:
                dot.attr('node', color="#000000", style='solid')
                dot.attr('node', shape='box')
            try:
                variable_entry = variables[variables["Variable"] == row[4]].iloc[0]
                if (variable_entry["Color"] == "#000000"):
                    dot.attr('node', color=variable_entry["Color"], style='solid')
                else:
                    dot.attr('node', color=variable_entry["Color"], style='filled')
                dot.attr('node', shape=variable_entry["Shape"])
                dot.node(row[4])
            except IndexError:
                dot.attr('node', color="#000000", style='solid')
                dot.attr('node', shape='box')

            dot.edge(row[4], row[0])

    dot.save('graph.dot')
    dot.render('test', view=True)


if __name__ == "__main__":
    # sets = pd.DataFrame.from_csv("../sets.csv", header=0, index_col=None)
    # gets = pd.DataFrame.from_csv("../gets.csv", header=0, index_col=None)
    # sets_to_csvs(sets, gets)
    # variable_graph()
    variable_connected_to_output("AvTotalP")
    # variables_connected_to_output()
    # output_intersection()
