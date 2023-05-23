#!/usr/bin/env python3

import networkx as nx
import random

from broker._utils._log import console
from broker._utils.tools import print_tb
from broker.errors import QuietExit

job_ids = {}


def dependency_job(G, i):
    if not len(set(G.predecessors(i))):
        job_id = notDependentSubmitJob(i)
        job_ids[i] = job_id
        print("job_id: " + str(job_id))
    else:
        job_id = dependentSubmitJob(i, list(G.predecessors(i)))
        job_ids[i] = job_id
        print("job_id: " + str(job_id))
        print(list(G.predecessors(i)))
        # sys.exit()


def notDependentSubmitJob(i):
    print("sbatch " + i + ".sh")
    return random.randint(1, 101)


def dependentSubmitJob(i, predecessors):
    if len(predecessors) == 1:
        if not predecessors[0] in job_ids:  # if the required job is not submitted to Slurm, recursive call
            dependencyJob(predecessors[0])

        print("sbatch --dependency=afterok:" + str(job_ids[predecessors[0]]) + " " + i + ".sh")
        return random.randint(1, 101)
    else:
        job_id_str = ""

        for j in predecessors:
            if j not in job_ids:  # if the required job is not submitted to Slurm, recursive call
                dependencyJob(j)

            job_id_str += str(job_ids[j]) + ":"

        job_id_str = job_id_str[:-1]
        # print(job_id_str)
        print("sbatch --dependency=afterok:" + job_id_str + " " + i + ".sh")
        return random.randint(1, 101)


def main():
    G = nx.drawing.nx_pydot.read_dot("job.dot")

    print("List of nodes:")
    print(list(G.nodes))

    for i in list(G.nodes):
        # print(i)
        # print(len(set(G.successors(i))))
        if i not in job_ids:
            dependencyJob(i)

    for i in list(G.nodes):
        print(i + " " + str(job_ids[i]))

    # jid4=$(sbatch --dependency=afterany:$jid2:$jid3 job4.sh)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except QuietExit as e:
        print(f"#> {e}")
    except Exception as e:
        print_tb(str(e))
        console.print_exception(word_wrap=True)
