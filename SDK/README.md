# Warframe Tactical Advisor Developer SDK

Welcome to the Developer SDK for Warframe Tactical Advisor v6.0. This SDK contains the tools, examples, and documentation required to build custom plugins, integrate external apps using our REST API layer, and extend the progression advice systems.

## Architecture Topology

```mermaid
graph TD
    UI[PySide6 UI Views] -->|Events/Queries| Core[Core Advisor Engine]
    FastAPI[FastAPI REST API Server] -->|Queries| Core
    Core -->|Service calls| Services[Services Layer: Player, Build, Resource]
    Services -->|Inference checks| ExpertSystem[Expert System Inference Engine]
    Services -->|Semantic links| KnowledgeGraph[Knowledge Graph Adjacency Net]
    Services -->|Local LLM| Ollama[Local Ollama REST API]
    Core -->|Dynamic loaders| Plugins[Third-Party Plugins Registry]
```

## Contents
* [plugin_documentation.md](plugin_documentation.md) - Learn how to build directory-structured marketplace plugins.
* [api_documentation.md](api_documentation.md) - Integration documentation for the local REST API server.
* `examples/sample_plugin` - A complete sample plugin implementing custom weapons, builds, and commands.
