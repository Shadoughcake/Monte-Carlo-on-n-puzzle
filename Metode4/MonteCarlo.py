from Game15 import Game15
import numpy as np
import pygame as pgm
import time
import copy
import statistics
import csv

TOTAL_WINS = 612
WIN_TIMES = []
MOVES = 0
SIMMOVES = 0
STUCK = 0
start_time = time.time()
start_time2 = time.time()
action_history = []

env = Game15()
#env.reset()
exit_program = False

def copy_game_state(env):
    new_env = Game15(grid_size=env.gamegrid_str, gamegrid=copy.deepcopy(env.gamegrid))
    return new_env

def simulate_action(env, init_action, max_depth):
    sim = copy_game_state(env)
    action = init_action
    total_score = []
    moves = 0
    for i in range(max_depth):
        sim.move_empty_tile(action)
        game_state, sim_score, possible_actions = sim.get_game_state()
        total_score.append(sim_score)
        moves += 1
        if sim.solve():
            break

        action = np.random.choice(possible_actions)
    
    return max(total_score), moves

while not exit_program:
    while env.aktiv:
        env.rendering()

        for event in pgm.event.get():
            if event.type == pgm.QUIT:
                env.aktiv = False
                exit_program = True

            if env.gamesolve:
                if event.type == pgm.MOUSEBUTTONDOWN:
                    env.reset()
                    env.gamesolve = False
                else:
                    x, y = pgm.mouse.get_pos()
                    column, row = int(x / env.tile_str), int(y / env.tile_str)
                    env.tile_ryk(row, column)

            elif event.type == pgm.KEYDOWN:
                print(env.get_game_state())

                if event.key == pgm.K_r:
                    env.complete()
                    env.gamesolve = True
                    time.sleep(0.05)
                    print("Solved automatically")
                    font = pgm.font.Font(None, 30)
                    text = font.render("Solved automatically by pressing 'r'", True, (127, 255, 212))
                    env.screen.blit(text, (125, 125))

                elif event.key == pgm.K_q:
                    exit_program = True
                    env.aktiv = False
                elif event.key == pgm.K_UP:
                    env.move_empty_tile('down')

                elif event.key == pgm.K_DOWN:
                    env.move_empty_tile('up')

                elif event.key == pgm.K_LEFT:
                    env.move_empty_tile('right')

                elif event.key == pgm.K_RIGHT:
                    env.move_empty_tile('left')

        if env.solve():
            font = pgm.font.Font(None, 30)
            text = font.render("WIN - Click to restart", True, (127, 255, 212))
            env.screen.blit(text, (125, 125))
            pgm.display.flip()
            time.sleep(1)
            TOTAL_WINS += 1

            current_time = time.time()
            win_time = current_time - start_time
            WIN_TIMES.append(win_time)
            print("Total Wins:", TOTAL_WINS ,"Moves:", MOVES, SIMMOVES)

            with open("Gamewin_Data_ModifiedManhattanUnstuck", "a", newline='') as file:
                writer = csv.writer(file, delimiter= ";")
                #writer.writerow(['Game Number', 'Time (seconds)', "Game Moves", "Total Simulation Moves", "Time Stuck"])
                writer.writerow([TOTAL_WINS, win_time, MOVES, SIMMOVES, STUCK])
                file.close()
            
            SIMMOVES = 0
            MOVES = 0
            
            #data = open("data.txt", "a")
            #data.write(str(win_time))
            #data.write("\n")
            #test = open("data.txt", "r")
            #print(data.read())
            #print(int(time.time()-start_time), "seconds")
            #print("You have won a total of:", TOTAL_WINS, "times")
            
            if TOTAL_WINS == 1000:
                end_time = time.time()  # Stop the timer
                time_elapsed = end_time - start_time
                print(f"Time taken to win 1000 games: {time_elapsed:.2f} seconds")

                average_time_per_game = time_elapsed / TOTAL_WINS
                print(f"Average time per game: {average_time_per_game:.2f} seconds")
                
                std_deviation = statistics.stdev(WIN_TIMES)
                print(f"Standard deviation of win times: {std_deviation:.2f} seconds")
                

                exit_program = True
                break
			
			

            
            start_time = time.time()
            env.reset()
            continue


        #Selve monte-carlo
        _, current_score, possible_actions = env.get_game_state()
        R_sims = 1000
        max_depth = 40
        print(current_score)
        #score_list.append(current_score)

        #if len(score_list) >= 8:
        #last_eight = score_list[-8:]
              #  if (last_eight[0] == last_eight[2] == last_eight[4] == last_eight[6] and
               #     last_eight[1] == last_eight[3] == last_eight[5] == last_eight[7] and
                #    last_eight[0] != last_eight[1]):
                 #   R_sims = 25
                  #  max_depth = 130
            

        action_history.append(tuple(possible_actions)) #Start på unstuck-funktionen til når board og algoritme ikke syncer op.
        if len(action_history) >= 8:  #Kigger på de sidste 4 par for at se, om den sidder fast.
            last_eight_actions = action_history[-8:]
            if (last_eight_actions[0] == last_eight_actions[2] == last_eight_actions[4] == last_eight_actions[6] and
                last_eight_actions[1] == last_eight_actions[3] == last_eight_actions[5] == last_eight_actions[7] and
                last_eight_actions[0] != last_eight_actions[1]):
                R_sims = 50 #justerer sims
                R_depth = 40 #juster også depth, for at se om den selv kan løse sig ud af det.

                STUCK += 1 #+1 til stuck, for at tælle.

        if STUCK > 2: #Hvis den bliver ved med at sidde fast pga fejl i sync, så re-setter den boardet. 
            env.reset() #Reset
            STUCK = 0 #Sætter stuck på 0 igen, så den ikke bliver ved med at genstarte boardet.


        scores = {action: 0 for action in possible_actions}
        for init_action in possible_actions:
            scores[init_action] = 0

            for r in range(R_sims):   
                sim_score, moves = simulate_action(env, init_action, max_depth)
                scores[init_action] += sim_score
                SIMMOVES += moves

        best_action = max(scores, key=scores.get)
        #print(scores, best_action)
        env.move_empty_tile(best_action)

        MOVES += 1

        #pgm.display.flip()

env.close()