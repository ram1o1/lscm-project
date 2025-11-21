## 🚀 How to Run the Project

### 1. Prerequisites

You need **Python 3.8+** installed on your system.

### 2. Setup and Installation

It is highly recommended to use a virtual environment to manage dependencies:

1.  **Create a Virtual Environment** (Optional but Recommended):
    ```bash
    python -m venv .venv
    ```

2.  **Activate the Virtual Environment:**
    * **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```

3.  **Install Dependencies:**
    Install all required Python packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependencies: `streamlit`, `pandas`, `plotly`, `openpyxl`)*

### 3. Running the App

Start the Streamlit application from your terminal:

```bash
streamlit run app.py