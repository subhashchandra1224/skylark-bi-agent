# Architecture & Engineering Decision Log
**Project**: Skylark BI Agent
**Goal**: Design a deterministic, real-time Business Intelligence conversational interface over live Monday.com operational data.

## 1. Deterministic BI Engine vs. LLM Arithmetic
**Decision**: Prevent the LLM from performing financial and aggregation arithmetic.
**Rationale**: LLMs inherently suffer from mathematical hallucinations, particularly when processing high-cardinality financial datasets (e.g., pipeline sums). 
**Implementation**: Gemini is restricted strictly to semantic orchestration (parsing intent to JSON) and executive summarization (translating JSON metrics to English). All aggregations (sums, counts, groupings) are deterministically executed in Python via `pandas` against normalized dataframes.

## 2. Monday.com GraphQL API vs. MCP Integration
**Decision**: Direct GraphQL API integration was chosen over a heavier Model Context Protocol (MCP) abstraction.
**Rationale**: Monday.com's dataset structure (dynamic column IDs vs text titles) requires highly specialized normalization that MCP does not natively handle well. Direct API calls allow for tight optimization, strict pagination control, and in-memory caching.

## 3. Dynamic Column Discovery
**Decision**: Resolve Monday columns by dynamic title rather than hardcoded IDs.
**Rationale**: Monday.com internally references columns via random hashes (e.g., `text_mm6qaqcr`). If a board admin duplicates or recreates a column, the ID changes, breaking hardcoded integrations. The agent fetches board metadata to dynamically map normalized text titles (e.g., "probable start date") to their live IDs on every cache miss.

## 4. Normalization and Date Parsing Overrides
**Decision**: Implement a custom text and date normalization service before Pandas injection.
**Rationale**: Monday.com stores dates as text strings containing non-standard timezone notations (e.g., `(Coordinated Universal Time)`). Standard parsers (including `dateutil` and `pandas`) fail on this trailing text, resulting in widespread `NaT` errors and false "missing data" reports. The normalization layer robustly strips this text prior to timestamp casting.

## 5. In-Memory Caching (TTL)
**Decision**: Utilize a 5-minute TTL cache via `cachetools` for Monday.com datasets.
**Rationale**: A single conversational query like "Give me a leadership update" requires scanning multiple high-volume boards. Hitting the live GraphQL endpoint for every sequential message introduces massive latency and risks hitting API rate limits. 5 minutes ensures near-real-time visibility without overwhelming external systems.

## 6. Data Quality Transparency
**Decision**: Expose dataset malformations directly to the end user.
**Rationale**: In the Deals board, 184/349 records lack a financial value. Instead of silently ignoring these or imputing fake averages, the BI engine detects `NaN`/`Unknown` values and injects explicit warnings (e.g., "Pipeline totals exclude 184 deals with missing values") into the LLM context, forcing the executive summary to communicate the data caveat.

## 7. Ambiguity & Fallback Handling
**Decision**: Gracefully handle ambiguous intent or unsupported operations.
**Rationale**: If a user asks "How are we doing?" without specifying a board, the LLM maps this to a `leadership_update` intent, automatically pulling cross-board KPIs. If a user asks for a non-existent company, the agent executes the filter, detects 0 rows in Pandas, and returns a factual statement rather than hallucinating records to please the user.

## Limitations & Future Work
1. **Stateless Conversational Memory**: The current implementation operates as a one-shot orchestration per query. Context does not persist across requests. In production, injecting a lightweight Redis store to track `session_id` would enable true conversational memory.
2. **Deprecation Handling**: The `google.generativeai` SDK used for Gemini orchestration is slated for deprecation. A near-term migration to `google.genai` is strictly recommended before LTS production deployment.
