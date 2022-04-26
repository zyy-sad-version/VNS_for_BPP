import datetime
import random
import sys
import functools

global number_of_probs
global num_of_runs
num_of_runs = 1
global shaking_num
shaking_num = 10
global local_neighbor_num
local_neighbor_num = 10
global total_time
total_time = 0

# 加权随机选择，若该种邻域算法得到结果优于上一种，加0.01的权重
global neibor_weight_random_list
neibor_weight_random_list = [0.25, 0.25, 0.25, 0.25]
global pre_neibor_method
# 四种寻找邻域的方法
global rand_neighbor
rand_neighbor_seed = [1, 2, 3, 4]


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
    # if solution1.num_of_bins < solution2.num_of_bins:
    #     return True
    if len(solution1.bins) < len(solution2.bins):
        return False
    # if solution1.num_of_bins > solution2.num_of_bins:
    #     return False
    # 对比两个解决办法，选择满箱子多的那个
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

    for i in range(0, number_of_probs):
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
    fp.write('\n')
    for box in best_solution.bins:
        for item in box.items:
            fp.write(str(item.index))
            fp.write(" ")
        fp.write('\n')


def print_solution(solution):
    print('problem name: ', solution.problem.name)
    print('objective :', solution.num_of_bins)
    print('num of bins = ', len(solution.bins))
    gap = solution.num_of_bins - solution.problem.best_known_solution
    print('gaps = ', gap)
    for b in solution.bins:
        print("bin capleft:", b.cap_left)
        item_sum = 0
        for item in b.items:
            item_sum += item.volume
        print("item weight", item_sum)


# 递减排序
def cmp1(a: Item, b: Item):
    if a.volume > b.volume:
        return 1
    elif a.volume < b.volume:
        return -1
    else:
        return 0


# 递增排序
def cmp2(a: Item, b: Item):
    if a.volume < b.volume:
        return 1
    elif a.volume > b.volume:
        return -1
    else:
        return 0


def init_solution(prob):
    sln = Solution(0, prob)
    bins = []
    while len(sln.problem.items) > 0:
        items = []
        cap_left = sln.problem.cap_of_bin
        # 寻找最大值
        sln.problem.items.sort(key=functools.cmp_to_key(cmp2))
        items.append(sln.problem.items[0])
        cap_left -= sln.problem.items[0].volume
        sln.problem.items.pop(0)

        # 按照递减排序
        sln.problem.items.sort(key=functools.cmp_to_key(cmp1))

        while len(sln.problem.items) > 0 and sln.problem.items[0].volume <= cap_left:
            # 递增排序
            sln.problem.items.sort(key=functools.cmp_to_key(cmp2))
            for it in sln.problem.items:
                if it.volume <= cap_left:
                    items.append((it))
                    cap_left -= it.volume
                    sln.problem.items.remove(it)
            # 递减排序
            sln.problem.items.sort(key=functools.cmp_to_key(cmp1))
            # items.append(sln.problem.items[0])
            # cap_left -= sln.problem.items[0].volume
            # sln.problem.items.pop(0)
        new_bin = Bin(cap_left)
        new_bin.items = items
        bins.append(new_bin)
        sln.num_of_bins += 1
    sln.bins = bins
    return sln


# 指定概率随机生成数
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


# 返回最优解的list
def sch_emuration(list, target: int):
    my_dict = {}
    count = 1
    lapse = target
    for item in list:
        # 计算偏差值, 若小于等于当前偏差值，将该item放入hashmap中，并更新偏差值
        # 需要得到最长的
        # 一个item的偏差值
        sum_of_volume = item.volume
        offset = target - sum_of_volume
        if 0 <= offset <= lapse:
            lapse = offset
            my_dict[lapse] = [item]
        temp_list = [item]
        for index in range(count, len(list)):
            sum_of_volume += list[index].volume
            temp_list.append(list[index])
            offset = target - sum_of_volume
            if 0 <= offset <= lapse:
                lapse = offset
                value_list = []
                for it in temp_list:
                    value_list.append(it)
                    # 选择较长的接近目标值的list待定 TODO
                if (lapse in my_dict.keys()) and (len(value_list) > len(my_dict[lapse])):
                    my_dict[lapse] = value_list
                elif lapse not in my_dict.keys():
                    my_dict[lapse] = value_list
        count += 1
    return my_dict[lapse]


def find_neighbour_m1(solution, times: int):
    # copy solution
    current_sln = Solution(num_of_bins=solution.num_of_bins, problem=solution.problem)
    temp_bins = []
    for b in solution.bins:
        temp_bins.append(b)
    current_sln.bins = temp_bins
    neighbor_solution = []
    # 生成邻域值
    for i in range(0, times):
        total_left = 0
        # 用于随机选择
        index_list = []
        rate_list = []
        ind = 0
        for a_bin in current_sln.bins:
            # 获取所有bin的空余值
            total_left += a_bin.cap_left
            index_list.append(ind)
            ind += 1
            # 获取对应的rate
        for a_bin in current_sln.bins:
            rate_list.append((a_bin.cap_left / total_left))
        while True:
            rand1 = rate_random(index_list, rate_list)
            rand2 = rate_random(index_list, rate_list)
            if rand2 != rand1:
                break
        # 选择两个随机的bin， 选择概率与剩余的容量成正比
        selected_bin1 = current_sln.bins[rand1]
        selected_bin2 = current_sln.bins[rand2]
        # 将这两个bin从solution中删除
        current_sln.bins.remove(selected_bin1)
        current_sln.bins.remove(selected_bin2)
        # print(current_sln.bins.pop(rand1))
        # if rand2 > rand1:
        #     current_sln.bins.pop(rand2 - 1)
        # else:
        #     current_sln.bins.pop(rand2)
        current_sln.num_of_bins -= 2
        # 初始化一个用于存放物品的list
        item_list = []

        # # 从被选择的两个中优化空间
        for item in selected_bin1.items:
            item_list.append(item)
        for item in selected_bin2.items:
            item_list.append(item)
        target = current_sln.problem.cap_of_bin
        best_item_list = sch_emuration(item_list, target)
        # print("selected bin1 item length:", len(selected_bin1.items))
        # print("selected bin2 item length:", len(selected_bin2.items))
        # print("original list length: ",len(item_list))
        # print("best item list length:",len(best_item_list))
        # 将最佳结果装箱放入solution
        for it in best_item_list:
            target -= it.volume
        new_bin1 = Bin(cap_left=target)
        new_bin1.items = best_item_list
        current_sln.bins.append(new_bin1)
        current_sln.num_of_bins += 1
        # 创建第二个bins
        if len(best_item_list) < len(item_list):
            target = current_sln.problem.cap_of_bin
            # 将已经装箱的物品移除
            for it in best_item_list:
                item_list.remove(it)
            # 计算箱子剩下容量
            for itt in item_list:
                target -= itt.volume
            new_bin2 = Bin(cap_left=target)
            new_bin2.items = item_list
            current_sln.bins.append(new_bin2)
            current_sln.num_of_bins += 1
        new_bins = []
        for b in current_sln.bins:
            new_bins.append(b)
        neibor_sln = Solution(num_of_bins=current_sln.num_of_bins, problem=current_sln.problem)
        neibor_sln.bins = new_bins
        neighbor_solution.append(neibor_sln)
    return neighbor_solution


# 选择剩余容量最大的 bin中最大的item
def find_neighbour_m2(solution, times: int):
    # copy the solution
    current_sln = Solution(num_of_bins=solution.num_of_bins, problem=solution.problem)
    temp_bins = []
    for b in solution.bins:
        temp_bins.append(b)
    current_sln.bins = temp_bins
    neighbor_solutions = []
    i = 0
    # 生成邻域：
    while i < times:
        max_left_bin = solution.bins[0]
        # 寻找剩余容量最大的bin

        for b in solution.bins:
            if max_left_bin.cap_left < b.cap_left:
                max_left_bin = b
        # 随机选择一个没有满的bin:
        while True:
            rand_bin = solution.bins[random.randint(0, len(solution.bins) - 1)]
            if rand_bin.cap_left > 0:
                break
        # 将剩余容量最大bin中最大的item 与这个随机bin中小于该item的items交换
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
            # 如果未有满足的邻居，则重新寻找
        if len(exchange_list) == 0:
            continue
        else:
            exchange_sum = 0
            for it in exchange_list:
                exchange_sum += it.volume
            # 计算cap是否feasibility
            rand_cap = rand_bin.cap_left + exchange_sum
            rand_cap -= max_item.volume

            max_cap = max_left_bin.cap_left + max_item.volume
            max_cap -= exchange_sum
            # 若不符合cap， 寻找下一个
            if rand_cap < 0 or max_cap < 0:
                continue
            # 交换两个bin中的item
            rand_bin.cap_left = rand_cap
            max_left_bin.cap_left = max_cap
            # 首先移除剩余容量大的bin的item,将其加入random的bin中
            rand_bin.items.append(max_item)
            max_left_bin.items.remove(max_item)
            # 移除随机的bin中的item, 并将其放入max bin中
            for item in exchange_list:
                max_left_bin.items.append(item)
                rand_bin.items.remove(item)
            new_bins = []
            for b in current_sln.bins:
                new_bins.append(b)
            neibor_sln = Solution(current_sln.num_of_bins, current_sln.problem)
            neibor_sln.bins = new_bins
            neighbor_solutions.append(neibor_sln)
            current_sln = neibor_sln
            i = i + 1
    return neighbor_solutions


# Split
def find_neighbour_split(solution):
    current_sln = Solution(num_of_bins=solution.num_of_bins, problem=solution.problem)
    temp_bins = []
    for b in solution.bins:
        temp_bins.append(b)
    current_sln.bins = temp_bins
    # 生成邻居
    # 计算平均每个bin中有几个item
    avg_item = 0
    for b in current_sln.bins:
        avg_item += len(b.items)
        # 计算平均值
    avg_item /= len(current_sln.bins)

    # 若该bin中item个数超过平均值，将其移入一个新的bin中
    for b in current_sln.bins:
        difference = len(b) - avg_item
        if difference > 0:
            # 创建新的Bin，移动一半的item至新的bin
            new_Bin = Bin(current_sln.problem.cap_of_bin)
            new_item_list = []
            for k in range(0, int(len(b) / 2)):
                rand_item = b.items[random.randint(0, len(b) - 1)]
                new_Bin.cap_left -= rand_item.volume
                new_item_list.append(Item(index=rand_item.index, volume=rand_item.volume))
                b.items.remove(rand_item)
            new_Bin.items = new_item_list
            current_sln.bins.append(new_Bin)
    return current_sln


#Shift
# 将剩余容量最大的bin中的所有item使用best desent放入其他bin中
def find_neighbour_shift(solution):
    #copy the solution
    current_sln = Solution(num_of_bins=solution.num_of_bins, problem=solution.problem)
    temp_bins = []
    for b in solution.bins:
        temp_bins.append(b)
    current_sln.bins = temp_bins

    return current_sln


# VNS to solve BPP problem
def variable_neighbourhood_search(problem):
    global best_solution
    start = datetime.datetime.now()
    # initial solution s0
    current_sln = init_solution(problem)
    best_solution = current_sln
    # shaking solution
    shaking_neighbor = find_neighbour_m2(current_sln, shaking_num)
    k = 1
    l = 1
    while k < shaking_num:
        s = random.randint(0, shaking_num - 1)
        shake_sln = shaking_neighbor[s]
        # get the neighbour of shake solution
        local_neighbor = find_neighbour_m2(shake_sln, local_neighbor_num)
        while l < local_neighbor_num:
            # find the best neighbour of shake solution
            for sl in local_neighbor:
                # 比较两个解决办法
                if evaluate_solution(sl, shake_sln):
                    shake_sln = sl
                # if sl.num_of_bins < shake_sln.num_of_bins:
                #     shake_sln = sl
                else:
                    l += 1
                # shake_sln = sl
                # l+=1
        if evaluate_solution(shake_sln, current_sln):
            current_sln = shake_sln
        # if current_sln.num_of_bins > shake_sln.num_of_bins:
        #     current_sln = shake_sln
        else:
            k += 1
        # current_sln = shake_sln
        # k+=1
    # best_bin_num = len(best_solution.bins)
    if evaluate_solution(current_sln, best_solution):
        # if best_bin_num > current_sln.num_of_bins:
        best_solution = current_sln
    best_solution = current_sln
    end = datetime.datetime.now()
    time_spent = (end - start)
    global total_time
    total_time += time_spent.seconds


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
    # print("number of problem:",number_of_probs)
    for i in range(0, number_of_probs):
        for run in range(0, num_of_runs):
            # variable_neighbourhood_search(my_problems[i])
            # out_put_solution(solution_file)
            # 检查邻域方法用
            best_solution = init_solution(my_problems[i])
            solutions = find_neighbour_m2(best_solution, 10)
            for s in solutions:
                print_solution(s)
        # print_solution(best_solution)
        # print_solution(first_fit(my_problems[i]))
        # print_solution(init_solution(my_problems[i]))
        # global best_solution
        # best_solution = init_solution(my_problems[i])
        # out_put_solution(solution_file)
        # print_solution(best_solution)
        # print_solution(best_solution)
    print('spent time = ', total_time)
    if total_time > int(max_time):
        print("The maximum set time has been exceeded")
