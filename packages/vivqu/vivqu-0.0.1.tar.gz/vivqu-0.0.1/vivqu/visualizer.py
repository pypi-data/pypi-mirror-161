# Copyright 2022 Airwallex.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def convert_df_to_dict(result):
    """Convert a dataframe to a dict

    The output format of QualityChecker.analyze is dataframe, which is not a constructed data type
    and is difficult for visualization of each separate column. This function changes it to dict.

    Args:
    result: pd.DataFrame
        Analysis result of previous procedure.

    Returns:
    data_dict: dict
        Analysis result converted to dict type.
    """
    data_dict = {}

    for idx in range(result.shape[0]):
        instance = result.at[idx, "instance"]
        name = result.at[idx, "name"]

        # create corresponding instance key-value pair if not exist
        if instance not in data_dict:
            data_dict[instance] = {}

        # implement what the instance contains by name
        if name == "Completeness":
            data_dict[instance]["Completeness"] = result.at[idx, "value"]
        elif name == "CountDistinct":
            data_dict[instance]["CountDistinct"] = result.at[idx, "value"]
        elif name[:13] == "Histogram.abs":
            if "Category" not in data_dict[instance]:
                data_dict[instance]["Category"] = []
            if "Data" not in data_dict[instance]:
                data_dict[instance]["Data"] = []
            data_dict[instance]["Category"].append(name[14:])
            data_dict[instance]["Data"].append(result.at[idx, "value"])
        elif name[:14] == "Histogram.bins":
            pass
        elif name[:15] == "Histogram.ratio":
            pass
        elif name == "Maximum":
            data_dict[instance]["Maximum"] = result.at[idx, "value"]
        elif name == "Minimum":
            data_dict[instance]["Minimum"] = result.at[idx, "value"]
        elif name[:15] == "ApproxQuantiles":
            if "ApproxQuantiles" not in data_dict[instance]:
                data_dict[instance]["ApproxQuantiles"] = []
            data_dict[instance]["ApproxQuantiles"].append(result.at[idx, "value"])
        else:
            raise(Exception("Unimplemented type of metric: instance {} of column {}".format(instance, name)))

    return data_dict

def pie_plot(ax: Axes, category: list, data: list, distinct, completeness, title):
    """Plot pie chart with given parameters.
    Args:
    ax: Axes
        Where to plot this sub figure.
    category: list
        Categories to be displayed.
    data: list
        Datas to be displayed.
    distinct: float
        Distinct values contained in this dataset.
    completeness: float
        Completeness of this dataset.
    title: str
        Title of this plot.
    """
    # if not copied in this way, the initial category and data list will
    # be change by the follwing pop operation
    raw_category = category.copy()
    raw_data = data.copy()

    data_sum = sum(raw_data)

    # calculate the completness
    if 'NullValue' in raw_category:
        null_index = raw_category.index("NullValue")
        null_cnt = raw_data[null_index]
        raw_category.pop(null_index)
        raw_data.pop(null_index)
        null_exist = True
    else:
        null_cnt = 0
        null_exist = False

    # only show first 5 categories at most
    if null_exist == True:
        aggreg_cnt = 4
    else:
        aggreg_cnt = 5
    
    raw_category = np.array(raw_category)
    raw_data = np.array(raw_data)
    # get sorted indice and reverse it to sort from large to small
    indice = np.argsort(raw_data)
    indice = np.flipud(indice)
    # sort data and category simultaneously
    sorted_data = raw_data[indice]
    sorted_category = raw_category[indice]

    # only reserve first 5 categories (include NullValue)
    if len(sorted_category) > aggreg_cnt:
        curr_sum = sorted_data[: aggreg_cnt - 1].sum()
        sorted_category = np.append(sorted_category[: aggreg_cnt - 1], "OtherValues")
        sorted_data = np.append(sorted_data[: aggreg_cnt - 1], data_sum - null_cnt - curr_sum)
    if null_exist:
        sorted_category = np.append("NullValue", sorted_category)
        sorted_data = np.append(null_cnt, sorted_data)

    # cut texts that are too long to display in the canvas
    show_category = []
    for idx in range(len(sorted_category)):
        curr_str = sorted_category[idx]
        if len(curr_str) > 20:
            curr_str = curr_str[:20] + "..."
        show_category.append(curr_str)
    
    # ensure that only NullValue is showed in red color
    if null_exist:
        color_palatte = ['C3', 'C0', 'C1', 'C2', 'C4', 'C5']
    else:
        color_palatte = ['C0', 'C1', 'C2', 'C4', 'C5', 'C6']
    
    ax.pie(
            sorted_data, 
            labels=show_category, 
            colors=color_palatte,
            labeldistance=None, 
            pctdistance=1.25, 
            autopct='%.2f%%', 
            frame=1
        )
    # the central white circle
    ax.pie([1], radius=0.7, colors='w', frame=1)

    ax.text(-1, 1.5,
        'Completness: {:.2f}\n'
        'Distinct values: {:d}'
        .format(completeness, int(distinct))
        )
    
    ax.legend(loc='upper center')
    ax.scatter([0, 0], [3.4, -1.2], color='white')

    ax.set_xlim((-1.8, 1.8))
    
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.set_title(title)


def box_plot(ax: Axes, Q1, Q2, Q3, min_val, max_val, completness, title):
    """plot box figure
    Args:
    ax: Axes
        Where to plot this sub figure.
    Q1, Q2, Q3: float
        The 0.25, 0.5, 0.75 quantiles.
    min_val, max_val: float
        Minimum and maxinum value.
    completeness: float
        Completeness to be displayed.
    title: str
        Title to be displayed.
    """
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR

    # plot the box
    ax.add_patch(
        patches.Rectangle(
            (-1, Q1),
            2,
            IQR,
            edgecolor='black',
            fill=False
        ))

    # vertival line
    ax.plot([0, 0], [lower_whisker, Q1], color='black', linewidth=1)
    ax.plot([0, 0], [Q3, upper_whisker], color='black', linewidth=1)
    # median value
    ax.plot([-1, 1], [Q2, Q2], color='orange', linewidth=1)
    # lower and upper whisker
    ax.plot([-0.5, 0.5], [lower_whisker, lower_whisker], color='black', linewidth=1)
    ax.plot([-0.5, 0.5], [upper_whisker, upper_whisker], color='black', linewidth=1)
    # minimum and maximum value
    ax.scatter([0, 0], [min_val, max_val], color='b', facecolors='none')

    highest = max(max_val, upper_whisker)
    lowest = min(min_val, lower_whisker)

    text_place = (highest + lowest) / 2

    ax.text(1.6, text_place, 
        'Completness: {:.2f}\n\n'
        'Max:      {:.2f}\n\n'
        'Q-75%:  {:.2f}\n'
        'Q-50%:  {:.2f}\n'
        'Q-25%:  {:.2f}\n\n'
        'Min:      {:.2f}\n'
        .format(completness, max_val, Q3, Q2, Q1, min_val)
        )
        
    ax.get_xaxis().set_visible(False)
    ax.set_xlim((-2, 5))

    ax.set_title(title)

def vis(result_df, max_col_per_line=4):
    """Visualize the analysis result.

    Args:
    result_df: pf.DataFrame
        Analysis result is the form of dataframe, which will be 
        further converted to dict.
    max_col_per_line: int
        Max columns in a single line.
    """
    result_dict = convert_df_to_dict(result_df)
    text_intances = []
    numeric_instances = []
    for instance in result_dict:
        if "Completeness" in result_dict[instance] \
            and "CountDistinct" in result_dict[instance] \
            and "Category" in result_dict[instance] \
            and "Data" in result_dict[instance]:
            text_intances.append(instance)
        elif "Completeness" in result_dict[instance] \
            and "Maximum" in result_dict[instance] \
            and "Minimum" in result_dict[instance] \
            and "ApproxQuantiles" in result_dict[instance]:
            numeric_instances.append(instance)

    total_len = len(text_intances) + len(numeric_instances)

    row = (total_len - 1) // max_col_per_line + 1
    if total_len <= max_col_per_line:
        col = total_len
    else:
        col = max_col_per_line

    _fig, axs = plt.subplots(row, col, figsize=(4 * col, 5 * row))

    for idx in range(len(text_intances)):
        instance = text_intances[idx]
        detail = result_dict[instance]
        pie_plot(
            axs[idx] if row == 1 else axs[idx // col, idx % col],
            detail["Category"], 
            detail["Data"], 
            detail["CountDistinct"], 
            detail["Completeness"], 
            instance
            )

    for idx in range(len(numeric_instances)):
        instance = numeric_instances[idx]
        detail = result_dict[instance]
        actual_idx = len(text_intances) + idx
        box_plot(
            axs[actual_idx] if row == 1 else axs[actual_idx // col, actual_idx % col],
            detail["ApproxQuantiles"][0], 
            detail["ApproxQuantiles"][1], 
            detail["ApproxQuantiles"][2],
            detail["Minimum"],
            detail["Maximum"],
            detail["Completeness"],
            instance
            )
    
    if row > 1:
        for idx in range(total_len, row * col):
            axs[idx // col, idx % col].axis('off')

    plt.show()