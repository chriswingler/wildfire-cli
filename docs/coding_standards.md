# Coding Instructions

## Core Principles
- **KISS**: Keep it simple, stupid
- **DRY**: Don't repeat yourself  
- **YAGNI**: You aren't gonna need it
- **SOLID**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **Boy Scout Rule**: Leave the campground cleaner than you found it
- **Principle of Least Surprise**: Code should behave as expected

## General Guidelines

### Code Quality
- Keep file sizes small (ideally less than 1000 lines)
- Always solve the root cause, not bandaid solutions
- Use the most efficient data structures and algorithms
- Work in small, modular, testable phases
- Follow standard conventions consistently
- Prefer composition over inheritance

### Design Principles
- Keep configurable data at high levels
- Prefer polymorphism to if/else or switch/case
- Separate multi-threading code
- Use dependency injection
- **Law of Demeter**: A class should know only its direct dependencies
- Avoid logical dependency between methods in the same class
- Avoid negative conditionals

## Naming Conventions

### General Rules
- Use descriptive and unambiguous names
- Make meaningful distinctions
- Use pronounceable and searchable names
- Replace magic numbers with named constants
- Pick one word per concept and use consistently

### Examples
❌ **Bad**:
```cpp
int d;
function calc(int num1, int num2) { return num1*num2; }
string date1, date2;
User[] activeUsersList;
```

✅ **Good**:
```cpp
int elapsedTimeInDays;
function multiply(int num1, int num2) { return num1*num2; }
string startDate, endDate;
User[] activeUsers;
```

## Functions

### Core Rules
- Keep functions small (ideal: 4 lines, max: 60 lines)
- Do one thing well
- Use descriptive function names
- Prefer ≤3 arguments
- Avoid side effects (pure functions when possible)
- Maintain constant level of abstraction

### Function Design
- A function should be readable top to bottom like a paragraph
- Avoid boolean arguments (split into separate functions instead)
- Commands and queries should be separate
- Setters should not return values
- Error handling is one responsibility

❌ **Bad**:
```cpp
function getUsers(boolean status) { ... }
function removeOrders(int id, boolean cleanCache, boolean updateLog) { ... }
```

✅ **Good**:
```cpp
function getActiveUsers() { ... }
function getInactiveUsers() { ... }
function removeOrders(int id) { ... }
function cleanOrdersCache(int id) { ... }
```

## Comments

### When to Comment
- For confusing or obscure logic
- To explain intent and warn of consequences  
- For complex business logic and assumptions
- For mathematical calculations, algorithms, and graphics programming
- For domain-specific operations that aren't obvious to general programmers
- For coordinate system transformations, matrix operations, and projection calculations
- Never for obvious operations (like simple assignments or increments)

### Comment Rules
- Express yourself in code first, comments second
- Don't be redundant (`i++; // increment i`)
- Don't comment out code - delete it
- Avoid closing brace comments
- Keep comments accurate and up-to-date

❌ **Bad**:
```cpp
// Sums 2 numbers
SumTwoNumbers() {}

i++; // increment i

// Create a grid color
Color gridColor = GRID_COLOR;
```

✅ **Good**:
```cpp
// Remove semicolons at the end of line
mermaid_code = re.sub(r';\\s*(\\n|$)', r'\\1', mermaid_code)

// Calculate frustum bounds for perspective projection
float top = nearPlane * tanf(camera.fovy * HALF_FACTOR * PI_APPROX / DEGREES_TO_RADIANS_FACTOR);

// Calculate grid center snapped to grid boundaries
float gridCenterX = floorf(cameraPos.x / CellSize) * CellSize;
```

## Code Organization

### File Structure
- Group code by functionality
- Related code should be vertically dense
- Declare variables close to their usage
- High-level code first, implementation details later
- Order functions by calling sequence (caller before callee)

### Formatting
- Keep lines short (70-120 characters)
- Use proper indentation
- Use whitespace to associate related code
- Follow team-wide formatting standards

## Objects and Data Structures

### Design Guidelines
- **Data structures**: Expose data, no behavior
- **Objects**: Hide data, expose behavior via methods
- Keep classes small (ideal: 100 lines, max: 1000 lines)
- Single responsibility per class
- High cohesion, low coupling
- Avoid hybrid structures (half object, half data)

### Class Design
- Class names should reflect their responsibility
- Avoid names like Processor, Manager
- Multiple small classes > few large classes
- Base classes shouldn't know about derivatives
- Encapsulate utility methods (make them private)

## Error Handling

### Best Practices
- Use exceptions instead of error codes at lower levels
- Don't mix error handling with business logic
- Provide adequate context in exceptions
- Wrap foreign errors to adhere to common standards
- Avoid null returns - use exceptions or error objects

### Error Handling Structure
```cpp
try {
    // Business logic only
} catch (SpecificException& e) {
    // Handle specific error
} catch (...) {
    // Handle unknown errors
}
```

## Testing

### Test Characteristics
- **Fast**: Quick to run
- **Independent**: No test dependencies
- **Repeatable**: Same results every time
- **Self-validating**: Clear pass/fail
- **Timely**: Written close to production code

### Test Guidelines
- One assert per test
- Use descriptive test names
- Keep tests readable
- Use coverage tools
- Tests should be easy to run

## Code Smells to Avoid

### Warning Signs
- **Rigidity**: Difficult to change, cascading changes
- **Fragility**: Breaks in many places from single change
- **Immobility**: Cannot reuse code in other projects
- **Needless Complexity**: Over-engineered solutions
- **Needless Repetition**: Violates DRY principle
- **Opacity**: Hard to understand

## Concurrency

### Guidelines
- Keep concurrency code separate
- Limit access to shared data
- Use independent data subsets when possible
- Avoid multiple synchronized methods on shared objects
- Keep synchronized sections small
- Plan shutdown early

## Logging

### Best Practices
- Follow common logging practices
- Use appropriate log levels
- Provide adequate context (timestamp, location, state)
- Don't log sensitive information (PII, financial data, auth info)
- Include relevant parameter values and error descriptions

## LLM-Specific Guidelines

### Preventing Infinite Loops and Thrashing

#### Problem Analysis First
- **Always understand the root cause** before attempting fixes
- Read error messages completely and carefully
- Use search tools to understand codebase patterns before making changes
- Identify the specific file and line causing issues

#### Systematic Approach
- **One change at a time** - Make single, focused changes
- **Test after each change** - Verify the fix works before proceeding
- **Document what you tried** - Keep track of attempted solutions
- **Avoid shotgun debugging** - Don't change multiple things simultaneously

#### When Stuck
- **Stop and reassess** - If 3 attempts fail, step back and re-analyze
- **Ask for clarification** - Request more context from the user
- **Suggest alternative approaches** - Propose different solutions
- **Break down complex problems** - Split large tasks into smaller steps

#### Decision Making
- **Choose the simplest solution** that solves the problem
- **Prefer existing patterns** in the codebase over new approaches
- **Don't over-engineer** - Solve the immediate problem, not future hypotheticals
- **When multiple solutions exist** - Pick the most maintainable one

#### Communication
- **Be explicit about limitations** - Say when you're uncertain
- **Explain your reasoning** - Help users understand your approach
- **Suggest next steps** - Provide clear direction when stuck
- **Ask before major changes** - Get approval for significant modifications

### LLM Best Practices

Don't use excessive token count.

#### Code Analysis
- **Read surrounding context** before making changes
- **Understand the file's purpose** and existing patterns
- **Check imports and dependencies** to understand available tools
- **Look for similar implementations** elsewhere in the codebase

#### Change Management
- **Make minimal viable changes** to fix the immediate issue
- **Preserve existing functionality** unless explicitly asked to change it
- **Use existing helper functions** rather than reinventing
- **Follow the established code style** in the file

#### Error Handling
- **Read the full error message** - Don't just focus on the first line
- **Check line numbers** - Errors often point to the exact problem
- **Understand error types** - Compilation vs runtime vs logic errors
- **Fix the cause, not symptoms** - Address root issues

#### Verification
- **Always compile/test** after making changes
- **Check for new errors** introduced by your changes
- **Verify the original problem is solved**
- **Ensure no regressions** in other functionality

#### File Naming During Refactoring
- **Keep original names** for the new, clean implementation
- **Rename old implementations** to "Old" suffix if you need to keep them temporarily
- **Prefer deleting old files** when the new implementation is complete and tested
- **Example**: When refactoring `MyClass.h/.cpp`, keep the clean version as `MyClass.h/.cpp` and rename the old version to `MyClassOld.h/.cpp` (then delete when safe)

---

> "Clean code is code that is written by someone who cares"  
> – Michael Feathers

Clean code is not just following rules - it comes from values, discipline, and craftsmanship in software development.