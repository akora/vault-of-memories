# Project Constitution: Vault of Memories

## Core Principles

### Simplicity First (SF)

Always choose the simplest practicable solution. Only introduce complex patterns if clearly justified. The system should be understandable and maintainable by future developers.

### Readability Priority (RP)

Code must be immediately understandable - for humans and machines. Clear variable names, logical structure, and comprehensive documentation are non-negotiable.

### Dependency Minimalism (DM)

No new libraries or frameworks without explicit approval. Prefer standard library solutions and well-established, minimal dependencies.

### Industry Standards Adherence (ISA)

Stick to established conventions for the language/framework. Follow PEP 8 for Python, use standard project structures, and adopt community best practices.

### Strategic Documentation (SD)

Comment only on complex logic or critical functions. Code should be self-documenting through clear naming and structure.

### Test-Driven Thinking (TDT)

Design code from the beginning so that it is easily testable. Each module should have clear interfaces and single responsibilities.

## Development Standards

### Code Quality

- **Atomic Changes (AC)**: Make small, self-contained changes to improve testability
- **Error Handling**: Implement comprehensive error handling with graceful degradation
- **Logging**: Provide detailed logging for debugging and monitoring
- **Configuration**: Use external configuration files for all settings

### Architecture Guidelines

- **Modular Design**: Each component has a single responsibility
- **Clear Interfaces**: Well-defined APIs between modules
- **Extensibility**: Easy to add new file types without rewriting existing code
- **Separation of Concerns**: Business logic, data access, and presentation are separate

### File Organization

- Use dashes (-) instead of underscores (_) in service names
- Maintain consistent folder structure
- Keep configuration files in dedicated config/ directory
- Separate source code from documentation and specifications

### Documentation Practices

- Use Markdown for all documentation
- Maintain relative links that work in repository
- Follow Markdown lint guidelines
- Document dependencies between services
- Don't create redundant documentation

### Quality Assurance

- Only commit code once it is confirmed to be working
- Implement one step at a time, don't run ahead
- Test each component in isolation before integration
- Provide clear error messages and recovery mechanisms

## Technical Constraints

### Performance Requirements

- System must handle large file collections efficiently
- Memory usage should be reasonable for typical desktop systems
- Processing should provide progress feedback for long operations

### Reliability Requirements

- Data integrity is paramount - never lose or corrupt user files
- Atomic operations for file moves to prevent partial states
- Comprehensive backup and recovery mechanisms
- Detailed audit trail of all operations

### Maintainability Requirements

- Clear separation between configuration and code
- Extensible architecture for adding new file types
- Comprehensive error handling and logging
- Self-documenting code with minimal but strategic comments

### Security Requirements

- Validate all file inputs to prevent security issues
- Handle file system permissions appropriately
- Protect against path traversal and other file system attacks
- Secure handling of temporary files and cleanup

## Decision Framework

When making technical decisions, evaluate against these criteria in order:

1. **User Value**: Does this serve the core mission of preserving digital memories?
2. **Simplicity**: Is this the simplest solution that meets requirements?
3. **Maintainability**: Can future developers understand and modify this?
4. **Reliability**: Does this protect user data and provide consistent results?
5. **Performance**: Does this meet reasonable performance expectations?

## Governance

### Code Reviews

- All changes must be reviewed against these principles
- Reviewers should explicitly call out principle violations
- Justify any exceptions with clear reasoning

### Architecture Decisions

- Major architectural changes require documentation
- Consider long-term maintenance implications
- Evaluate against all core principles before implementation

### Dependency Management

- New dependencies require explicit justification
- Prefer mature, well-maintained libraries
- Document all external dependencies and their purposes
- Regular review of dependency security and maintenance status
