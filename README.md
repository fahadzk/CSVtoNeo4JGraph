# CSV to Neo4j Graph

Standalone utility for converting a two-column relationship mapping from CSV into a Neo4j graph.

## Basic workflow

1. Start the application.
2. Upload a CSV file.
3. Select the primary column.
4. Select the secondary column.
5. Enter or accept a predicate.
6. Enter a node prefix.
7. Preview the generated nodes and relationships.
8. Select the Neo4j connection.
9. Press Insert / update graph.

## Neo4j settings

Create this file:

```text
config/neo4j.json
```

Example:

```json
{
  "uri": "neo4j://localhost:7687",
  "database": "neo4j",
  "username": "neo4j",
  "password": "your-password",
  "timeout_seconds": 30
}
```

For safety, use an environment variable instead of storing the password:

```text
NEO4J_PASSWORD=your-password
```

When both values exist, the environment variable should win.

Do not commit `config/neo4j.json` when it contains credentials. Add it to `.gitignore`.

## Import behavior

The application creates nodes with the label `CSVEntity` and relationships with the fixed Neo4j type `RELATED_TO`. The selected predicate is stored on the relationship as a property:

```text
(source:CSVEntity)-[:RELATED_TO {predicate: "LOCATED_IN"}]->(target:CSVEntity)
```

This avoids unsafe dynamic relationship types and makes repeated imports idempotent.

Repeated values are deduplicated by normalized value and entity type. Re-importing the same file should update existing nodes and relationships rather than create duplicates.

## Example query after import

```cypher
MATCH (city:CSVEntity)-[r:RELATED_TO]->(province:CSVEntity)
WHERE r.predicate = "LOCATED_IN"
RETURN city, r, province
LIMIT 100
```

## Important safety rules

- Preview data before writing.
- Use parameterized Cypher.
- Use one transaction per import.
- Roll back on any error.
- Never log the Neo4j password.
- Keep imports scoped by `import_id` and `source_file`.
- Do not delete existing graph data during a normal import.

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for the complete handoff specification.

## Installation and startup

Create a virtual environment, install the Python dependencies, and copy the example Neo4j settings:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config/neo4j.example.json config/neo4j.json
```

Set `NEO4J_PASSWORD` in `.env` or in the shell. Environment variables override the JSON settings. Start the backend from the repository root:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal, install and start the Vite frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, upload a CSV, preview it, test the configured Neo4j connection, and explicitly confirm the import. Backend tests run with `pytest`; the frontend production build runs with `npm run build`.
