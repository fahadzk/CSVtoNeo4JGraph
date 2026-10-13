# CSV to Neo4j Graph - Implementation Details

## Build directive for the implementation agent

Build a complete, runnable standalone application from this document. Do not assume access to the DocIntelligence repository. Do not implement only a mockup or pseudocode. The finished project must include a working Python backend, working frontend, tests, configuration examples, and startup instructions.

### Required stack

- Python 3.10+.
- FastAPI backend.
- Uvicorn development server.
- Official `neo4j` Python driver.
- Python standard-library `csv` module for parsing CSV files.
- React + TypeScript frontend built with Vite.
- Plain CSS or a small existing component system; do not add a large UI framework for this small tool.
- Pytest for backend tests.
- Vitest and React Testing Library for frontend tests.

### Required project structure

Create at least this structure:

```text
csv-to-neo4j/
  backend/
    app/
      main.py
      config.py
      csv_parser.py
      graph_builder.py
      neo4j_client.py
      schemas.py
      api.py
    tests/
  frontend/
    src/
      App.tsx
      api.ts
      types.ts
      components/
      styles/
    package.json
  config/
    neo4j.example.json
  .env.example
  README.md
  IMPLEMENTATION.md
  requirements.txt
```

The agent may use a different structure, but it must preserve the same separation: CSV parsing and graph generation must be independently testable from the HTTP API and UI.

### Required backend implementation

Implement these backend responsibilities:

1. `csv_parser.py`
   - Parse uploaded CSV bytes with UTF-8 decoding.
   - Support quoted values and commas inside quoted values.
   - Validate headers and row widths.
   - Return headers, rows, warnings, and row count.
   - Never write the uploaded file permanently unless explicitly needed.

2. `graph_builder.py`
   - Accept rows, primary column, secondary column, predicate, prefix, and source filename.
   - Return normalized nodes, relationships, skipped-row warnings, and summary counts.
   - Have no FastAPI or Neo4j imports so it can be unit tested directly.

3. `neo4j_client.py`
   - Load settings from `config/neo4j.json` and environment variables.
   - Use the official Neo4j Python driver.
   - Provide `test_connection()`.
   - Provide one transactional `upsert_graph(nodes, relationships)` method.
   - Use parameters only; never concatenate CSV values into Cypher.
   - Close the driver cleanly.

4. `api.py`
   - Add an upload/parse endpoint.
   - Add a graph preview endpoint.
   - Add a Neo4j connection-test endpoint.
   - Add an insert/update endpoint.
   - Validate every request with Pydantic models.
   - Return useful HTTP errors without exposing passwords or stack traces.

5. `main.py`
   - Create the FastAPI app.
   - Configure CORS for the local Vite development server.
   - Add a health endpoint.
   - Serve the API under a clear prefix such as `/api`.

### Required frontend implementation

Implement a complete single-page workflow:

1. Upload CSV.
2. Show filename, row count, columns, warnings, and sample rows.
3. Let the user select primary and secondary columns.
4. Automatically remove the primary column from secondary options.
5. Show editable predicate input with a useful suggestion.
6. Show editable node-prefix input with a filename-based suggestion.
7. Preview the generated graph.
8. Show primary and secondary entities in separate panels.
9. Paginate long lists.
10. Show a readable relationship preview.
11. Show Neo4j connection status.
12. Provide Insert / update graph and Cancel / Reset buttons.
13. Show success counts and actionable errors.

The UI must not write to Neo4j merely because a dropdown changes. Writing occurs only after Preview and explicit Insert / update graph confirmation.

### Required API contract

Use an API contract similar to this:

```text
POST /api/csv/parse
  multipart/form-data: file

POST /api/graph/preview
  {
    "rows": [...],
    "primary_column": "City",
    "secondary_column": "Province",
    "predicate": "LOCATED_IN",
    "prefix": "PAKISTAN_CITIES",
    "source_file": "pakistan_cities.csv"
  }

GET /api/neo4j/test

POST /api/graph/import
  {
    "nodes": [...],
    "relationships": [...]
  }
```

The agent may choose different endpoint names, but the same separation is required: parse, preview, connection test, and explicit import.

### Required completion criteria

The project is complete only when all of these are true:

- `README.md` explains installation, configuration, startup, and usage.
- `config/neo4j.example.json` contains no real password.
- `.env.example` documents `NEO4J_PASSWORD`.
- The backend starts with one documented command.
- The frontend starts with one documented command.
- A user can upload a real CSV and preview nodes and relationships.
- A user can insert the preview into Neo4j with one explicit confirmation.
- Re-importing the same CSV does not create duplicate nodes or relationships.
- Connection failures are shown in the UI.
- All tests pass.
- The agent must run the tests and build before claiming completion.

## Goal

Build a small standalone application that uploads a CSV file, lets the user map two columns, previews the graph, and inserts the result into Neo4j.

The first version supports one primary column and one secondary column.

Example:

```text
Primary column:   City
Secondary column: Province
Predicate:        LOCATED_IN
```

For this row:

```text
Karachi, Sindh, Pakistan
```

The application creates:

```text
(Karachi)-[:LOCATED_IN]->(Sindh)
```

The `Country` column is ignored unless the user selects it as the secondary column in another import.

## User interface

### 1. Upload

- File picker accepts `.csv`.
- Parse the first row as column headers.
- Show file name, row count, and column count.
- Show the first five rows in a preview table.
- Show a Cancel/Reset button.

### 2. Map columns

Show these controls:

- Primary column dropdown.
- Secondary column dropdown.
- Predicate text input.
- Node prefix text input.
- Preview Graph button.

The secondary dropdown must exclude the selected primary column.

Suggested predicate:

```text
Primary City + Secondary Province -> LOCATED_IN
Primary University + Secondary Province -> LOCATED_IN_PROVINCE
```

The user can edit the predicate before previewing.

Suggested prefix:

```text
PAKISTAN_CITIES
```

### 3. Preview

After pressing Preview Graph:

- Trim whitespace from values.
- Ignore empty primary or secondary values.
- Treat values case-insensitively for deduplication.
- Preserve the first clean display value.
- Create one node for each distinct primary value.
- Create one node for each distinct secondary value.
- Create one relationship for each distinct primary/secondary pair.

Show:

- Primary node count.
- Secondary node count.
- Total node count.
- Relationship count.
- A two-column entity preview.
- A relationship preview such as:

```text
University of Balochistan [LOCATED_IN_PROVINCE] Balochistan
```

Use pagination for long entity lists.

### 4. Insert into Neo4j

Show a Neo4j connection selector or configured connection name.

The final button should say:

```text
Insert / update graph
```

Ask for confirmation before writing.

After writing, show:

- Nodes created or updated.
- Relationships created or updated.
- Number of skipped rows.
- Any errors.

## Graph data model

Use one common node label:

```text
CSVEntity
```

Each node should have:

```text
{
  id: "PAKISTAN_CITIES_CITY:karachi",
  name: "Karachi",
  normalized_name: "karachi",
  entity_type: "CITY",
  source_file: "pakistan_cities.csv",
  import_id: "unique-import-id"
}
```

Use a different `entity_type` for the two columns. For example:

```text
PAKISTAN_CITIES_CITY
PAKISTAN_CITIES_PROVINCE
```

The entity type prevents a city named `Lahore` from colliding with a province or another column type that happens to have the same text.

The relationship should have:

```text
{
  predicate: "LOCATED_IN",
  source_file: "pakistan_cities.csv",
  import_id: "unique-import-id"
}
```

## ID and deduplication rules

Never use the display name alone as the Neo4j identity.

Create a stable ID from:

```text
prefix + entity_type + normalized value
```

Example:

```text
PAKISTAN_CITIES_CITY:karachi
PAKISTAN_CITIES_PROVINCE:sindh
```

Normalize values with:

1. Trim leading and trailing spaces.
2. Collapse repeated internal whitespace.
3. Convert to lowercase for the ID.

Keep the original cleaned value in `name`.

Repeated rows must not create duplicate nodes or duplicate relationships.

## Cypher write strategy

Use parameters. Never concatenate CSV values directly into Cypher.

For every primary and secondary value, use `MERGE`:

```cypher
MERGE (n:CSVEntity {id: $id})
SET n.name = $name,
    n.normalized_name = $normalized_name,
    n.entity_type = $entity_type,
    n.source_file = $source_file,
    n.import_id = $import_id
```

For every relationship, use:

```cypher
MATCH (source:CSVEntity {id: $source_id})
MATCH (target:CSVEntity {id: $target_id})
MERGE (source)-[r:RELATED_TO {
  predicate: $predicate,
  source_id: $source_id,
  target_id: $target_id,
  import_id: $import_id
}]->(target)
SET r.source_file = $source_file
```

Neo4j relationship types cannot safely be supplied as normal parameters. Keep one fixed relationship type, such as `RELATED_TO`, and store the user predicate as the `predicate` property. This allows predicates such as `LOCATED_IN` without unsafe dynamic Cypher.

## Recommended transaction

Write the entire import in one transaction:

1. Validate all rows.
2. Build the deduplicated node list.
3. Build the deduplicated relationship list.
4. `UNWIND` the node list and `MERGE` nodes.
5. `UNWIND` the relationship list and `MERGE` relationships.
6. Commit only if every operation succeeds.

If any write fails, roll back the transaction and show the error. Do not leave a partially imported graph.

## Batch Cypher

Use `UNWIND` for performance:

```cypher
UNWIND $nodes AS item
MERGE (n:CSVEntity {id: item.id})
SET n.name = item.name,
    n.normalized_name = item.normalized_name,
    n.entity_type = item.entity_type,
    n.source_file = item.source_file,
    n.import_id = item.import_id
```

Then:

```cypher
UNWIND $relationships AS item
MATCH (source:CSVEntity {id: item.source_id})
MATCH (target:CSVEntity {id: item.target_id})
MERGE (source)-[r:RELATED_TO {
  predicate: item.predicate,
  source_id: item.source_id,
  target_id: item.target_id,
  import_id: item.import_id
}]->(target)
SET r.source_file = item.source_file
```

## CSV parsing rules

Use a real CSV parser. Do not split lines manually.

It must support:

- Quoted values.
- Commas inside quoted values.
- UTF-8 files.
- Empty values.
- Windows and Unix line endings.

Reject:

- Files without headers.
- Files with duplicate headers.
- Files larger than the configured safety limit.
- Rows with an unexpected number of columns.

Show row-level warnings rather than silently changing data.

## Example: cities

Input:

```csv
City,Province,Country
Karachi,Sindh,Pakistan
Hyderabad,Sindh,Pakistan
Zhob,Balochistan,Pakistan
```

Mapping:

```text
Primary: City
Secondary: Province
Predicate: LOCATED_IN
Prefix: PAKISTAN_CITIES
```

Nodes:

```text
PAKISTAN_CITIES_CITY:karachi
PAKISTAN_CITIES_CITY:hyderabad
PAKISTAN_CITIES_CITY:zhob
PAKISTAN_CITIES_PROVINCE:sindh
PAKISTAN_CITIES_PROVINCE:balochistan
```

Relationships:

```text
Karachi   -[LOCATED_IN]-> Sindh
Hyderabad -[LOCATED_IN]-> Sindh
Zhob      -[LOCATED_IN]-> Balochistan
```

There are five nodes, not six, because `Sindh` is deduplicated.

## Example: universities

Mapping:

```text
Primary: University
Secondary: Province
Predicate: LOCATED_IN_PROVINCE
Prefix: UNIVERSITIES_OF_PAK
```

The same application creates distinct university and province node types and connects every university to its province.

## Configuration

Keep Neo4j settings outside source code. Use a local configuration file such as:

```text
config/neo4j.json
```

Do not commit this file if it contains a password.

Suggested settings:

```json
{
  "uri": "neo4j://localhost:7687",
  "database": "neo4j",
  "username": "neo4j",
  "password": "change-me",
  "timeout_seconds": 30
}
```

Prefer an environment variable for the password:

```text
NEO4J_PASSWORD=your-password
```

The application should test the connection before showing the import button as enabled.

## Tests required

Implement tests for:

- CSV parsing with quoted commas.
- Header validation.
- Whitespace and case normalization.
- Empty value handling.
- Primary/secondary column exclusion.
- Distinct node counts.
- Relationship deduplication.
- Correct generated IDs.
- Correct predicate preview.
- Parameterized Cypher generation.
- Neo4j connection failure.
- Transaction rollback.
- Re-importing the same CSV without duplicates.

Use a fake Neo4j driver for unit tests. Use a disposable Neo4j instance for integration tests when available.
