import datetime
import os
import sys

global number_of_probs
global num_of_runs
num_of_runs = 1


class Item:
    def __init__(self, index, volume):
        self.index = index
        self.volume = volume


class Bin:
    def __init__(self, cap_left, index):
        # self.items = items
        self.cap_left = cap_left
        self.index = index

    items = []


class Problem:
    def __init__(self, name, number_of_item, cap_of_bin, best_known_solution):
        self.name = name
        self.number_of_item = number_of_item
        self.cap_of_bin = cap_of_bin
        self.best_known_solution = best_known_solution

    items = []


class Solution:
    def __init__(self, num_of_bins, feasibility, problem):
        self.problem = problem
        self.num_of_bins = num_of_bins
        self.feasibility = feasibility

    bins = []


def load_problems(data):
    fp = open(data)
    global number_of_probs
    number_of_probs = fp.readline()
    number_of_probs = int(number_of_probs)
    problems = []
    for i in range(0, number_of_probs):
        instance_name = fp.readline().split()[0]
        temp_str = fp.readline().split()
        bin_cap = int(temp_str[0])
        num_of_item = int(temp_str[1])
        obj_opt = int(temp_str[2])
        problems.append(Problem(instance_name, num_of_item, bin_cap, obj_opt))
        for j in range(0, problems[i].number_of_item):
            item_volume = fp.readline()
            item_volume = int(item_volume)
            problems[i].items.append(Item(j, item_volume))
    fp.close()
    return problems


def print_problem(problems):
    print('number of problems', number_of_probs)
    for i in range(0, number_of_probs):
        print('NO. ', i, 'problem:')
        print('problem\'s name:', problems[i].name)
        print('capacity of bins:', problems[i].cap_of_bin)
        print('number of items', problems[i].number_of_item)
        print('objective solution: ', problems[i].best_known_solution)
        for j in range(0, problems[i].number_of_item):
            print('No.', j, ' item = ', problems[i].items[j].volume)


# 打印一个solution
def out_put_solution(solution, dest_file):
    fp = open(dest_file, 'a')
    # write name of problem
    fp.write(solution.problem.name)
    fp.write('\n')
    fp.write(' obj=   ')
    fp.write(str(solution.num_of_bins))
    fp.write('   ')
    fp.write(str(solution.num_of_bins - solution.problem.best_known_solution))
    fp.write('\n')
    for i in range(0, solution.num_of_bins):
        for item in solution.bins[i].items:
            fp.write(str(item.index))
            fp.write(' ')
        fp.write(str(solution.bins[i].index))
        fp.write("\n")


def print_solution(solution):
    print('problem name: ', solution.problem.name)
    print('objective :', solution.num_of_bins)
    for i in range(0, solution.num_of_bins):
        print('No. ', solution.bins[i].index, ' bin left capacity = ', solution.bins[i].cap_left)


# initial solution
def best_fit(prob):
    sln = Solution(0, 0, prob)
    while sln.problem.number_of_item > 0:
        items = []
        cap_left = prob.cap_of_bin
        max_volume = sln.problem.items[0].volume
        max_index = 0
        min_volume = sln.problem.items[0].volume
        for itemIndex in range(0, sln.problem.number_of_item):
            if max_volume < sln.problem.items[itemIndex].volume < sln.problem.cap_of_bin:
                max_volume = sln.problem.items[itemIndex].volume
                max_index = itemIndex
            if min_volume > sln.problem.items[itemIndex].volume:
                min_volume = sln.problem.items[itemIndex].volume
        items.append(Item(sln.problem.items[max_index].index, max_volume))
        cap_left -= max_volume
        # remove the item form problem
        sln.problem.items.pop(max_index)
        sln.problem.number_of_item -= 1

        while min_volume < cap_left and sln.problem.number_of_item > 0:
            max_index = 0
            max_volume = 0
            for itemIndex in range(0, sln.problem.number_of_item):
                if max_volume < sln.problem.items[itemIndex].volume < cap_left:
                    max_volume = sln.problem.items[itemIndex].volume
                    max_index = itemIndex
            items.append(Item(sln.problem.items[max_index].index, max_volume))
            cap_left -= max_volume
            sln.problem.items.pop(max_index)
            sln.problem.number_of_item -= 1
            for itemIndex in range(0, sln.problem.number_of_item):
                if min_volume > sln.problem.items[itemIndex].volume:
                    min_volume = sln.problem.items[itemIndex].volume
        # add the bin to solution
        new_bin = Bin(cap_left=cap_left, index=sln.num_of_bins)
        new_bin.items = items
        sln.bins.append(new_bin)
        sln.num_of_bins += 1
    return sln


# VNS to solve BPP problem
def variable_neighbourhood_search(problem):
    start = datetime.datetime.now()
    current_sln = best_fit(problem)
    global best_solution
    best_solution = current_sln

    end = datetime.datetime.now()
    time_spent = (end - start)


if __name__ == '__main__':
    para_list = sys.argv
    if len(para_list) < 7:
        print("Insufficient arguments. Please use the following options:-s data_file (compulsory)-c "
              "solution_file_to_check-t max_time (in sec)")
        exit(0)
    elif len(para_list) > 7:
        print("Too many arguments")
        exit(0)
    for i in range(0, len(para_list)):
        if para_list[i] == '-s':
            data_file = para_list[i + 1]
        elif para_list[i] == '-o':
            solution_file = para_list[i + 1]
        elif para_list[i] == '-t':
            max_time = para_list[i + 1]
    # init all problems
    my_problems = load_problems(data_file)
    p = open(solution_file, 'w')
    p.write(str(number_of_probs))
    p.write('\n')
    p.close()
    for i in range(0, number_of_probs):
        for run in range(0, num_of_runs):
            best_solution = best_fit(my_problems[i])
            out_put_solution(best_solution, solution_file)
