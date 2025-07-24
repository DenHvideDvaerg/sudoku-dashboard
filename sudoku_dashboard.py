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
    
    # Display sidebar
    display_sidebar()
    
    # Create two main columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Global grid dimensions
        col_dimension_input, col_solver_options = st.columns([1.25,1])
        with col_dimension_input: 
            sub_grid_width, sub_grid_height = get_grid_dimensions()
        
        # Input method tabs
        st.subheader("Input Method")
        tab1, tab2, tab3, tab4 = st.tabs(["🎲 Generate", "📝 String", "📁 File", "✏️ Manual"])
        
        with tab1:
            generate_puzzle_tab(sub_grid_width, sub_grid_height)
        
        with tab2:
            string_input_tab(sub_grid_width, sub_grid_height)
        
        with tab3:
            file_input_tab(sub_grid_width, sub_grid_height)
        
        with tab4:
            manual_input_tab(sub_grid_width, sub_grid_height)
    
        # Note: After the input method tabs, so that the solver has been set up
        with col_solver_options:
            # Solving options
            solve_options_section()

    with col2:
        # Display puzzle and solution
        display_puzzle_and_results()

def get_grid_dimensions():
    """Get grid dimensions input from user"""
    st.subheader("Grid Dimensions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sub_grid_width = st.number_input(
            "Sub-grid Width", 
            min_value=2, 
            max_value=6, 
            value=3,
            help="Width of each sub-grid (e.g., 3 for standard 9x9 Sudoku)",
            key="global_sub_grid_width"
        )
    
    with col2:
        sub_grid_height = st.number_input(
            "Sub-grid Height", 
            min_value=2, 
            max_value=6, 
            value=3,
            help="Height of each sub-grid (e.g., 3 for standard 9x9 Sudoku)",
            key="global_sub_grid_height"
        )
    
    # Display grid size below the inputs for better alignment
    grid_size = sub_grid_width * sub_grid_height
    st.info(f"**Grid size: {grid_size}×{grid_size}**")
        
    return sub_grid_width, sub_grid_height


def solve_options_section():
    """Display solving options section"""
    if 'current_solver' not in st.session_state:
        return
    
    st.subheader("Solving Options")
    
    # Create placeholders for consistent layout
    button_placeholder = st.empty()
    options_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # All options within the options container
    with options_placeholder.container():
        # Multiple solutions toggle
        allow_multiple = st.checkbox(
            "Allow Multiple Solutions",
            value=False,
            help="Search for multiple solutions instead of stopping at the first one",
            key="allow_multiple_solutions"
        )
        
        # Show max solutions input only if multiple solutions is enabled
        if allow_multiple:
            max_solutions = st.number_input(
                "Maximum Solutions:",
                min_value=1,
                max_value=100,
                value=10,
                help="Limit the search to avoid excessive computation",
                key="max_solutions_input"
            )
    
    # Button placement stays consistent
    with button_placeholder.container():
        # Get the states from session state using the keys
        allow_multiple = st.session_state.get("allow_multiple_solutions", False)
        
        if allow_multiple:
            # Get the max_solutions value from session state or use default
            max_solutions = st.session_state.get("max_solutions_input", 10)
            if st.button("🔢 Find Multiple Solutions", type="primary", key="solve_multiple"):
                solve_puzzle_with_options(max_solutions, status_placeholder, False)
        else:
            if st.button("🔍 Solve Puzzle", type="primary", key="solve_single"):
                solve_puzzle_with_options(1, status_placeholder, False)


def clear_solution_state():
    """Clear solution-related state when loading a new puzzle"""
    keys_to_clear = [
        'current_solution',
        'multiple_solutions',
        'solve_time',
        'multi_solve_time'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def generate_puzzle_tab(sub_grid_width, sub_grid_height):
    """Generate puzzle tab content"""
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
        value=True,
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
                
                # Clear previous solutions
                clear_solution_state()
                
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
                st.session_state.current_solver = solver
                st.session_state.generated_difficulty = actual_difficulty
                st.session_state.generation_time = generation_time
                st.session_state.string_puzzle_input = solver.to_string()

                st.success(f"Puzzle generated successfully in {generation_time:.2f} seconds!")
                st.info(f"Actual difficulty: {actual_difficulty:.3f}")
                
            except Exception as e:
                st.error(f"Error generating puzzle: {str(e)}")
    

def string_input_tab(sub_grid_width, sub_grid_height):
    """String input tab content"""
    grid_size = sub_grid_width * sub_grid_height

    st.subheader("String Input")
    
    # Button row - matching the manual input tab layout
    col_load, col_update, col_clear = st.columns(3)
    status_container = st.empty()
    
    with col_load:
        if st.button("📥 Load Current Puzzle", help="Load the active puzzle into the string input field"):
            if 'current_solver' in st.session_state:
                solver = st.session_state.current_solver
                st.session_state.string_puzzle_input = solver.to_string()
                status_container.success("Puzzle loaded into string input!")
            else:
                status_container.warning("No active puzzle to load!")
    
    with col_clear:
        if st.button("🗑️ Clear Field", help="Clear the string input field"):
            st.session_state.string_puzzle_input = ""
            status_container.success("String input cleared!")
    
    # Get current value from session state or use empty string
    current_value = st.session_state.get('string_puzzle_input', '')
    
    puzzle_string = st.text_area(
        "Enter puzzle string:",
        value=current_value,
        placeholder=f"Enter {grid_size}x{grid_size} puzzle as a string with 0 for empty cells",
        help=f"Enter puzzle as a string of {grid_size**2} characters with 0 or . for empty cells",
        height=100
    )
    
    # Update session state when text changes
    if puzzle_string != current_value:
        st.session_state.string_puzzle_input = puzzle_string
    
    # Update puzzle button (after text area creation)
    with col_update:
        if st.button("🚀 Update Puzzle", help="Update the active puzzle with the string input", disabled=not puzzle_string.strip()):
            try:
                # Clear previous solutions
                clear_solution_state()
                
                solver = SudokuMIPSolver.from_string(
                    puzzle_string.strip(),
                    sub_grid_width=sub_grid_width,
                    sub_grid_height=sub_grid_height
                )
                st.session_state.current_solver = solver
                status_container.success("Puzzle updated successfully!")
            except Exception as e:
                status_container.error(f"Error parsing puzzle string: {str(e)}")
    

def file_input_tab(sub_grid_width, sub_grid_height):
    """File input tab content"""
    uploaded_file = st.file_uploader("Choose a puzzle file", type=['txt'])
    
    # Only process if we have a file and haven't processed this exact file yet
    if uploaded_file is not None:
        # Use file content hash to detect if this is a new file
        content = uploaded_file.read().decode('utf-8')
        content_hash = hash(content)
        
        # Only process if this is a new file upload
        if st.session_state.get('last_uploaded_hash') != content_hash:
            try:
                # Clear previous solutions
                clear_solution_state()
                
                solver = SudokuMIPSolver.from_string(
                    content.strip(),
                    sub_grid_width=sub_grid_width,
                    sub_grid_height=sub_grid_height
                )
                st.session_state.current_solver = solver
                st.session_state.last_uploaded_hash = content_hash
                st.success("Puzzle loaded from file successfully!")
            except Exception as e:
                st.error(f"Error parsing file: {str(e)}")
    

def manual_input_tab(sub_grid_width, sub_grid_height):
    """Manual input tab content"""
    grid_size = sub_grid_width * sub_grid_height
    
    st.subheader("Manual Input Grid")
    
    # Load current puzzle button
    col_load, col_update, col_clear = st.columns(3)
    status_container = st.empty()
    with col_load:
        if st.button("📥 Load Current Puzzle", help="Load the active puzzle into the manual input grid"):
            if 'current_solver' in st.session_state:
                solver = st.session_state.current_solver
                solver_grid_size = len(solver.board)
                
                # Check if the current puzzle matches the manual input grid size
                if solver_grid_size != grid_size:
                    status_container.error(f"Cannot load {solver_grid_size}×{solver_grid_size} puzzle into {grid_size}×{grid_size} manual input grid. Please adjust the grid dimensions to match.")
                else:
                    load_puzzle_into_manual_input(solver.board, grid_size)
                    status_container.success("Puzzle loaded into manual input!")
            else:
                status_container.warning("No active puzzle to load!")
    
    with col_clear:
        if st.button("🗑️ Clear Grid", help="Clear all values in the manual input grid"):
            clear_manual_input_grid(grid_size)
            status_container.success("Grid cleared!")
    
    # Create the manual input grid
    board = create_manual_input_grid(grid_size)
    
    # Create puzzle button (after board creation)
    with col_update: 
        if st.button("🚀 Update Puzzle", help="Update the active puzzle with the manual input grid values"):
            try:
                # Clear previous solutions
                clear_solution_state()
                
                # The board already contains None for empty cells and integers for filled cells
                solver = SudokuMIPSolver(board, sub_grid_width, sub_grid_height)
                st.session_state.current_solver = solver
                status_container.success("Puzzle created successfully!")
            except Exception as e:
                status_container.error(f"Error creating puzzle: {str(e)}")
        

def create_manual_input_grid(grid_size):
    """Create a manual input grid for entering puzzle values"""
    
    # Initialize session state keys to None if they don't exist (ensures empty widgets on first load)
    for i in range(grid_size):
        for j in range(grid_size):
            key = f"manual_cell_{grid_size}_{i}_{j}"
            if key not in st.session_state:
                st.session_state[key] = None
    
    st.write(f"Enter values for {grid_size}×{grid_size} grid (leave empty or enter 0 for blank cells):")
    
    board = []
    
    for i in range(grid_size):
        row = []
        st.write(f"**Row {i+1}:**")
        row_cols = st.columns(grid_size)
        
        for j in range(grid_size):
            with row_cols[j]:
                # Get existing value from session state if available
                # Include grid_size in key to avoid conflicts when grid size changes
                key = f"manual_cell_{grid_size}_{i}_{j}"
                
                value = st.number_input(
                    f"({i+1},{j+1})",
                    min_value=0,
                    max_value=grid_size,
                    key=key,
                    label_visibility="collapsed",
                    help=f"Cell ({i+1},{j+1}) - Enter number 1-{grid_size} or 0 to leave empty",
                    placeholder="·",
                    width=120 # Hides the +/- buttons
                )
                # Convert 0 values to None for SudokuMIPSolver compatibility
                row.append(None if value == 0 else value)
        board.append(row)

    return board


def load_puzzle_into_manual_input(puzzle_board, grid_size):
    """Load an existing puzzle into the manual input grid"""
    for i in range(min(len(puzzle_board), grid_size)):
        for j in range(min(len(puzzle_board[i]), grid_size)):
            # Include grid_size in key to match the key format used in create_manual_input_grid
            key = f"manual_cell_{grid_size}_{i}_{j}"
            value = puzzle_board[i][j]
            # Store the actual value (None for empty, integer for filled)
            st.session_state[key] = value if value is not None and value != 0 else None


def clear_manual_input_grid(grid_size):
    """Clear all values in the manual input grid"""
    for i in range(grid_size):
        for j in range(grid_size):
            # Include grid_size in key to match the key format used in create_manual_input_grid
            key = f"manual_cell_{grid_size}_{i}_{j}"
            if key in st.session_state:
                st.session_state[key] = None


def display_puzzle_and_results():
    """Display puzzle and solution in the right column"""

    st.subheader("Current Puzzle")
    if 'current_solver' in st.session_state:

        original_col, solved_col = st.columns(2)
        original_export_col, solved_export_col = st.columns(2)
        with original_col:

            solver = st.session_state.current_solver
            
            # Display original puzzle
            display_sudoku_board(solver.board, "Puzzle")
            
            col1, col2 = st.columns(2)
            with col1:
                # Display puzzle statistics
                clues = count_clues(solver.board)
                total_cells = len(solver.board) ** 2
                st.metric("Clues", f"{clues}/{total_cells}")
            with col2:    
                if 'generated_difficulty' in st.session_state:
                    st.metric("Difficulty", f"{st.session_state.generated_difficulty:.3f}")
                if 'generation_time' in st.session_state:
                    st.metric("Generation Time", f"{st.session_state.generation_time:.2f}s")
            
        with original_export_col:
            # Export options
            create_export_interface("Puzzle", solver.board, "puzzle_format_radio")
        
        # Determine which solution board to use for export
        selected_solution_board = None
        
        with solved_col:
            # Display solution if available
            if 'current_solution' in st.session_state:
                st.subheader("Solution")
                display_sudoku_board(st.session_state.current_solution, "Solution")
                
                # Solution statistics
                st.subheader("Solution Statistics")
                col_sol1, col_sol2 = st.columns(2)
                with col_sol1:
                    st.metric("Solve Time", f"{st.session_state.solve_time:.3f}s")
                with col_sol2:
                    st.metric("Status", "Solved ✓")
                
                selected_solution_board = st.session_state.current_solution

            # Display multiple solutions if available
            elif 'multiple_solutions' in st.session_state:
                selected_solution_board = display_multiple_solutions()

        with solved_export_col:
             if selected_solution_board is not None:
                # Export solution (works for both single and multiple solutions)
                create_export_interface("Solution", selected_solution_board, "solution_format_radio")
        
    else:
        st.info("Please generate or input a puzzle using the options on the left")

  
def display_sidebar():
    """Display the sidebar with information and tips"""
    with st.sidebar:
        st.header("📚 About")
        st.write("""
        This dashboard uses the **sudoku-mip-solver** library to solve and generate Sudoku puzzles using Mixed Integer Programming (MIP).
        
        ### Features:
        - ✅ Solve puzzles of any size
        - 🎲 Generate random puzzles
        - 🔍 Find multiple solutions
        - 📐 Support non-standard grid sizes
        - ⚙️ Customizable difficulty levels
        - 📥 Export puzzles and solutions
        - 📁 Load puzzles from files
        
        ### Supported Grid Sizes:
        - 9×9 (standard)
        - 6×6, 4×4, 12×12, 16×16
        - Custom dimensions (2×2 to 6×6 sub-grids)
        
        ### Input Methods:
        - **Generate**: Create random puzzles with customizable difficulty
        - **String**: Enter puzzle as text (0 or . for empty cells)
        - **File**: Upload puzzle files (.txt format)
        - **Manual**: Enter values cell by cell with visual grid interface
        """)
                
        st.header("💡 Tips")
        st.write("""
        - Use the **Generate** tab to create practice puzzles
        - Try different grid sizes for variety
        - Enable "Multiple Solutions" to check puzzle uniqueness
        - Export puzzles to share or save for later
        - Use the string format to input puzzles from other sources
        """)

        st.header("🔗 Links")
        st.write("""
        - [sudoku-mip-solver GitHub](https://github.com/DenHvideDvaerg/sudoku-mip-solver)
        - [Streamlit Documentation](https://docs.streamlit.io/)
        """)


# Helper functions
def create_export_interface(content_type, board_data, radio_key):
    """Create complete export interface with expander, text area, and download options"""
    
    if "current_solver" not in st.session_state:
        return
    
    solver = st.session_state.current_solver

    with st.expander("Export Options"):
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            content_string = solver.to_string(board_data)
            st.text_area(f"{content_type} as String", content_string, height=68)
        
        with col_exp2:
            # Download format selection
            st.write(f"**Download {content_type} Format:**")
            download_format = st.radio(
                "Choose format:",
                options=["String Format", "Pretty Format"],
                help="String format is compatible with file upload, Pretty format is human-readable",
                label_visibility="collapsed",
                key=radio_key
            )
            
            # Single download button
            if download_format == "String Format":
                download_content = content_string
                file_suffix = "string"
                format_help = f"{content_type} in string format (compatible with re-import)"
            else:
                download_content = solver.get_pretty_string(board_data)
                file_suffix = "pretty"
                format_help = f"{content_type} in pretty format (human-readable)"
            
            st.download_button(
                f"📥 Download {content_type}",
                download_content,
                file_name=f"sudoku_{content_type.lower()}_{file_suffix}_{int(time.time())}.txt",
                mime="text/plain",
                help=format_help
            )


def count_clues(board):
    return sum(sum(1 for cell in row if cell != 0 and cell is not None) for row in board)


def display_sudoku_board(board, title="Sudoku Board"):
    st.subheader(title)
    
    # Create a styled display of the Sudoku board
    board_html = create_sudoku_html(board)
    st.markdown(board_html, unsafe_allow_html=True)


def create_sudoku_html(board):
    if "current_solver" not in st.session_state:
        return
    
    solver = st.session_state.current_solver

    grid_size = len(board)
    sub_grid_width = solver.sub_grid_width
    sub_grid_height = solver.sub_grid_height
    
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


def solve_puzzle_with_options(max_solutions, status_placeholder, show_output):
    if 'current_solver' not in st.session_state:
        st.error("No active puzzle to solve!")
        return
    
    solver = st.session_state.current_solver
    
    with st.spinner("Solving puzzle..." if max_solutions == 1 else f"Finding up to {max_solutions} solutions..."):
        start_time = time.time()
        
        try:
            if max_solutions == 1:
                # Clear multiple solutions state when solving for single solution
                if 'multiple_solutions' in st.session_state:
                    del st.session_state.multiple_solutions
                if 'multi_solve_time' in st.session_state:
                    del st.session_state.multi_solve_time
                
                success = solver.solve(show_output=show_output)
                solve_time = time.time() - start_time
                
                if success:
                    solution = solver.get_solution()
                    st.session_state.current_solver = solver
                    st.session_state.current_solution = solution
                    st.session_state.solve_time = solve_time
                    
                    status_placeholder.success(f"Puzzle solved in {solve_time:.3f} seconds!")
                else:
                    status_placeholder.error("No solution found!")
            else:
                # Clear single solution state when solving for multiple solutions
                if 'current_solution' in st.session_state:
                    del st.session_state.current_solution
                if 'solve_time' in st.session_state:
                    del st.session_state.solve_time
                
                solutions = solver.find_all_solutions(max_solutions=max_solutions)
                solve_time = time.time() - start_time
                
                # Reset the model to remove any cuts added during find_all_solutions
                solver.reset_model()
                
                st.session_state.current_solver = solver
                st.session_state.multiple_solutions = solutions
                st.session_state.multi_solve_time = solve_time
                
                if len(solutions) == 0:
                    status_placeholder.error("No solutions found!")
                elif len(solutions) == 1:
                    status_placeholder.success(f"Found 1 unique solution in {solve_time:.3f} seconds!")
                else:
                    status_placeholder.success(f"Found {len(solutions)} solutions in {solve_time:.3f} seconds!")
                    if len(solutions) == max_solutions:
                        status_placeholder.warning(f"Reached maximum limit of {max_solutions} solutions. There may be more.")
        
        except Exception as e:
            status_placeholder.error(f"Error solving puzzle: {str(e)}")


def display_multiple_solutions():
    solutions = st.session_state.multiple_solutions
    
    st.subheader(f"Found {len(solutions)} Solution(s)")
    
    if solutions:        
        # Create a placeholder for the board that we can update
        board_placeholder = st.empty()
        
        # Solution selector (only show if there are multiple solutions)
        if len(solutions) > 1:
            selected_solution = st.selectbox(
                "Select solution to view:",
                range(len(solutions)),
                format_func=lambda x: f"Solution {x+1}"
            )
        else:
            selected_solution = 0
        
        # Display the selected solution in the placeholder
        with board_placeholder.container():
            display_sudoku_board(solutions[selected_solution], f"Solution {selected_solution + 1}")
        
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
        
        # Return the selected solution board for export
        return solutions[selected_solution]
    
    return None


if __name__ == "__main__":
    main()
