import pygame as pgm
import sys
import random
import time
import numpy as np
import copy

gridTest = None

class Game15:
    render = False
    #optimalGrid = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,None]]

    def __init__(self, grid_size=3, tile_size=150, gamegrid=gridTest):
        pgm.init()

        self.gamegrid_str = grid_size
        self.tile_str = tile_size
        self.gamegrid = gamegrid

        if self.gamegrid == None:
            #print("No Preset")
            self.reset()
        #else:
            #print("Preset is:", self.gamegrid)
        self.aktiv = True
        self.gamesolve = False
        self.optimalGrid = self.gridSolution(grid_size)

    def gridSolution(self, grid_size):
        grid = []
        c = 1
        for i in range(grid_size):
            row = []

            for j in range(grid_size):
                row.append(c)
                c += 1
            grid.append(row)
        
        grid[len(grid)-1][len(grid)-1] = None

        return grid
            




    def tile_ryk(self, row, column):
        if row < 0 or row >= self.gamegrid_str or column < 0 or column >= self.gamegrid_str:
            return False

        for ab, ac in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            a, b = row + ab, column + ac
            if 0 <= a < self.gamegrid_str and 0 <= b < self.gamegrid_str and self.gamegrid[a][b] is None:
                self.gamegrid[a][b], self.gamegrid[row][column] = self.gamegrid[row][column], self.gamegrid[a][b]
                return True
        return False

    def solve(self):
        return self.gamegrid[0][:3] == [1, 2, 3]
        #return all(self.gamegrid[a][b] == (b + a * self.gamegrid_str) + 1 or (a, b) == (self.gamegrid_str - 1, self.gamegrid_str - 1)
        #          for a in range(self.gamegrid_str) for b in range(self.gamegrid_str))

    def mix(self):
        #print("mix")
        for x in range(10000):
            empty_row, empty_column = [(a, b) for a in range(self.gamegrid_str) for b in range(self.gamegrid_str) if
                                        self.gamegrid[a][b] is None][0]
            vej = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            if 0 <= empty_row + vej[0] < self.gamegrid_str and 0 <= empty_column + vej[1] < self.gamegrid_str:
                self.tile_ryk(empty_row + vej[0], empty_column + vej[1])
        
        if self.solve():
            print("MIX ERROR")
            self.reset()

    def reset(self):
        self.gamegrid = [[(b + a * self.gamegrid_str) + 1 for b in range(self.gamegrid_str)] for a in range(self.gamegrid_str)]
        self.gamegrid[self.gamegrid_str - 1][self.gamegrid_str - 1] = None
        self.mix()

    def display(self):
        score = self.get_game_state()[1]
        for a in range(self.gamegrid_str):
            for b in range(self.gamegrid_str):
                if self.gamegrid[a][b]:
                    pos = (self.gamegrid[a][b] == (b + a * self.gamegrid_str) + 1)
                    tile_col = (255, 165, 0) if pos else (127, 255, 212)

                    pgm.draw.rect(self.screen, tile_col, (b * self.tile_str, a * self.tile_str, self.tile_str, self.tile_str))
                    font = pgm.font.Font(None, 36)
                    text = font.render(str(self.gamegrid[a][b]), True, (0, 0, 0))
                    self.screen.blit(text, (b * self.tile_str + 40, a * self.tile_str + 40))

        score_font = pgm.font.Font(None, 36)
        score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 460))
    
    def rendering(self):
        if not self.render:
            self.init_render()

        self.clock.tick(30)
        self.screen.fill((0, 0, 0))
        self.display()
        pgm.display.flip()

    def init_render(self):
        self.screen = pgm.display.set_mode((500, 500))
        pgm.display.set_caption("The 8 Puzzle - Press 'r' to solve ")
        self.background = pgm.Surface(self.screen.get_size())
        self.render = True
        self.clock = pgm.time.Clock()

    def complete(self):
        self.gamegrid = [[(b + a * self.gamegrid_str) + 1 for b in range(self.gamegrid_str)] for a in range(self.gamegrid_str)]
        self.gamegrid[self.gamegrid_str - 1][self.gamegrid_str - 1] = None

    def close(self):
        pgm.quit()

    def get_coordinates(self, node, grid):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] == node:
                    return x + 1, y + 1
    
    def manhattanDistance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x2 - x1) + abs(y2 - y1)
    
    def distancesScore(self, grid):
        distances = {}

        for y in range(len(grid)):
            for x in range(len(grid[y])):
                node = grid[y][x]
                original_position = self.get_coordinates(node, self.optimalGrid)
                current_position = (x + 1, y + 1)
                distance = self.manhattanDistance(original_position, current_position)
                distances[node] = distance

        return distances

    def get_game_state(self):
        state = []
        score = 0
        possible_actions = []

        empty_row, empty_column = None, None
        for a in range(self.gamegrid_str):
            row = []
            for b in range(self.gamegrid_str):
                tile = self.gamegrid[a][b]
                row.append(tile)
                if tile is None:
                    empty_row, empty_column = a, b


            state.append(row)

        if state[0] == [1, 2, 3]:
            score += 100
        
        
        if state[0] == [1, 2, 3] and state[1] == [4, 5, 6] and state[2] == [7, 8, None]:
            score += 1000

        mScores = self.distancesScore(state)
        for node in mScores:
            if node is None:
                continue
            
            score -= (mScores[node] **2)

        if empty_row > 0:
            possible_actions.append('down')
        if empty_row < self.gamegrid_str - 1:
            possible_actions.append('up')
        if empty_column > 0:
            possible_actions.append('right')
        if empty_column < self.gamegrid_str - 1:
            possible_actions.append('left')

        return state, score, possible_actions



    def move_empty_tile(self, direction):

        empty_row, empty_column = [(a, b) for a in range(self.gamegrid_str) for b in range(self.gamegrid_str) if self.gamegrid[a][b] is None][0]
        if direction == 'up' and empty_row < self.gamegrid_str - 1:
            self.tile_ryk(empty_row + 1, empty_column)
        elif direction == 'down' and empty_row > 0:
            self.tile_ryk(empty_row - 1, empty_column)
        elif direction == 'left' and empty_column < self.gamegrid_str - 1:
            self.tile_ryk(empty_row, empty_column + 1)
        elif direction == 'right' and empty_column > 0:
            self.tile_ryk(empty_row, empty_column - 1)


