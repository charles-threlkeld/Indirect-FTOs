"""
indirect_ftos.py creates a json file that documents all
ftos available in the Switchboard corpus based on their
syntactic sentence type and sw_damsl dialogue act annotation.
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import filter_data


def get_ftos(file_list, sentence_fname="sentence_ftos.csv",
             directness_fname="direct_ftos.csv", refresh=False):
    """
    Given a list of csv files, return a json file name that contains
    the ftos of all the fto data indexed by syntax and dialogue act.
    """

    sentence_ftos = {"interrogative": {"question": [],
                                       "statement": []},
                     "declarative": {"question": [],
                                     "statement": []}}
    directness_ftos = []

    if os.path.exists(sentence_fname) and os.path.exists(directness_fname) \
       and not refresh:
        # We've already build the csv, and we don't want to rebuild it.
        with open(sentence_fname, 'r', encoding="UTF-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                sentence_type = row["sentence_type"]
                speech_act = row["speech_act"]
                # Declarative and statements are -0.5
                # Questions and interrogative are 0.5
                if sentence_type < 0:
                    if speech_act < 0:
                        sentence_ftos["declarative"]["statement"].append(
                            row["fto"])
                    elif speech_act > 0:
                        sentence_ftos["declarative"]["question"].append(
                            row["fto"])
                elif sentence_type > 0:
                    if speech_act < 0:
                        sentence_ftos["interrogative"]["statement"].append(
                            row["fto"])
                    elif speech_act > 0:
                        sentence_ftos["interrogative"]["question"].append(
                            row["fto"])

        with open(directness_fname, 'r', encoding="UTF-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                directness = float(row["directness"])
                fto = float(row["fto"])
                directness_ftos.append((directness, fto))

        return sentence_ftos, directness_ftos

    sentence_output = "fto,sentence_type,speech_act,convo_num\n"
    directness_output = "directness,fto,convo_num\n"

    for _, file_name in enumerate(file_list):
        # print(f"Checking {i+1} of {len(file_list)}\t{file_name}")

        with open(file_name, 'r', encoding="UTF-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    fto = float(row["fto"])
                except ValueError:
                    continue

                if not -1000 < fto < 1000:
                    continue
                try:
                    syntax = [float(row["declarative"]),
                              float(row["interrogative"])]
                except ValueError:
                    continue
                function_str = row["function"]
                convo_num = file_name.split(".")[0]
                if function_str == "command":
                    try:
                        directness_ftos.append((float(row["imperative"]), fto))
                        directness_output += f"{float(row['imperative'])}"
                        directness_output += f",{fto},{convo_num}\n"
                    except ValueError:
                        continue
                if function_str not in ["statement", "question"]:
                    # We aren't going to use other functions
                    continue

                if function_str == "statement":
                    function = -0.5
                    directness_ftos.append((syntax[0], fto))
                    directness_output += f"{syntax[0]},{fto},{convo_num}\n"
                else:
                    function = 0.5
                    directness_ftos.append((syntax[1], fto))
                    directness_output += f"{syntax[1]},{fto},{convo_num}\n"
                max_syntax = max(syntax)
                max_index = syntax.index(max_syntax)
                if max_syntax > 0.5:
                    if max_index == 0:
                        sentence_ftos["declarative"][function_str].append(fto)
                        sentence_type = -0.5
                    elif max_index == 1:
                        sentence_ftos["interrogative"][function_str].append(fto)
                        sentence_type = 0.5
                    sentence_output += f"{fto},{sentence_type},{function},"
                    sentence_output += f"{convo_num}\n"

    with open(sentence_fname, 'w', encoding="UTF-8") as csv_file:
        csv_file.write(sentence_output)

    with open(directness_fname, 'w', encoding="UTF-8") as csv_file:
        csv_file.write(directness_output)

    return sentence_ftos, directness_ftos

def make_fto_sentence_graph(data, figname="sentence_type_ftos.png", show=False):
    """Make a graph comparing FTOs by sentence type."""
    interrogative = data["interrogative"]["question"] + data["interrogative"]["statement"]
    declarative = data["declarative"]["question"] + data["declarative"]["statement"]
    sns.kdeplot(interrogative)
    sns.kdeplot(declarative)
    plt.title("FTOs after Sentence Type")
    plt.legend(labels=["Declarative", "Interrogative"])
    plt.xlabel("Milliseconds (ms)")
    plt.ylabel("Density")
    plt.xlim(-1000, 1000)
    plt.savefig(figname)
    if show:
        plt.show()
    else:
        plt.close()

    return figname


def make_fto_speech_act_graph(data, figname="speech_act_ftos.png", show=False):
    """Make a graph comparing FTOs by speech act."""
    statement = data["interrogative"]["statement"] + data["declarative"]["statement"]
    question = data["interrogative"]["question"] + data["declarative"]["question"]
    sns.kdeplot(statement, fill=True, label="Statement")
    sns.kdeplot(question, fill=True, label="Question")
    plt.legend()
    plt.title("FTOs following Speech Act Type")
    plt.xlabel("Milliseconds (ms)")
    plt.xlim(-1000, 1000)
    plt.gca().get_yaxis().set_ticks([])
    plt.ylabel("Density")
    plt.savefig(figname)
    if show:
        plt.show()
    else:
        plt.close()


    return figname


def make_fto_directness_graph(data, figname="indirect_ftos.png", show=False):
    """Make a graph comparing FTOs by speech act directness."""
    direct = data["interrogative"]["question"] + data["declarative"]["statement"]
    indirect = data["interrogative"]["statement"] + data["declarative"]["question"]
    sns.kdeplot(direct, fill=True, label="Direct")
    sns.kdeplot(indirect, fill=True, label="Indirect")
    plt.title("FTOs Following Direct vs Indirect Speech Acts")
    plt.legend()
    plt.xlabel("Milliseconds (ms)")
    plt.ylabel("Density")
    plt.xlim(-1000, 1000)
    plt.gca().get_yaxis().set_ticks([])
    plt.savefig(figname)
    if show:
        plt.show()
    else:
        plt.close()

    return figname


def main():
    """Gather data and create figures for FTOs by speech acts, sentence types,
    and directness."""
    fname_list = filter_data.get_data()
    sentence_data, directness_data = get_ftos(fname_list, refresh=True)

    show = True
    make_fto_sentence_graph(sentence_data, show=show)
    make_fto_speech_act_graph(sentence_data, show=show)
    make_fto_directness_graph(sentence_data, show=show)

    total_turns = len(sentence_data["interrogative"]["statement"]) + \
        len(sentence_data["interrogative"]["question"]) + \
        len(sentence_data["declarative"]["statement"]) + \
        len(sentence_data["declarative"]["question"])

    print(f"\n\nNumber of Turns:        {len(directness_data)}")
    print(f"\nNumber conversations:   {len(fname_list)}")
    print(f"Total number turns:     {total_turns}\n")
    print("|            | Declarative | Interrogative |")
    print("| Statements |        ", end="")
    print(f"{len(sentence_data['declarative']['statement'])} | ",
          end="")
    print(f"           {len(sentence_data['interrogative']['statement'])} |")
    print("|  Questions |          ", end="")
    print(f"{len(sentence_data['declarative']['question'])} | ",
          end="")
    print(f"          {len(sentence_data['interrogative']['question'])} |")

#main()
