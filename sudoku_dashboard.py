import streamlit as st
from sudoku_mip_solver import SudokuMIPSolver
import time


def main():
    st.set_page_config(
        page_title="Sudoku Dashboard",
        page_icon="🧩",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🧩 Sudoku Dashboard")
    st.markdown("Generate, manipulate, and solve Sudoku puzzles with customizable parameters")

    with st.expander("🎲 Generate Puzzle"):
        generate_puzzle_page()

    solve_puzzle_page()


def generate_puzzle_page():
    st.header("🎲 Generate Random Puzzle")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Grid Dimensions")
        sub_grid_width = st.number_input(
            "Sub-grid Width", 
            min_value=2, 
            max_value=6, 
            value=3,
            help="Width of each sub-grid (e.g., 3 for standard 9x9 Sudoku)"
        )
        
        sub_grid_height = st.number_input(
            "Sub-grid Height", 
            min_value=2, 
            max_value=6, 
            value=3,
            help="Height of each sub-grid (e.g., 3 for standard 9x9 Sudoku)"
        )
        
        grid_size = sub_grid_width * sub_grid_height
        st.info(f"Grid size: {grid_size}×{grid_size}")
        
        st.subheader("Puzzle Parameters")
        difficulty = st.slider(
            "Difficulty Level",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="0.0 = easiest (more clues), 1.0 = hardest (fewer clues)"
        )
        
        unique_solution = st.checkbox(
            "Ensure Unique Solution",
            value=False,
            help="If checked, ensures the puzzle has exactly one solution"
        )
        
        max_attempts = st.number_input(
            "Max Generation Attempts",
            min_value=10,
            max_value=500,
            value=100,
            help="Maximum attempts to generate a puzzle with the specified difficulty"
        )
        
        random_seed = st.number_input(
            "Random Seed (optional)",
            min_value=0,
            max_value=999999,
            value=None,
            help="Set a seed for reproducible puzzle generation"
        )
        
        if st.button("🎲 Generate Puzzle", type="primary"):
            with st.spinner("Generating puzzle..."):
                try:
                    start_time = time.time()
                    
                    seed_val = random_seed if random_seed is not None else None
                    
                    solver, actual_difficulty = SudokuMIPSolver.generate_random_puzzle(
                        sub_grid_width=sub_grid_width,
                        sub_grid_height=sub_grid_height,
                        target_difficulty=difficulty,
                        unique_solution=unique_solution,
                        max_attempts=max_attempts,
                        random_seed=seed_val
                    )
                    
                    generation_time = time.time() - start_time
                    
                    # Store in session state
                    st.session_state.generated_solver = solver
                    st.session_state.generated_difficulty = actual_difficulty
                    st.session_state.generation_time = generation_time
                    
                    st.success(f"Puzzle generated successfully in {generation_time:.2f} seconds!")
                    st.info(f"Actual difficulty: {actual_difficulty:.3f}")
                    
                except Exception as e:
                    st.error(f"Error generating puzzle: {str(e)}")
    
    with col2:
        if 'generated_solver' in st.session_state:
            st.subheader("Generated Puzzle")
            
            # Display puzzle statistics
            col2a, col2b, col2c = st.columns(3)
            with col2a:
                st.metric("Difficulty", f"{st.session_state.generated_difficulty:.3f}")
            with col2b:
                clues = count_clues(st.session_state.generated_solver.board)
                total_cells = len(st.session_state.generated_solver.board) ** 2
                st.metric("Clues", f"{clues}/{total_cells}")
            with col2c:
                st.metric("Generation Time", f"{st.session_state.generation_time:.2f}s")
            
            # Display the puzzle
            display_sudoku_board(st.session_state.generated_solver.board, "Generated Puzzle", st.session_state.generated_solver)
            
            # Export options
            st.subheader("Export Options")
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                puzzle_string = st.session_state.generated_solver.to_string()
                st.text_area("Puzzle as String", puzzle_string, height=68)
            
            with col_exp2:
                pretty_string = st.session_state.generated_solver.get_pretty_string(st.session_state.generated_solver.board)
                st.download_button(
                    "📥 Download Puzzle",
                    pretty_string,
                    file_name=f"sudoku_puzzle_{int(time.time())}.txt",
                    mime="text/plain"
                )
            
            # Quick solve option
            if st.button("🚀 Solve Generated Puzzle"):
                solve_and_display(st.session_state.generated_solver)


def solve_puzzle_page():
    st.header("🔍 Solve Puzzle")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input Method")
        input_method = st.radio(
            "Choose input method:",
            ["String Input", "File Upload", "Use Generated Puzzle"]
        )
        
        solver = None
        
        if input_method == "String Input":
            st.subheader("Puzzle String")
            puzzle_string = st.text_area(
                "Enter puzzle string",
                placeholder="530070000600195000098000060800060003400803001700020006060000280000419005000080079",
                help="Enter puzzle as a string with 0 for empty cells"
            )
            
            sub_grid_width = st.number_input("Sub-grid Width", min_value=2, max_value=6, value=3, key="solve_width")
            sub_grid_height = st.number_input("Sub-grid Height", min_value=2, max_value=6, value=3, key="solve_height")
            
            if puzzle_string:
                try:
                    solver = SudokuMIPSolver.from_string(
                        puzzle_string.strip(),
                        sub_grid_width=sub_grid_width,
                        sub_grid_height=sub_grid_height
                    )
                except Exception as e:
                    st.error(f"Error parsing puzzle string: {str(e)}")
        
        elif input_method == "File Upload":
            uploaded_file = st.file_uploader("Choose a puzzle file", type=['txt'])
            if uploaded_file is not None:
                content = uploaded_file.read().decode('utf-8')
                sub_grid_width = st.number_input("Sub-grid Width", min_value=2, max_value=6, value=3, key="file_width")
                sub_grid_height = st.number_input("Sub-grid Height", min_value=2, max_value=6, value=3, key="file_height")
                
                try:
                    solver = SudokuMIPSolver.from_string(
                        content.strip(),
                        sub_grid_width=sub_grid_width,
                        sub_grid_height=sub_grid_height
                    )
                except Exception as e:
                    st.error(f"Error parsing file: {str(e)}")
        
        elif input_method == "Use Generated Puzzle":
            if 'generated_solver' in st.session_state:
                solver = st.session_state.generated_solver
                st.success("Using previously generated puzzle")
            else:
                st.warning("No generated puzzle found. Please generate a puzzle first.")
        
        # Solving options
        if solver is not None:
            st.subheader("Solving Options")
            
            # Solution search mode
            search_mode = st.radio(
                "Search Mode:",
                ["Single Solution", "Multiple Solutions"],
                help="Choose whether to find one solution or search for multiple solutions"
            )
            
            if search_mode == "Single Solution":
                show_output = st.checkbox("Show Solver Output", value=False)
                
                if st.button("🔍 Solve Puzzle", type="primary"):
                    solve_puzzle_with_options(solver, 1, show_output)
            
            else:  # Multiple Solutions
                max_solutions = st.number_input(
                    "Maximum Solutions to Find",
                    min_value=1,
                    max_value=100,
                    value=10,
                    help="Limit the search to avoid excessive computation"
                )
                
                show_output = st.checkbox("Show Solver Output", value=False, key="multi_output")
                
                if st.button("🔢 Find Multiple Solutions", type="primary"):
                    find_multiple_solutions(solver, max_solutions)
    
    with col2:
        if 'current_solver' in st.session_state:
            display_puzzle_and_solution()
        elif 'multiple_solutions' in st.session_state:
            display_multiple_solutions()





# Helper functions
def count_clues(board):
    return sum(sum(1 for cell in row if cell != 0) for row in board)


def display_sudoku_board(board, title="Sudoku Board", solver=None):
    st.subheader(title)
    
    # Create a styled display of the Sudoku board
    board_html = create_sudoku_html(board, solver)
    st.markdown(board_html, unsafe_allow_html=True)


def create_sudoku_html(board, solver=None):
    grid_size = len(board)
    
    # Try to get sub-grid dimensions from solver, otherwise use square root approximation
    if solver and hasattr(solver, 'sub_grid_width') and hasattr(solver, 'sub_grid_height'):
        sub_grid_width = solver.sub_grid_width
        sub_grid_height = solver.sub_grid_height
    else:
        sub_grid_width = int(grid_size ** 0.5)
        sub_grid_height = sub_grid_width
    
    # Simple CSS that adapts to Streamlit's theme
    html = """
    <style>
    .sudoku-grid {
        display: inline-block;
        border: 2px solid currentColor;
        font-family: monospace;
        font-size: 16px;
        margin: 10px auto;
    }
    .sudoku-grid td {
        width: 35px;
        height: 35px;
        text-align: center;
        border: 1px solid currentColor;
        opacity: 0.6;
    }
    .sudoku-grid .thick-right { border-right: 2px solid currentColor; }
    .sudoku-grid .thick-bottom { border-bottom: 2px solid currentColor; }
    .sudoku-grid .clue { 
        background: rgba(var(--primary-color-rgb, 255, 75, 75), 0.1);
        font-weight: bold;
        opacity: 1;
    }
    .sudoku-grid .empty { opacity: 0.4; }
    </style>
    <table class="sudoku-grid">
    """
    
    for i, row in enumerate(board):
        html += "<tr>"
        for j, cell in enumerate(row):
            classes = []
            
            # Add thick borders for sub-grid boundaries
            if (j + 1) % sub_grid_width == 0 and j < grid_size - 1:
                classes.append("thick-right")
            if (i + 1) % sub_grid_height == 0 and i < grid_size - 1:
                classes.append("thick-bottom")
            
            if cell == 0 or cell is None:
                classes.append("empty")
                display_value = "·"
            else:
                classes.append("clue")
                display_value = str(cell)
            
            class_attr = f' class="{" ".join(classes)}"' if classes else ""
            html += f"<td{class_attr}>{display_value}</td>"
        html += "</tr>"
    
    html += "</table>"
    return html


def solve_and_display(solver):
    with st.spinner("Solving puzzle..."):
        start_time = time.time()
        
        try:
            success = solver.solve()
            solve_time = time.time() - start_time
            
            if success:
                solution = solver.get_solution()
                st.session_state.current_solver = solver
                st.session_state.current_solution = solution
                st.session_state.solve_time = solve_time
                
                st.success(f"Puzzle solved in {solve_time:.3f} seconds!")
                display_sudoku_board(solution, "Solution", solver)
            else:
                st.error("No solution found for this puzzle!")
        
        except Exception as e:
            st.error(f"Error solving puzzle: {str(e)}")


def solve_puzzle_with_options(solver, max_solutions, show_output):
    with st.spinner("Solving puzzle..."):
        start_time = time.time()
        
        try:
            if max_solutions == 1:
                success = solver.solve(show_output=show_output)
                solve_time = time.time() - start_time
                
                if success:
                    solution = solver.get_solution()
                    st.session_state.current_solver = solver
                    st.session_state.current_solution = solution
                    st.session_state.solve_time = solve_time
                    
                    st.success(f"Puzzle solved in {solve_time:.3f} seconds!")
                else:
                    st.error("No solution found!")
            else:
                max_sol = None if max_solutions == "All" else int(max_solutions)
                solutions = solver.find_all_solutions(max_solutions=max_sol)
                solve_time = time.time() - start_time
                
                st.session_state.current_solver = solver
                st.session_state.multiple_solutions = solutions
                st.session_state.solve_time = solve_time
                
                st.success(f"Found {len(solutions)} solution(s) in {solve_time:.3f} seconds!")
        
        except Exception as e:
            st.error(f"Error solving puzzle: {str(e)}")


def display_puzzle_and_solution():
    solver = st.session_state.current_solver
    
    # col_a, col_b = st.columns(2)
    
    # with col_a:
    display_sudoku_board(solver.board, "Original Puzzle", solver)
    
    # with col_b:
    if 'current_solution' in st.session_state:
        display_sudoku_board(st.session_state.current_solution, "Solution", solver)
        
        # Solution statistics
        st.subheader("Solution Statistics")
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Solve Time", f"{st.session_state.solve_time:.3f}s")
        with col_stat2:
            clues = count_clues(solver.board)
            total = len(solver.board) ** 2
            st.metric("Clues Used", f"{clues}/{total}")
        
        # Export solution
        pretty_solution = solver.get_pretty_string(st.session_state.current_solution)
        st.download_button(
            "📥 Download Solution",
            pretty_solution,
            file_name=f"sudoku_solution_{int(time.time())}.txt",
            mime="text/plain"
        )


def find_multiple_solutions(solver, max_solutions):
    with st.spinner(f"Finding up to {max_solutions} solutions..."):
        start_time = time.time()
        
        try:
            solutions = solver.find_all_solutions(max_solutions=max_solutions)
            solve_time = time.time() - start_time
            
            st.session_state.multiple_solutions = solutions
            st.session_state.multi_solve_time = solve_time
            st.session_state.multi_solver = solver  # Store the solver for display
            
            if len(solutions) == 0:
                st.error("No solutions found!")
            elif len(solutions) == 1:
                st.success(f"Found 1 unique solution in {solve_time:.3f} seconds!")
            else:
                st.success(f"Found {len(solutions)} solutions in {solve_time:.3f} seconds!")
                if len(solutions) == max_solutions:
                    st.warning(f"Reached maximum limit of {max_solutions} solutions. There may be more.")
        
        except Exception as e:
            st.error(f"Error finding solutions: {str(e)}")


def display_multiple_solutions():
    solutions = st.session_state.multiple_solutions
    
    st.subheader(f"Found {len(solutions)} Solution(s)")
    
    if len(solutions) > 1:
        st.warning("This puzzle has multiple solutions - it's not uniquely solvable!")
    
    # Solution selector
    if len(solutions) > 1:
        selected_solution = st.selectbox(
            "Select solution to view:",
            range(len(solutions)),
            format_func=lambda x: f"Solution {x+1}"
        )
    else:
        selected_solution = 0
    
    if solutions:
        col_orig, col_sol = st.columns(2)
        
        with col_orig:
            solver = st.session_state.multi_solver
            display_sudoku_board(solver.board, "Original Puzzle", solver)
        
        with col_sol:
            display_sudoku_board(solutions[selected_solution], f"Solution {selected_solution + 1}", solver)
        
        # Statistics
        st.subheader("Search Statistics")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Solutions Found", len(solutions))
        with col_stat2:
            st.metric("Search Time", f"{st.session_state.multi_solve_time:.3f}s")
        with col_stat3:
            avg_time = st.session_state.multi_solve_time / len(solutions)
            st.metric("Avg Time per Solution", f"{avg_time:.3f}s")





if __name__ == "__main__":
    main()
