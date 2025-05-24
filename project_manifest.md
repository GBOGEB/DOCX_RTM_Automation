## 3. Workflow

```mermaid
graph TD
    A[Word Document] -->|word_to_md.py| B[Markdown]
    B -->|clean_outline.py| C[Outline YAML/JSON]
    B -->|generate_rtm.py| D[Requirements]
    C -->|ascii_diagram.py| E[ASCII Diagram]
    D -->|generate_rtm.py| F[RTM Output]
    F -->|compare_formats.py| G[Format Validation]
    G -->|github_operations.py| H[GitHub Repository]