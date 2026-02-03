# Code Similarity Measurement using Machine Learning

## Overview

This project implements a **Machine Learning–based system to measure similarity between source code files**. It is designed to analyze and compare code submissions that may be syntactically different but logically similar, with applications in **plagiarism detection, code clone analysis, and software assessment**.

The system is developed as a **Django-based web application** with a dedicated similarity engine that handles preprocessing, feature extraction, and similarity computation.

This project is also my **Final Year Project**, focusing on applying ML techniques to real-world software engineering problems rather than toy datasets.

---

## Problem Statement

Traditional code comparison techniques often rely on direct text matching, which fails when:

* Variable names are changed
* Code is reformatted
* Logic is restructured but functionality remains the same

This project addresses that gap by using **Machine Learning–based approaches** to capture deeper patterns in source code and provide more meaningful similarity scores.

---

## System Architecture

The project is structured into three major layers:

1. **Web Layer (Django)**

   * Handles user interaction, file uploads, dashboards, and history tracking
   * Renders comparison results through HTML templates

2. **Similarity Engine**

   * Preprocesses source code files
   * Extracts features suitable for ML models
   * Computes similarity using trained models and similarity metrics

3. **Machine Learning Layer**

   * Supports multiple ML models (SVM, Random Forest, Neural Networks, Gradient Boosting)
   * Training logic is maintained separately for reproducibility

---

## Key Features

* Upload and compare multiple source code files
* Supports comparison across different programming files
* ML-based similarity scoring instead of plain text matching
* Stores comparison history for later review
* Modular design separating web logic and ML logic

---

## Technologies Used

* **Programming Language:** Python
* **Web Framework:** Django
* **Machine Learning:** scikit-learn
* **Data Processing:** NumPy, Pandas
* **Frontend:** HTML, CSS (Django Templates)
* **Database:** SQLite (development)

---

## Project Structure (Simplified)

```
code-similarity-measurement-ml/
│
├── accounts/              # Authentication and account handling
├── admins/                # Admin-level functionality
├── users/                 # User-facing features
├── similarity_engine/     # Core ML similarity logic
├── ml_models/             # Model training scripts (no binaries)
├── templates/             # HTML templates
├── static/                # Static files
├── reports/               # Comparison reports and logic
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## How the Similarity Works (High-Level)

1. Uploaded source code files are cleaned and normalized
2. Code is transformed into feature representations suitable for ML
3. Trained models evaluate similarity between code pairs
4. A similarity score is generated and presented to the user

> Note: Trained model binaries are intentionally **not committed** to the repository. The project emphasizes reproducibility through training scripts rather than binary artifacts.

---

## How to Run the Project Locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations:

   ```bash
   python manage.py migrate
   ```
5. Start the development server:

   ```bash
   python manage.py runserver
   ```
6. Open the application in your browser:

   ```
   http://127.0.0.1:8000/
   ```

---

## Use Cases

* Academic plagiarism detection
* Code clone identification
* Software quality assessment
* Learning tool for understanding ML applications in software engineering

---

## Future Improvements

* Support for cross-language code similarity
* Integration with deep learning models (e.g., CodeBERT)
* Improved explainability of similarity scores
* Scalable deployment using Streamlit or cloud platforms

---

## Disclaimer

This project is intended for **academic and learning purposes**. Similarity scores should be interpreted as supportive indicators rather than absolute judgments.

---

## Author

**Yateen R**
B.Tech Computer Science & Engineering
Final Year Project
