# Yuyan Zhou 2022.5.1
import copy
import datetime
import random
import sys
import functools

global number_of_probs
global num_of_runs
num_of_runs = 1
global shaking_num
shaking_num = 30
global local_neighbor_num
local_neighbor_num = 300
global total_cost_time
total_cost_time = 0
global average_bin_gaps
average_bin_gaps = 0


class Item:
    def __init__(self, index: int, volume: int):
        self.index = index
        self.volume = volume


class Bin:
    cap_left = 0

    def __init__(self, cap_left: int):
        self.cap_left = cap_left

    items = [Item]


class Problem:
    def __init__(self, name, number_of_item, cap_of_bin, best_known_solution):
        self.name = name
        self.number_of_item = number_of_item
        self.cap_of_bin = cap_of_bin
        self.best_known_solution = best_known_solution

    items = [Item]


class Solution:
    def __init__(self, num_of_bins, problem):
        self.problem = problem
        self.num_of_bins = num_of_bins

    bins = [Bin]


best_solution = Solution(0, None)


# evaluate 2 solution, true represent the previous one, otherwise is latter one.
def evaluate_solution(solution1: Solution, solution2: Solution):
    if len(solution1.bins) < len(solution2.bins):
        return True
    if len(solution1.bins) < len(solution2.bins):
        return False
    # Compare the two solutions and choose the one with more full boxes
    else:
        solu1_full_bin = 0
        solu2_full_bin = 0
        for one_bin in solution1.bins:
            if one_bin.cap_left == 0:
                solu1_full_bin += 1
        for one_bin in solution2.bins:
            if one_bin.cap_left == 0:
                solu2_full_bin += 1
    return solu1_full_bin > solu2_full_bin


def load_problems(data):
    fp = open(data)
    global number_of_probs
    number_of_probs = fp.readline()
    number_of_probs = int(number_of_probs)
    problems = []

    for problem in range(0, number_of_probs):
        items = []
        instance_name = fp.readline().split()[0]
        temp_str = fp.readline().split()
        bin_cap = int(temp_str[0])
        num_of_item = int(temp_str[1])
        obj_opt = int(temp_str[2])
        new_prob = Problem(name=instance_name, number_of_item=num_of_item, cap_of_bin=bin_cap,
                           best_known_solution=obj_opt)
        for j in range(0, num_of_item):
            item_volume = fp.readline()
            item_volume = int(item_volume)
            items.append(Item(j, item_volume))
        new_prob.items = items
        problems.append(new_prob)
    fp.close()
    return problems


# 打印一个solution
def out_put_solution(dest_file):
    fp = open(dest_file, 'a')
    # write name of problem
    fp.write(best_solution.problem.name)
    fp.write('\n')
    fp.write(' obj=   ')
    fp.write(str(best_solution.num_of_bins))
    fp.write('   ')

    fp.write(str(best_solution.num_of_bins - best_solution.problem.best_known_solution))
    global average_bin_gaps
    average_bin_gaps += best_solution.num_of_bins - best_solution.problem.best_known_solution
    fp.write('\n')
    for box in best_solution.bins:
        for item in box.items:
            fp.write(str(item.index))
            fp.write(" ")
        fp.write('\n')


# sort by descending
def cmp1(a: Item, b: Item):
    if a.volume > b.volume:
        return 1
    elif a.volume < b.volume:
        return -1
    else:
        return 0


# sort by ascending
def cmp2(a: Item, b: Item):
    if a.volume < b.volume:
        return 1
    elif a.volume > b.volume:
        return -1
    else:
        return 0


# always find the largest items for packing
def greedy_search(prob):
    sln = Solution(0, copy.deepcopy(prob))
    bins = []
    while len(sln.problem.items) > 0:
        items = []
        cap_left = sln.problem.cap_of_bin
        # find the largest item
        sln.problem.items.sort(key=functools.cmp_to_key(cmp2))
        items.append(sln.problem.items[0])
        cap_left -= sln.problem.items[0].volume
        sln.problem.items.pop(0)

        # sort the items by descending
        sln.problem.items.sort(key=functools.cmp_to_key(cmp1))

        while len(sln.problem.items) > 0 and sln.problem.items[0].volume <= cap_left:
            # sort by ascending
            sln.problem.items.sort(key=functools.cmp_to_key(cmp2))
            for it in sln.problem.items:
                if it.volume <= cap_left:
                    items.append((it))
                    cap_left -= it.volume
                    sln.problem.items.remove(it)
            # sort the items by descending
            sln.problem.items.sort(key=functools.cmp_to_key(cmp1))
        new_bin = Bin(cap_left)
        new_bin.items = items
        bins.append(new_bin)
        sln.num_of_bins += 1
    sln.bins = bins
    return sln


# generate an index by weighted probablity
def rate_random(data_list, rate_list):
    if len(data_list) != len(rate_list):
        print("length of 2 list is not equal")
        return -1
    else:
        start = 0
        idx = 0
        ran_num = random.random()
        for idx, score in enumerate(rate_list):
            start += score
            if ran_num <= start:
                break
        return data_list[idx]


# return the most satisified item list
def most_satisfied_items(item_list, target: int):
    my_dict = {}
    count = 1
    lapse = target
    for item in item_list:
        # Calculate the deviation, if less than or equal to the current deviation,
        # put the item into the HashMap, and update the deviation
        sum_of_volume = item.volume
        offset = target - sum_of_volume
        if 0 <= offset <= lapse:
            lapse = offset
            my_dict[lapse] = [item]
        temp_list = [item]
        for index in range(count, len(item_list)):
            sum_of_volume += item_list[index].volume
            temp_list.append(item_list[index])
            offset = target - sum_of_volume
            if 0 <= offset <= lapse:
                lapse = offset
                value_list = []
                for it in temp_list:
                    value_list.append(it)
                    # select the longer list
                if (lapse in my_dict.keys()) and (len(value_list) > len(my_dict[lapse])):
                    my_dict[lapse] = value_list
                elif lapse not in my_dict.keys():
                    my_dict[lapse] = value_list
        count += 1
    return my_dict[lapse]


def randomBin_reshuffle(solution, times: int):
    # copy solution
    current_sln = Solution(num_of_bins=solution.num_of_bins, problem=solution.problem)
    temp_bins = []
    for b in solution.bins:
        temp_bins.append(b)
    current_sln.bins = temp_bins
    neighbor_solution = []
    # generate the neighbourhoods
    for i in range(0, times):
        total_left = 0
        index_list = []
        rate_list = []
        ind = 0
        for a_bin in current_sln.bins:
            # get all left capacity
            total_left += a_bin.cap_left
            index_list.append(ind)
            ind += 1
            # obtain the rate of each index value
        for a_bin in current_sln.bins:
            rate_list.append((a_bin.cap_left / total_left))
        while True:
            rand1 = rate_random(index_list, rate_list)
            rand2 = rate_random(index_list, rate_list)
            if rand2 != rand1:
                break
        # Select two random bins, the probability of selection is proportional to the remaining capacity
        selected_bin1 = current_sln.bins[rand1]
        selected_bin2 = current_sln.bins[rand2]
        # remove 2 bins
        current_sln.bins.remove(selected_bin1)
        current_sln.bins.remove(selected_bin2)

        current_sln.num_of_bins -= 2
        # Remove these two bins from the solution
        item_list = []

        # Optimise space from the two chosen
        for item in selected_bin1.items:
            item_list.append(item)
        for item in selected_bin2.items:
            item_list.append(item)
        target = current_sln.problem.cap_of_bin
        best_item_list = most_satisfied_items(item_list, target)
        # Box the best results into a solution
        for it in best_item_list:
            target -= it.volume
        new_bin1 = Bin(cap_left=target)
        new_bin1.items = best_item_list
        current_sln.bins.append(new_bin1)
        current_sln.num_of_bins += 1
        # Create a second bins
        if len(best_item_list) < len(item_list):
            target = current_sln.problem.cap_of_bin
            # Removal of boxed items
            for it in best_item_list:
                item_list.remove(it)
            # Calculate the remaining capacity of the box
            for itt in item_list:
                target -= itt.volume
            new_bin2 = Bin(cap_left=target)
            new_bin2.items = item_list
            current_sln.bins.append(new_bin2)
            current_sln.num_of_bins += 1

        new_bins = []
        for b in current_sln.bins:
            temp_items = []
            for item in b.items:
                temp_items.append(Item(index=item.index, volume=item.volume))
            new_bin = Bin(cap_left=b.cap_left)
            new_bin.items = temp_items
            new_bins.append(new_bin)
        neibor_sln = Solution(num_of_bins=current_sln.num_of_bins, problem=current_sln.problem)
        neibor_sln.bins = new_bins

        neighbor_solution.append(neibor_sln)
    return neighbor_solution


# swap 2 items in 2 diffenent bins randomly
def largestBin_largestItem(solution, times: int):
    neighbor_solutions = []
    current_sln = copy.deepcopy(solution)
    # generate the neighbourhoods：
    nei_iter = 0
    while nei_iter < times:
        max_left_bin = current_sln.bins[0]
        num_of_rest_bin = 0
        # find the largest residual capacity bin
        for b in current_sln.bins:
            if max_left_bin.cap_left <= b.cap_left:
                max_left_bin = b
            if b.cap_left > 0:
                num_of_rest_bin += 1
        # select a bin that residual capacity greater than 0
        if num_of_rest_bin > 0:
            while True:
                rand_bin = current_sln.bins[random.randint(0, len(current_sln.bins) - 1)]
                if rand_bin.cap_left > 0:
                    break
            # swap the bin1' s largest item with bin2's item or items
            max_item = max_left_bin.items[0]
            for item in max_left_bin.items:
                if item.volume > max_item.volume:
                    max_item = item
            exchange_list = []
            judge_cap = max_item.volume
            for item in rand_bin.items:
                if item.volume <= judge_cap:
                    exchange_list.append(item)
                    judge_cap -= item.volume

            if len(exchange_list) == 0:
                nei_iter += 1
                continue
            else:
                exchange_sum = 0
                for it in exchange_list:
                    exchange_sum += it.volume
                # calculate the feasibility
                rand_cap = rand_bin.cap_left + exchange_sum
                rand_cap -= max_item.volume

                max_cap = max_left_bin.cap_left + max_item.volume
                max_cap -= exchange_sum
                # the feasibility is false
                if rand_cap < 0 or max_cap < 0:
                    nei_iter += 1
                    continue
                # swap operation
                rand_bin.cap_left = rand_cap
                max_left_bin.cap_left = max_cap
                rand_bin.items.append(max_item)
                max_left_bin.items.remove(max_item)
                for item in exchange_list:
                    max_left_bin.items.append(item)
                    rand_bin.items.remove(item)
                neighbor_solutions.append(copy.deepcopy(current_sln))
        nei_iter += 1
    if len(neighbor_solutions) < times:
        for count in range(0, times - len(neighbor_solutions)):
            # swap the item randomly
            while True:
                rand_inx1 = random.randint(0, len(current_sln.bins) - 1)
                rand_inx2 = random.randint(0, len(current_sln.bins) - 1)
                if rand_inx1 != rand_inx2:
                    break
            rand_bin1 = current_sln.bins[rand_inx1]
            rand_bin2 = current_sln.bins[rand_inx2]
            current_sln.bins.remove(rand_bin1)
            current_sln.bins.remove(rand_bin2)
            current_sln.num_of_bins -= 2

            item_list = []
            item_list.extend(rand_bin1.items)
            item_list.extend(rand_bin2.items)
            target = current_sln.problem.cap_of_bin
            best_item_list = most_satisfied_items(item_list, target)
            for it in best_item_list:
                target -= it.volume
            new_bin1 = Bin(cap_left=target)
            new_bin1.items = best_item_list
            current_sln.bins.append(new_bin1)
            current_sln.num_of_bins += 1
            # create another bin
            if len(best_item_list) < len(item_list):
                target = current_sln.problem.cap_of_bin
                # remove the packed item
                for it in best_item_list:
                    item_list.remove(it)
                # calculate the residual capacity of bin
                for itt in item_list:
                    target -= itt.volume
                new_bin2 = Bin(cap_left=target)
                new_bin2.items = item_list
                current_sln.bins.append(new_bin2)
                current_sln.num_of_bins += 1
            neighbor_solutions.append(copy.deepcopy(current_sln))
    return neighbor_solutions


# VNS to solve BPP problem
# parameter maxtime is the limitation of the maxmium running time
def variable_neighbourhood_search(maxtime):
    global best_solution
    current_sln = best_solution
    total_time = 0
    while total_time < maxtime:

        start = datetime.datetime.now()
        # shaking solution
        shaking_neighbor = largestBin_largestItem(current_sln, shaking_num)
        k = 1
        l = 1
        while k < shaking_num:
            s = random.randint(0, shaking_num - 1)
            shake_sln = shaking_neighbor[s]
            while l < local_neighbor_num:
                # get the neighbour of shake solution，which is the local neighbour
                local_neighbor = randomBin_reshuffle(shake_sln, local_neighbor_num)
                # find the best neighbour of shake solution
                for sl in local_neighbor:
                    # Compare two solutions
                    if evaluate_solution(sl, shake_sln):
                        shake_sln = sl
                        l = 1
                    else:
                        l += 1
            if evaluate_solution(shake_sln, current_sln):
                current_sln = shake_sln
                k = 1
            else:
                k += 1
        if evaluate_solution(current_sln, best_solution):
            best_solution = current_sln
        end = datetime.datetime.now()
        time_spent = (end - start).microseconds

        total_time += time_spent
        # save time
        if best_solution.num_of_bins - best_solution.problem.best_known_solution <= 0:
            print(best_solution.problem.name, " has been solved, costed ", total_time // 1000000, "seconds")
            break
        if total_time + time_spent > maxtime:
            print(best_solution.problem.name, " has been solved, costed ", total_time // 1000000, "seconds")
            break
    global total_cost_time
    total_cost_time += total_time


if __name__ == '__main__':
    print('start running...')
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
        # init the solution by greedy search
        best_solution = greedy_search(my_problems[i])
        for run in range(0, num_of_runs):
            variable_neighbourhood_search(int(max_time) * 1000000)
            out_put_solution(solution_file)
    print("The average absolute gap:", average_bin_gaps / len(my_problems))
    print('spent time = ', total_cost_time / 1000000, ' seconds')
    if total_cost_time > int(max_time) * len(my_problems) * 1000000:
        print("The maximum set time has been exceeded")
