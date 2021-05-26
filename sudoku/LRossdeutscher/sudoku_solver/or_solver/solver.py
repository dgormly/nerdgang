import argparse
import pulp as pl

from typing import Dict, List, Tuple, Optional


THREE = 3
NINE = 9


class SudokuPuzzle:
    def __init__(self, filename: str):
        self._unsolved = self.read_puzzle_file(filename)
        self._solved = self._unsolved
        self._filename = filename

    def read_puzzle_file(self, filename: str) -> List[List[int]]:
        unsolved_puzzle: List[List[int]] = []
        with open(filename, "r") as p:
            for row in p:
                if len(row.strip()) != NINE:
                    raise Exception(f"Invalid puzzle: row length not {NINE}.")
                unsolved_puzzle.append([int(x) for x in row.strip()])
        if len(unsolved_puzzle) != NINE:
            raise Exception(f"Invalid puzzle: number of rows not {NINE}.")
        return unsolved_puzzle

    def get_unsolved_puzzle(self) -> List[List[int]]:
        return self._unsolved

    def get_solved_puzzle(self) -> List[List[int]]:
        return self._solved

    def get_filename(self) -> str:
        return self._filename

    def print_solved_puzzle(self) -> None:
        for row in range(NINE):
            print("--" * NINE, end="-\n")
            print("|", end="")
            for col in range(NINE):
                print(self._solved[row][col], end="|")
            print()
        print("--" * NINE, end="-\n")


class SudokuSolver:
    def __init__(self):
        self._problem = pl.LpProblem("Sudoku Puzzle")
        self._variables = self._create_variables()
        self._create_constraints()
        self._puzzle = None

    def _create_variables(self) -> Dict[Tuple[int, int], List[pl.LpVariable]]:
        variables: Dict[Tuple[int, int], List[pl.LpVariable]] = {}
        for x in range(NINE):
            for y in range(NINE):
                variables[(x, y)] = []
                for value in range(1, 10):
                    variables[(x, y)].append(
                        pl.LpVariable(f"cell({x},{y})_is_{value}", cat=pl.LpBinary)
                    )
        return variables

    def _create_constraints(self) -> None:
        # Constraint 1: only one value per cell
        for x in range(NINE):
            for y in range(NINE):
                self._problem += (
                    pl.lpSum(self._variables[(x, y)]) == 1,
                    f"Only one value per cell:({x},{y}).",
                )

        # Constraint 2: Row and Column constraints
        for x in range(NINE):
            for value_index in range(NINE):
                # only one of each number in Set[1,9] for each row
                self._problem += (
                    pl.lpSum(
                        [self._variables[(x, y)][value_index] for y in range(NINE)]
                    )
                    == 1,
                    f"Max one ({value_index+1}) for row:{x}.",
                )
                # only one of each number in Set[1,9] for each column
                self._problem += (
                    pl.lpSum(
                        [self._variables[(y, x)][value_index] for y in range(NINE)]
                    )
                    == 1,
                    f"Max one ({value_index+1}) for column:{x}.",
                )

        # Constraint 3: only one of each number in Set[1,9] for each 3x3 sub-grid
        for i in range(THREE):
            for j in range(THREE):
                for value_index in range(NINE):
                    self._problem += (
                        pl.lpSum(
                            [
                                self._variables[(sub_i + i * 3, sub_j + j * 3)][
                                    value_index
                                ]
                                for sub_i in range(THREE)
                                for sub_j in range(THREE)
                            ]
                        )
                        == 1,
                        f"Max one ({value_index+1}) for subgrid:({i},{j}).",
                    )

    def get_puzzle(self) -> Optional[SudokuPuzzle]:
        return self._puzzle

    def init_problem(self, puzzle: SudokuPuzzle) -> None:
        self._puzzle = puzzle
        unsolved_puzzle = self._puzzle.get_unsolved_puzzle()

        for x in range(NINE):
            for y in range(NINE):
                if unsolved_puzzle[x][y] != 0:
                    for value_index in range(NINE):
                        # set initial value of variable
                        self._variables[(x, y)][value_index].setInitialValue(
                            int(value_index + 1 == unsolved_puzzle[x][y])
                        )
                        # lock in this values
                        self._variables[(x, y)][value_index].fixValue()

    def solve_problem(self) -> None:
        if self._puzzle:
            filename = self._puzzle.get_filename().split(".")[0]
            print(filename)
            self._problem.writeLP(f"{filename}.lp")
            self._problem.solve()
            self.unpack_solution()

    def unpack_solution(self) -> None:
        # unpack the variable values after solve and interpret the solution
        solved_puzzle = self._puzzle.get_unsolved_puzzle()
        for i in range(NINE):
            for j in range(NINE):
                for k in range(NINE):
                    if pl.value(self._variables[(i, j)][k]) == 1:
                        solved_puzzle[i][j] = k + 1
        self._puzzle.solved = solved_puzzle


class ProgramArgs:
    pass


def main(filename) -> None:
    puzzle = SudokuPuzzle(filename)

    solver = SudokuSolver()
    solver.init_problem(puzzle)
    solver.solve_problem()

    solver.get_puzzle().print_solved_puzzle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LPSolver for Sudoku puzzles")
    parser.add_argument(
        "puzzle_file", metavar="p", type=str, nargs=1, help="path to puzzle_file.txt"
    )
    args = parser.parse_args(namespace=ProgramArgs)

    main(ProgramArgs.puzzle_file[0])
