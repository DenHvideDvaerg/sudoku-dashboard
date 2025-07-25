# 🧩 Sudoku Dashboard

A Streamlit web application for generating, solving, and analyzing Sudoku puzzles of various sizes using Mixed Integer Programming (MIP) via the [sudoku-mip-solver](https://github.com/DenHvideDvaerg/sudoku-mip-solver) library.

## Features

- ✅ **Solve puzzles** of any size (4×4, 6×6, 9×9, 12×12, 16×16, etc.)
- 🎲 **Generate random puzzles** with customizable difficulty levels
- 🔍 **Find multiple solutions** to check puzzle uniqueness
- 📐 **Support non-standard grid sizes** (2×2 to 6×6 sub-grids)
- � **Multiple input methods**: Generate, String input, File upload, Manual entry
- � **Export puzzles and solutions** in multiple formats
- 🎨 **Interactive visual interface** with clean grid display

## Getting Started

### Online Demo

Visit the live demo on Streamlit Community Cloud: **[https://sudoku-dashboard.streamlit.app/](https://sudoku-dashboard.streamlit.app/)**

### Running Locally

1. Clone this repository:
```bash
git clone https://github.com/DenHvideDvaerg/sudoku-dashboard.git
cd sudoku-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run sudoku_dashboard.py
```

## Dependencies & Related Projects

Built with:
- [Streamlit](https://streamlit.io/) - Web application framework
- [sudoku-mip-solver](https://github.com/DenHvideDvaerg/sudoku-mip-solver) - Core MIP-based Sudoku solving library
