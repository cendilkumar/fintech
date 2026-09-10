# Technology Option Catalog — Production Candidates

The case is technology-neutral. Use this catalogue only after requirements are understood.

| Architecture concern | Common production options | Notes |
|---|---|---|
| Data/lakehouse | Databricks, Snowflake, Microsoft Fabric, BigQuery | Do not confuse physical storage with business semantics. |
| Semantic layer | dbt Semantic Layer, Cube, Microsoft Fabric/Power BI semantic model, custom domain API | Centralize canonical measures/definitions. |
| Ontology engineering | Protégé, OWL/RDF, SHACL; commercial ontology tooling | Protégé is an open-source ontology editor from Stanford's BMIR ecosystem. |
| Knowledge graph / graph DB | Neo4j, Amazon Neptune, Stardog, GraphDB, Azure Cosmos DB graph capabilities | Property graph vs RDF is an ADR, not a slogan. |
| Structured operational store | PostgreSQL, cloud relational stores | Good for exact workflow/state. |
| Vector / search | pgvector, Elasticsearch/OpenSearch, managed vector services | Use for semantic similarity, not active-policy authority. |
| Retrieval/orchestration | LangGraph, Google ADK, custom workflow, LlamaIndex/LangChain components | Keep deterministic controls outside model discretion. |
| LLM | OpenAI, Anthropic, Gemini, enterprise-hosted models | Model selection follows evals and risk requirements. |
| Tool interoperability | MCP where appropriate, typed enterprise APIs | MCP = Model Context Protocol. |
| Policy enforcement | Open Policy Agent (OPA), application policy engines, IAM/ABAC | OPA = Open Policy Agent; do not use prompts as authorization. |
| Workflow | Temporal, Camunda 8, application state machines | Useful for durable human gates and retries. |
| Observability/evals | Langfuse, MLflow, OpenTelemetry, provider telemetry | Capture traces/metrics without storing hidden chain-of-thought. |
| Event backbone | Kafka/Confluent/Redpanda, cloud event systems | Supports source updates and context invalidation. |

## Workshop build

Google AI Build may simulate graph/vector/policy APIs with supplied JSON fixtures. The participant must still document what would change for production.
