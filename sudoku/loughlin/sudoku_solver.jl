# Helper only for checking solutions.
function section_correct(collection)
    if length(collection) != 9
        return false
    end
    for n in  1:9
        if !(n in collection)
            return false
        end
    end
    return true
end

# Helper for checking a puzzle solution.
function check_solution(G)
    # check each row
    for rowi ∈ 1:9
        if !section_correct(G[rowi, :])
            println("Incorrect row: $rowi")
            return false
        end
    end
    # check each column
    for coli ∈ 1:9
        if !section_correct(G[:, coli])
            println("Incorrect col: $coli")
            return false
        end
    end
    # check each of the sub grids (3 x 3 ones).
    ranges = [1:3, 4:6, 7:9]
    sections = [(rowrange, colrange) for rowrange in ranges for colrange in ranges]
    for (rowrange, colrange) in sections
        if !section_correct(G[rowrange, colrange])
            println("Incorrect section: ($rowrange, $colrange)")
            return false
        end
    end

    return true
end


"""
Read the puzzle from text file `filename` and put each of the numbers into a 9x9 matrix.
All of the empty spaces will be represented by a `0`.
"""
function read_puzzle(filename)
    lines = readlines(filename)
    matrix = zeros(Int, length(lines), length(lines))
    for (row, line) in enumerate(lines)
        for (col, char) in enumerate(line)
            n = parse(Int, char)
            matrix[row, col] = n
        end
    end
    matrix
end

function sectionrange(index::Int64)::UnitRange{Int64}
    if index <= 3
        1:3
    elseif index <= 6
        4:6
    else
        7:9
    end
end

"""
Work out what numbers could be substituted into position `(rowi, coli)`
in the grid.

If there is already a number (non zero) there, then it is the only option -
i.e. it has been specified in the puzzle.
"""
function calc_options(G, rowi, coli)::Vector{Int64}
    current = G[rowi, coli]
    if current == 0
        section = G[sectionrange(rowi), sectionrange(coli)]
        setdiff(1:9, G[rowi, :], G[:, coli], section)
    else
        return [current]
    end
end

"""
Given puzzle `G`, try to find solutions from position `(rowi, coli)`.
Any position that comes before `(rowi, coli)` is assumed to already have a potential solution / number
already inserted.

Once a potential solution for the position `(rowi, coli)` has been inserted,
the function recursively calls into itself to check if a solution for the whole thing can be found.
Basically a DFS for solutions.

If a solution was not found, then the position `(rowi, coli)` is reset to its orginal value
so that new solution spaces can be explored.

Return `true` if a solution has been found so search can be short circuited, else `false`.
"""
function solve_from!(G::Matrix{Int64}, rowi::Int64, coli::Int64) :: Bool
    original = G[rowi, coli]
    options = calc_options(G, rowi, coli)
    # Now, let's try each of these options.
    # Keep in mind that if we are currently at (9, 9) AND we have a valid option:
    # then we have solved the puzzle.
    for opt in options
        G[rowi, coli] = opt
        if (rowi, coli) == (9, 9)
            return true
        end
        rowi₂, coli₂ = if coli == 9
            (rowi + 1, 1)
        else
            (rowi, coli + 1)
        end
        solved = solve_from!(G, rowi₂, coli₂)
        if solved
            return true
        end
    end
    G[rowi, coli] = original

    return false
end

function solve(puzzle)
    G = copy(puzzle)
    solved = solve_from!(G, 1, 1)
    return solved, G
end

function main()
    if length(ARGS) < 1
        println("ERROR: No problem filename passed as command line arg")
        println("Usage: julia sudoku_solver.jl <problem_filename>")
        return
    end

    filename = ARGS[1]
    println("Going to try and solve: $filename")
    println("This will return/print the first found solution to the puzzle.")
    println()

    puzzle = read_puzzle(filename)
    solved, soln = solve(puzzle)

    display(soln)
    println()
    println("Solved? $solved")
    check_passed = check_solution(soln)
    println("Solution double check passed? $check_passed")
end

main()
