# Contributing to Microboss

Thank you for considering contributing to Microboss! Here are some guidelines to help you get started.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/microboss.git
   cd microboss
   ```

2. Install dependencies with Poetry:
   ```bash
   ./install.sh
   ```
   
   Or manually:
   ```bash
   poetry install
   ```

3. Run the tests:
   ```bash
   poetry run pytest
   ```

## Code Style

We use:
- Black for code formatting
- isort for import sorting
- pylint for linting

You can run these tools with:
```bash
poetry run black .
poetry run isort .
poetry run pylint microboss
```

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Update the documentation if needed.
3. Make sure your code passes all tests.
4. Submit a pull request!

## Adding a New Feature

1. First, create an issue describing the feature you want to add.
2. Implement the feature in your fork.
3. Write tests for your feature.
4. Submit a pull request.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 