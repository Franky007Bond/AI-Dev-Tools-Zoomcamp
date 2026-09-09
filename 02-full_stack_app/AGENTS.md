## Specifications
- Full spec: [`_docs/specs.md`](_docs/specs.md). 

## Documentation lookups
- Use **/find-docs** skill when implementing against any external library, framework, or API (e.g. the SMS provider, web framework, floor-plan/canvas library) instead of relying on training data — library APIs change and Context7 returns current, version-specific docs.

## Guidelines
- for backend, use uv for dependency management
- use Node.js for the frontend.
- a few useful commands:
	- uv sync
	- uv add <PACKAGE-NAME>
	- uv run python <PYTHON-FILE>
- regularly commit code to git 