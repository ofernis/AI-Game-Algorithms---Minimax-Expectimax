import random

import numpy as np

import Gobblet_Gobblers_Env as gge

import time

not_on_board = np.array([-1, -1])

time_safety_delay = 5


# agent_id is which player I am, 0 - for the first player , 1 - if second player
def dumb_heuristic1(state, agent_id):
    is_final = gge.is_final_state(state)
    # this means it is not a final state
    if is_final is None:
        return 0
    # this means it's a tie
    if is_final is 0:
        return -1
    # now convert to our numbers the win
    winner = int(is_final) - 1
    # now winner is 0 if first player won and 1 if second player won
    # and remember that agent_id is 0 if we are first player  and 1 if we are second player won
    if winner == agent_id:
        # if we won
        return 1
    else:
        # if other player won
        return -1


# checks if a pawn is under another pawn
def is_hidden(state, agent_id, pawn):
    pawn_location = gge.find_curr_location(state, pawn, agent_id)
    for key, value in state.player1_pawns.items():
        if np.array_equal(value[0], pawn_location) and gge.size_cmp(value[1], state.player1_pawns[pawn][1]) == 1:
            return True
    for key, value in state.player2_pawns.items():
        if np.array_equal(value[0], pawn_location) and gge.size_cmp(value[1], state.player1_pawns[pawn][1]) == 1:
            return True
    return False


# count the numbers of pawns that i have that aren't hidden
def dumb_heuristic2(state, agent_id):
    sum_pawns = 0
    if agent_id == 0:
        for key, value in state.player1_pawns.items():
            if not np.array_equal(value[0], not_on_board) and not is_hidden(state, agent_id, key):
                sum_pawns += 1
    if agent_id == 1:
        for key, value in state.player2_pawns.items():
            if not np.array_equal(value[0], not_on_board) and not is_hidden(state, agent_id, key):
                sum_pawns += 1

    return sum_pawns



def win_lose(state, agent_id):
    final = gge.is_final_state(state)
    sum_heu = 0
    if final is not None:
        if int(final) == 0:
            sum_heu = -50
        if int(final) == int(agent_id) + 1:
            sum_heu = 1000
        if int(final) == (1 - int(agent_id)) + 1:
            sum_heu = -1000
        return sum_heu
    return 0


def num_of_two_self_pawns_in_row_col_diag(state, agent_id):
    counter = 0
    arr = gge.pawn_list_to_marks_array(state)
    agent_id = str(agent_id + 1)
    # check rows
    for i in range(3):
        if (arr[i][0] == agent_id and (arr[i][0] == arr[i][1] or arr[i][0] == arr[i][2])) or\
                (arr[i][1] == agent_id and arr[i][1] == arr[i][2]):
            counter += 1
    # check columns
    for i in range(3):
        if (arr[0][i] == agent_id and (arr[0][i] == arr[1][i] or arr[0][i] == arr[2][i])) or \
                (arr[1][i] == agent_id and arr[1][i] == arr[2][i]):
            counter += 1
    # check obliques
    if (arr[0][0] == agent_id and ([0][0] == arr[1][1] or arr[2][2] == arr[1][1])) or\
            (arr[1][1] == agent_id and arr[1][1] == arr[2][2]):
        counter += 1

    if arr[0][2] == (agent_id and (arr[0][2] == arr[1][1] or arr[2][0] == arr[2][0])) or \
            (arr[1][1] == agent_id and arr[1][1] == arr[2][0]):
        counter += 1
    return counter


def smart_heuristic(state, agent_id):
    if gge.is_final_state(state) is not None:
        return win_lose(state, agent_id)
    return (dumb_heuristic2(state, agent_id) - dumb_heuristic2(state, 1 - agent_id)) + \
        num_of_two_self_pawns_in_row_col_diag(state, agent_id) - num_of_two_self_pawns_in_row_col_diag(state, 1 - agent_id)



# IMPLEMENTED FOR YOU - NO NEED TO CHANGE
def human_agent(curr_state, agent_id, time_limit):
    print("insert action")
    pawn = str(input("insert pawn: "))
    if pawn.__len__() != 2:
        print("invalid input")
        return None
    location = str(input("insert location: "))
    if location.__len__() != 1:
        print("invalid input")
        return None
    return pawn, location


# agent_id is which agent you are - first player or second player
def random_agent(curr_state, agent_id, time_limit):
    neighbor_list = curr_state.get_neighbors()
    rnd = random.randint(0, neighbor_list.__len__() - 1)
    return neighbor_list[rnd][0]


# TODO - instead of action to return check how to raise not_implemented
def greedy(curr_state, agent_id, time_limit):
    neighbor_list = curr_state.get_neighbors()
    max_heuristic = 0
    max_neighbor = None
    for neighbor in neighbor_list:
        curr_heuristic = dumb_heuristic2(neighbor[1], agent_id)
        if curr_heuristic >= max_heuristic:
            max_heuristic = curr_heuristic
            max_neighbor = neighbor
    return max_neighbor[0]


# TODO - add your code here
def greedy_improved(curr_state, agent_id, time_limit):
    neighbor_list = curr_state.get_neighbors()
    max_heuristic = float('-inf')
    max_neighbor = None
    for neighbor in neighbor_list:
        curr_heuristic = smart_heuristic(neighbor[1], agent_id)
        if curr_heuristic >= max_heuristic:
            max_heuristic = curr_heuristic
            max_neighbor = neighbor
    return max_neighbor[0]


def rb_heuristic_min_max_d(time_limit, start_time, curr_state, agent_id, d, action=None):
    if time.time() - start_time > time_limit - time_safety_delay:
        return (None, None, True)
    elif gge.is_final_state(curr_state) or (d == 0):
        return (action, smart_heuristic(curr_state, agent_id) + d, False)
    turn = curr_state.turn
    children = curr_state.get_neighbors()
    if turn == agent_id:
        max_action = None
        cur_max = float('-inf')
        for c in children:
            v = rb_heuristic_min_max_d(time_limit, start_time, c[1], agent_id, d-1, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if v[1] > cur_max:
                cur_max = v[1]
                max_action = c[0]
        return (max_action, cur_max, False)
    elif turn == 1 - agent_id:
        min_action = None
        cur_min = float('inf')
        for c in children:
            v = rb_heuristic_min_max_d(time_limit, start_time, c[1], agent_id, d - 1, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if v[1] < cur_min:
                cur_min = v[1]
                min_action = c[0]
        return (min_action, cur_min, False)


def rb_heuristic_min_max(curr_state, agent_id, time_limit):
    start_time = time.time()
    depth = 1
    current_sol = None

    while True:
        prev_sol = rb_heuristic_min_max_d(time_limit, start_time, curr_state, agent_id, depth)
        is_time_ended = prev_sol[2]
        if is_time_ended:
            break
        current_sol = prev_sol[0]
        depth += 1
    return current_sol


def alpha_beta_d(time_limit, start_time, curr_state, agent_id, d,alpha,beta,action=None):
    if time.time() - start_time > time_limit - time_safety_delay:
        return (None, None, True)
    elif gge.is_final_state(curr_state) or (d == 0):
        return (action, smart_heuristic(curr_state, agent_id) + d, False)
    turn = curr_state.turn
    max_action = None
    children = curr_state.get_neighbors()
    if turn == agent_id:
        cur_max = float('-inf')
        for c in children:
            v = alpha_beta_d(time_limit, start_time, c[1], agent_id, d-1, alpha, beta, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if v[1] > cur_max:
                cur_max = v[1]
                max_action = c[0]
            alpha = max(cur_max, alpha)
            if cur_max >= beta:
                return (max_action, float('inf'), False)
        return (max_action, cur_max, False)
    elif turn == 1 - agent_id:
        min_action = None
        cur_min = float('inf')
        for c in children:
            v = alpha_beta_d(time_limit, start_time, c[1], agent_id, d-1, alpha, beta, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if v[1] < cur_min:
                cur_min = v[1]
                min_action = c[0]
            beta = min(cur_min, beta)
            if cur_min <= alpha:
                return (min_action, float('-inf'), False)
        return (min_action, cur_min, False)


def alpha_beta(curr_state, agent_id, time_limit):
    start_time = time.time()
    depth = 1
    current_sol = None

    while True:
        prev_sol = alpha_beta_d(time_limit, start_time, curr_state, agent_id, depth, float('-inf'), float('inf'))
        is_time_ended = prev_sol[2]
        if is_time_ended:
            break
        current_sol = prev_sol[0]
        depth += 1

    return current_sol


def expectimax_d(time_limit, start_time, curr_state, agent_id, d, action=None):
    if time.time() - start_time > time_limit - time_safety_delay:
        return (None, None, True)
    elif gge.is_final_state(curr_state) or (d == 0):
        return (action, smart_heuristic(curr_state, agent_id) + d, False)

    turn = curr_state.turn
    children = curr_state.get_neighbors()
    if turn == agent_id:
        max_action = None
        cur_max = float('-inf')
        for c in children:
            v = expectimax_d(time_limit, start_time, c[1], agent_id, d-1, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if v[1] > cur_max:
                cur_max = v[1]
                max_action = c[0]
        return (max_action, cur_max, False)

    elif turn == 1 - agent_id:
        exp_sum = 0
        small_action = 0
        eat_action = 0
        min_action = action
        cur_min = float('inf')
        special_child_arr = []
        for i, c in enumerate(children):
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            if c[0][0] == "S1" or c[0][0] == "S2":
                small_action = small_action + 1
                special_child_arr.append(i)
                continue
            for pawn in curr_state.player2_pawns:
                if pawn[1] == c[0][1]:
                    eat_action = eat_action + 1
                    special_child_arr.append(i)
                    break

            for pawn in curr_state.player1_pawns:
                if pawn[1] == c[0][1]:
                    eat_action = eat_action + 1
                    special_child_arr.append(i)
                    break

        special_action = small_action + eat_action
        p = 1 / (2 * special_action + (len(children) - special_action))

        for i, c in enumerate(children):
            _, val,_bool_dummy = expectimax_d(time_limit, start_time, c[1], agent_id, d-1, c[0])
            if time.time() - start_time > time_limit - time_safety_delay:
                return (None, None, True)
            p_factor = 1
            if i in special_child_arr:
                p_factor = 2
            val = val * p_factor * p
            if val < cur_min:
                cur_min = val
                min_action = c[0]
            exp_sum = exp_sum + val
        return (min_action, exp_sum, False)


def expectimax(curr_state, agent_id, time_limit):
    start_time = time.time()
    depth = 1
    current_sol = None

    while True:
        prev_sol = expectimax_d(time_limit, start_time, curr_state, agent_id, depth)
        is_time_ended = prev_sol[2]
        if is_time_ended:
            break
        current_sol = prev_sol[0]
        depth += 1

    return current_sol


# this is the BONUS - not mandatory
def super_agent(curr_state, agent_id, time_limit):
    return alpha_beta(curr_state, agent_id, time_limit)

