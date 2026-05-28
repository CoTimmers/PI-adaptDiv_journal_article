# PI-adaptDiv: Adaptive Algorithm to Prevent and Escape Online Filter Bubbles

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This repository contains the complete implementation and reproducible experiments for the paper **"PI-adaptDiv: an adaptive algorithm to prevent and escape online filter bubbles"**. The codebase enables reproduction of all results presented in the article and supports running new simulations of user interactions with four different recommendation algorithms on two major news datasets.

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Datasets](#datasets)
- [Recommendation Algorithms](#recommendation-algorithms)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Reproducing Paper Results](#reproducing-paper-results)
  - [Running New Simulations](#running-new-simulations)
- [Project Structure](#project-structure)
- [Results](#results)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About the Project

Filter bubbles represent a significant challenge in modern recommendation systems, where users become increasingly isolated in personalized content environments. This project introduces **PI-adaptDiv**, an adaptive diversification algorithm designed to both prevent the formation of filter bubbles and help users escape existing ones.

The repository provides:
- Complete implementation of PI-adaptDiv and baseline algorithms
- Simulation frameworks for user-recommender interactions
- Analysis notebooks with all paper results
- Tools for running custom experiments on real-world datasets

## Key Features

- **Multiple Recommendation Strategies**: Baseline, MMR, MMR with Expected Diversity Change, and PI-adaptDiv
- **Two Major Datasets**: Support for EB-NeRD and MIND news recommendation datasets
- **User Behavior Simulation**: Realistic modeling of user interactions and preference evolution
- **Comprehensive Metrics**: Diversity, precision, and filter bubble measurements
- **Reproducible Results**: All paper figures and statistics can be regenerated
- **Dockerized Environment**: Consistent execution environment across platforms
- **Extensible Framework**: Easy to add new algorithms or datasets

## Datasets

### [EB-NeRD](https://dl.acm.org/doi/10.1145/3687151.3687152)
Ekstra Bladet News Recommendation Dataset - A large-scale Danish news dataset with real user interactions.

### [MIND](https://msnews.github.io/)
Microsoft News Dataset - A comprehensive English news dataset from Microsoft News with diverse content and user behaviors.

## Recommendation Algorithms

1. **Baseline**: Standard collaborative filtering without diversification
2. **MMR (Maximal Marginal Relevance)**: Static diversification with fixed trade-off parameter
3. **MMR-ExpDivChange**: MMR variant optimizing expected diversity change
4. **PI-adaptDiv**: Adaptive diversification using proportional-integral control to dynamically balance relevance and diversity

## Requirements

- [Docker](https://www.docker.com/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/) (v2.0+)
- At least 8GB RAM recommended
- 10GB+ free disk space for datasets

## Installation

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/CoTimmers/PI-adaptDiv_journal_article.git
   cd PI-adaptDiv_journal_article
   ```

2. **Build the Docker images**
   ```bash
   docker-compose build
   ```

3. **Load the datasets**
   ```bash
   docker-compose up load_data
   ```
   This step downloads and preprocesses the EB-NeRD and MIND datasets.

### Local Installation (Alternative)

If you prefer running without Docker:

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate the environment**
   ```bash
   poetry shell
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials if needed
   ```

## Usage

### Reproducing Paper Results

All results from the paper are available in Jupyter notebooks and can be reproduced interactively:

```bash
docker-compose up notebook
```

Then navigate to `http://localhost:8888` in your browser. The analysis notebooks are located in:

- **EB-NeRD Results**: `offline_study/ebnerd/notebooks/analyse_massive_simulation.ipynb`
- **MIND Results**: `offline_study/mind/notebooks/analyse_massive_simulations.ipynb`
- **Online Study**: `online_study/notebooks/experiment_analysis.ipynb`
- **User Behavior Validation**:
  - `offline_study/ebnerd/user_behavior/model_validation.ipynb`
  - `offline_study/mind/user_behavior/model_validation.ipynb`

### Running New Simulations

#### 1. Configure Simulation Parameters

Edit the simulation configuration files to enable desired algorithms:

**For EB-NeRD:**
```bash
nano offline_study/ebnerd/run_massive_simulations.py
```

**For MIND:**
```bash
nano offline_study/mind/run_massive_simulations.py
```

#### 2. Set Algorithm Parameters

```python
# Enable/disable algorithms
run_baseline_simulations = True  # Standard recommendation
run_mmr_simulations = True        # MMR with fixed lambda
run_mmr_expected_div_change_simulations = True  # MMR-ExpDivChange
run_adaptative_simulations = True # PI-adaptDiv

# Configure parameters
if run_mmr_simulations:
    lambda_ = 0.7  # Diversity weight (0-1)
    run_mmr_simulations_for_active_users(lambda_)

if run_mmr_expected_div_change_simulations:
    lambda_ = 0.9  # Diversity weight (0-1)
    run_mmr_expected_div_change_simulations_for_active_users(lambda_)

if run_adaptative_simulations:
    K_p = 10  # Proportional gain for adaptive control
    run_adaptative_simulations_for_active_users(K_p)
```

#### 3. Rebuild and Run

```bash
# Rebuild with new configuration
docker-compose build

# Run simulations for EB-NeRD
docker-compose up run_new_simulations_ebnerd

# Run simulations for MIND
docker-compose up run_new_simulations_mind
```

#### 4. Analyze Results

After simulations complete, use the analysis notebooks to visualize and analyze results:

```bash
docker-compose up notebook
```

## Project Structure

```
PI-adaptDiv_journal_article/
├── offline_study/              # Offline simulation experiments
│   ├── ebnerd/                 # EB-NeRD dataset experiments
│   │   ├── notebooks/          # Analysis notebooks
│   │   ├── user_behavior/      # User behavior models
│   │   ├── diversification_strategies.py
│   │   ├── simulation.py
│   │   └── run_massive_simulations.py
│   └── mind/                   # MIND dataset experiments
│       ├── notebooks/          # Analysis notebooks
│       ├── user_behavior/      # User behavior models
│       ├── diversification_strategies.py
│       ├── simulation.py
│       └── run_massive_simulations.py
├── online_study/               # Online user study
│   ├── notebooks/              # Experiment analysis
│   ├── data/                   # User study data
│   └── experiment_phase/       # Experiment implementation
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container definition
├── pyproject.toml              # Python dependencies
└── README.md                   # This file
```

## Results

The main results include:

- **Diversity Evolution**: How content diversity changes over recommendation rounds
- **Precision Metrics**: Recommendation accuracy across different algorithms
- **Filter Bubble Indicators**: Measurement of content isolation
- **User Engagement**: Probability of users finding relevant content
- **Adaptation Performance**: How PI-adaptDiv responds to user preference changes

All results are presented with statistical significance tests and confidence intervals.

## Citation

If you use this code or dataset in your research, please cite:

```bibtex
@article{timmers2024piadaptdiv,
  title={PI-adaptDiv: an adaptive algorithm to prevent and escape online filter bubbles},
  author={Timmers, Colin and [Other Authors]},
  journal={[Journal Name]},
  year={2024},
  volume={[Volume]},
  pages={[Pages]},
  doi={[DOI]}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows existing style conventions
- All tests pass
- New features include appropriate tests
- Documentation is updated

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Colin Timmers** - [GitHub](https://github.com/CoTimmers)

**Project Link**: [https://github.com/CoTimmers/PI-adaptDiv_journal_article](https://github.com/CoTimmers/PI-adaptDiv_journal_article)

---

**Troubleshooting**

<details>
<summary>Docker build fails</summary>

- Ensure Docker Desktop is running
- Check you have sufficient disk space (10GB+)
- Try `docker system prune` to clean up old images
</details>

<details>
<summary>Notebook server won't start</summary>

- Check port 8888 is not in use: `lsof -i :8888`
- Try changing the port in docker-compose.yml
- Ensure containers are fully stopped: `docker-compose down`
</details>

<details>
<summary>Simulations are slow</summary>

- Simulations are computationally intensive
- Consider reducing the number of users or rounds
- Increase Docker memory allocation in Docker Desktop settings
</details>

---

## Citation

```bash
   @article{timmers2026pi,
    title={PI-adaptDiv: an adaptive algorithm to prevent and escape online filter bubbles},
    author={Timmers, Colin and Fouss, Fran{\c{c}}ois and Vande Kerckhove, Corentin},
    journal={ACM Transactions on Recommender Systems},
    year={2026},
    publisher={ACM New York, NY}}
```



For more information, issues, or questions, please open an issue on GitHub.
