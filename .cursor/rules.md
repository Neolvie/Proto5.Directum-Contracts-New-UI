# Multi-Agent Prototype Development System - Rules

## PROJECT OVERVIEW

This is a multi-agent system for rapid hypothesis testing and prototype development.

**6 Coordinated Agents:**
- **Project Manager**: Orchestration and progress tracking  
- **Business Analyst**: Requirements clarification
- **Architect**: System design
- **Developer**: Implementation
- **QA**: Testing and quality assurance
- **Quality Gate**: Final approval

## CORE PRINCIPLES

1. **File-based communication**: Agents communicate through `.hypothesis/` directory
2. **Single agent per task**: Only one agent works on a task at a time
3. **Test-driven development**: Code must be tested before reports
4. **Actual execution required**: All tests and builds must be run, no simulation
5. **Iterative quality**: QA runs after each development cycle
6. **User involvement for business only**: Technical decisions by agents
7. **User communication**: In Russian
8. **Result documents**: In Russian
9. **Agent instructions**: In English

## EXECUTION MODES (MANUAL vs AUTO)

These modes control whether the system waits after each agent or proceeds end-to-end.

### MODE: MANUAL (default)
- Each agent completes its task and stops.
- User manually invokes the next agent (or says "continue").
- Best when you want full control or to answer BA questions carefully.

### MODE: AUTO
- Project Manager orchestrates the full chain automatically.
- If BA questions are asked and no user answers are provided in the same turn,
  the BA must document assumptions in `01_REQUIREMENTS.md` and proceed.
- Best for uninterrupted end-to-end runs.

### How to switch
Include the mode in your message, e.g.:
- `MODE: MANUAL`
- `MODE: AUTO`

## MANDATORY TECHNOLOGY STACK

### Required Stack (No Exceptions)

**Core:**
- Python 3.10+ (primary language)
- UI framework: **choose any standard, well-supported technology** suitable for the prototype
- Backend API framework (if needed): FastAPI / Flask / Django / similar standard options
- pytest (unit/integration testing)
- Playwright (E2E testing with real browser automation)
- Docker + docker-compose (deployment)
- All framework examples mentioned in the guidelines are recommendations; choose the framework that, in your opinion, will best enable the implementation of this prototype.

**Examples of acceptable UI options** (non-exhaustive):
- Gradio, Streamlit
- Django templates / Jinja + Flask
- React / Vue / Angular (if a separate frontend is justified)

### Allowed for UI Enhancement

- Small inline JavaScript for animations
- CSS for styling
- Custom components with minimal JS

### Strictly Forbidden

- Niche/experimental frameworks that are not widely used or maintained
- Custom one-off UI frameworks with unclear support

**Rationale**: Use standard, widely-supported technologies to keep prototypes reliable and easy to maintain

## UI / UX REQUIREMENTS

- **Interface must be maximally simple**: only necessary elements, no clutter
- **UX must be very clear and intuitive**: minimal steps, obvious controls, predictable flows
- Avoid decorative-only elements; prioritize clarity and speed of use

## AGENT ROLES

> **Note**: Each agent has a detailed instruction file in `.cursor/[agent-name]-agent.md`. This section provides a summary.

### Project Manager Agent

**Files**: Read all status files, write `BUILD_LOG.md`

**Key responsibilities**:
- Orchestrate agent sequence
- Monitor progress (update BUILD_LOG every 30 min)
- Control iteration limits (max 5-7 cycles)
- **CRITICAL**: Reject reports without terminal output evidence
- Notify user when ready

**See**: `.cursor/project-manager-agent.md`

### Business Analyst Agent

**Files**: Read `00_HYPOTHESIS.md`, write `01_REQUIREMENTS.md`

**Key responsibilities**:
- Clarify hypothesis and requirements
- Ask 5-7 clarifying questions to user
- Create detailed FR/NFR/acceptance criteria

**See**: `.cursor/business-analyst-agent.md`

### Architect Agent

**Files**: Read `01_REQUIREMENTS.md`, write `02_ARCHITECTURE.md`

**Key responsibilities**:
- Design system using **standard, well-supported technologies** suited to the prototype
- Select UI stack based on requirements and keep it minimal
- Create component diagrams (Mermaid)
- Ensure UI/UX requirements (simplicity and clarity) are enforced

**See**: `.cursor/architect-agent.md`

### Developer Agent

**Files**: Read `02_ARCHITECTURE.md`, write `src/`, `04_IMPLEMENTATION.md`

**Key responsibilities**:
- Implement using the **selected standard stack**
- **MANDATORY: RUN CODE LOCALLY** after each implementation
- **MANDATORY: RUN TESTS** (pytest)
- **MANDATORY: BUILD & TEST DOCKER**
- Include ALL terminal outputs in reports
- **FORBIDDEN**: Writing reports without running code

**See**: `.cursor/developer-agent.md`

### QA Agent

**Files**: Read source code, write `tests/`, `05_TEST_RESULTS.md`

**Key responsibilities**:
- Write unit, integration, and **E2E tests with Playwright**
- **MANDATORY: ACTUALLY RUN ALL TESTS**
- **MANDATORY: RUN APPLICATION MANUALLY**
- **MANDATORY: RUN PLAYWRIGHT E2E TESTS**
- **MANDATORY: REQUEST TEST DATA** from user if needed
- **MANDATORY: BUILD AND RUN DOCKER**
- Include ALL terminal outputs in reports
- **FORBIDDEN**: Writing test reports without running tests

**See**: `.cursor/qa-agent.md`

### Quality Gate Agent

**Files**: Read all reports, write `06_QUALITY_GATE_REPORT.md`

**Key responsibilities**:
- Verify all requirements met
- Check code quality (>70% coverage)
- **CRITICAL**: Verify all reports contain REAL terminal outputs
- **CRITICAL**: Reject if evidence missing
- Make go/no-go decision

**See**: `.cursor/quality-gate-agent.md`

## COMMUNICATION PROTOCOL

### File Structure

All communication in `.hypothesis/` directory:
- `00_HYPOTHESIS.md` - User's initial hypothesis
- `01_REQUIREMENTS.md` - Clarified requirements (BA)
- `02_ARCHITECTURE.md` - Architecture design (Architect)
- `04_IMPLEMENTATION.md` - Implementation details (Developer)
- `05_TEST_RESULTS.md` - Test results (QA)
- `06_QUALITY_GATE_REPORT.md` - Final approval/rejection (Quality Gate)
- `BUILD_LOG.md` - Activity log with timestamps (PM)

### File Format

Each file must contain:
1. **Header**: Agent name, timestamp, phase
2. **Summary**: 1-2 sentences
3. **Content**: Full details
4. **Next steps**: What should happen next
5. **Questions/Blockers**: If any

## MANDATORY EXECUTION REQUIREMENTS

### No Reports Without Execution

**Developer MUST before writing report**:
```bash
# 1. Run application
# Use the command for the chosen stack, e.g.:
streamlit run src/app.py  # or: python src/app.py

# 2. Run tests
pytest --cov=src tests/ -v

# 3. Build Docker
docker-compose build

# 4. Run Docker  
docker-compose up

# 5. Include ALL outputs in 04_IMPLEMENTATION.md
```

**QA MUST before writing report**:
```bash
# 1. Run all tests
pytest --cov=src tests/ -v
pytest --cov=src --cov-report=term-missing

# 2. Run E2E with Playwright
pytest tests/e2e/ -v --headed

# 3. Run application manually
# Use the command for the chosen stack, e.g.:
streamlit run src/app.py

# 4. Test UI: click buttons, upload files, fill forms

# 5. Build and run Docker
docker-compose build && docker-compose up

# 6. Run linters
black --check src/ tests/
flake8 src/ tests/

# 7. Include ALL outputs in 05_TEST_RESULTS.md
```

**If test data needed**, QA must request from user:
```
@user For testing I need:
- [list of files/data]
Can you provide these?
```

### Evidence Required in All Reports

**Required**:
- Terminal output with timestamps
- Full error messages with stack traces
- Success confirmations from commands
- Coverage metrics from pytest
- Docker build/run logs
- Playwright test results

**Forbidden**:
- "All tests passed" without pytest output
- "Docker works" without build logs
- Simulated or invented results
- Reports written before running code

## CODE QUALITY STANDARDS

### Python Requirements

- **Version**: Python 3.10+
- **Type hints**: All functions
- **Docstrings**: All classes and functions (in Russian)
- **Error handling**: Try-catch for external calls
- **Linting**: black for formatting, flake8 for linting
- **Dependencies**: All in `requirements.txt` with pinned versions

### Testing Standards

**Unit Tests** (`tests/unit/`): Test all business logic, min 70% coverage

**Integration Tests** (`tests/integration/`): Test component interactions, API endpoints

**E2E Tests** (`tests/e2e/`): 
- **MANDATORY: Use Playwright** for real browser automation
- Test critical user workflows
- Upload files, fill forms, click buttons
- Run with: `pytest tests/e2e/ -v --headed`

**Coverage requirement**: Minimum 70%

### Git Workflow

- **Branch**: Work on main
- **Commits**: After each successful dev+test cycle
- **Format**: `feat: description`, `fix: description`, `test: description`
- **Push**: Only when tests pass

## LOCAL DEVELOPMENT CYCLE

### Setup (First time)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Development Iteration
```bash
# 1. Run application
# Use the command for the chosen stack, e.g.:
streamlit run src/app.py

# 2. Run tests
pytest --cov=src tests/ -v

# 3. Run linting
black --check src/ tests/
flake8 src/ tests/

# 4. Commit if all pass
git commit -m "feat: description"
```

### Handling Port Conflicts (NO BATCH FILES!)

**If port is already in use:**

**Windows:**
```bash
# Find process using port (e.g., 8501 for Streamlit)
netstat -ano | findstr :8501

# Kill process by PID
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process
lsof -ti:8501 | xargs kill -9
```

**❌ FORBIDDEN**: Creating `.bat` or `.sh` scripts for process management
**✅ REQUIRED**: Use terminal commands directly as shown above

### Docker Validation
```bash
# Build
docker-compose build

# Run
docker-compose up

# Verify:
# Use the appropriate URL/port for the chosen stack
# Streamlit: http://localhost:8501
# Gradio: http://localhost:7860
# FastAPI: http://localhost:8000/docs
```

## ITERATIVE DEVELOPMENT PROCESS

### Correct Cycle

```
1. BA → clarifies → creates 01_REQUIREMENTS.md

2. Architect → designs → creates 02_ARCHITECTURE.md

3. Developer → implements module → RUN CODE → pytest → commit
   ↓
4. QA → writes tests → RUN ALL → report bugs/pass
   ↓
5. If bugs → Developer fixes → RUN AGAIN → QA verifies
   ↓
6. If pass → next module → repeat from step 3

7. Quality Gate → verify → approve/reject
```

### Wrong Approach (Forbidden)

```
Developer → writes all code → report (no run) →
QA → writes tests → "passed" (no run) →
Quality Gate → "approved" (no verification) →
RESULT: Nothing works
```

## DOCUMENTATION REQUIREMENTS

### TECHNICAL_DOCUMENTATION.md
- Architecture overview with Mermaid diagrams
- Component descriptions
- API specifications
- Known limitations
- Deployment instructions

### README.md
- Quick start guide
- How to run locally
- How to run in Docker
- How to run tests

### Inline Documentation
- Docstrings in Russian
- Type hints throughout
- Comments for complex logic

## SUCCESS CRITERIA

Prototype is ready when:
- ✅ All FR implemented using the chosen standard stack
- ✅ All NFR met
- ✅ >70% test coverage (verified with pytest output)
- ✅ All tests passing (with terminal output in reports)
- ✅ Application runs locally (verified)
- ✅ Docker builds and runs (verified with logs)
- ✅ E2E tests with Playwright pass
- ✅ Documentation complete
- ✅ All reports contain REAL execution evidence
- ✅ UI is maximally simple with clear, intuitive UX
- ✅ No TODO/placeholder code

## ITERATION LIMITS

- **Per agent**: 5-7 complete cycles before escalation
- **Per requirement**: 3 iterations before re-evaluation
- **Escalate to user**: When blocked or limit exceeded

## FILE CREATION RESTRICTIONS

### Strictly Forbidden Files

**NEVER create the following files**:
- ❌ Error description MD files (`*_ERROR.md`, `*_ISSUE.md`, `CRITICAL_ISSUE_FOUND.md`, etc.)
- ❌ Status update MD files (`*_STATUS.md`, `*_UPDATE.md`, `FINAL_STATUS.md`, etc.)
- ❌ Apology/explanation MD files
- ❌ Temporary batch files for process termination (`kill_*.bat`, `stop_*.bat`, `terminate_*.bat`)
- ❌ Multiple restart scripts (`kill_8001_and_restart.bat`, `kill_all_and_restart.bat`, etc.)
- ❌ Any temporary helper batch files not part of the project structure

**If issues occur**:
- ✅ Report in existing files (`.hypothesis/` directory)
- ✅ Use terminal output for error reporting
- ✅ Update BUILD_LOG.md with issues
- ✅ Communicate problems directly in chat (no extra files)

**Process management**:
- ✅ Use terminal commands directly (no batch file creation)
- ✅ If port conflict: find and kill process via terminal, don't create scripts
- ✅ Document port/process issues in reports only

## 🚫 CRITICAL: FILE CREATION RESTRICTIONS

**NEVER CREATE the following files under ANY circumstances:**

❌ **Temporary status/error MD files:**
- `*_ERROR.md`, `*_ISSUE.md`, `*_STATUS.md`, `FINAL_STATUS.md`, `CRITICAL_ISSUE_FOUND.md`
- `FIX_*.md`, `CHECK_*.md`, `FINAL_REPORT.md`, `QUICK_START.md`
- Any MD files with apologies, explanations, or "intermediate concerns"

❌ **Process termination batch files:**
- `kill_*.bat`, `stop_*.bat`, `terminate_*.bat`, `*_restart.bat`
- `kill_8001_and_restart.bat`, `kill_all_and_restart.bat`
- Any `.bat` files for managing processes

❌ **Any other temporary helper files** not explicitly part of project structure

**✅ ONLY these files are allowed:**
- Communication files in `.hypothesis/`: `00_HYPOTHESIS.md`, `01_REQUIREMENTS.md`, `02_ARCHITECTURE.md`, `04_IMPLEMENTATION.md`, `05_TEST_RESULTS.md`, `06_QUALITY_GATE_REPORT.md`, `BUILD_LOG.md`
- Source code in `src/`
- Tests in `tests/`
- Standard project files: `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `README.md`, `TECHNICAL_DOCUMENTATION.md`
- Configuration: `.gitignore`, `pytest.ini`, `.coveragerc`, etc.

**If problems occur:**
- ✅ Report in appropriate `.hypothesis/` file
- ✅ Communicate directly in chat
- ✅ Use terminal commands (no script creation)
- ❌ NEVER create additional MD files to "explain" or "apologize"

### Allowed Files Only

**Create ONLY these files**:
- Project source code in `src/`
- Tests in `tests/`
- Communication files in `.hypothesis/` (01-06 numbered files + BUILD_LOG.md)
- Standard project files: `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `README.md`, `TECHNICAL_DOCUMENTATION.md`
- Configuration files: `.gitignore`, `pytest.ini`, etc.

**Rule**: If a file is not listed above or not explicitly requested by the user → DO NOT CREATE IT

## COMMON MISTAKES TO AVOID

### Developer
- ❌ Writing report without running code
- ❌ Using niche/experimental frameworks
- ❌ Leaving TODO code
- ❌ Creating temporary MD files for error descriptions
- ❌ Creating batch scripts for process management
- ✅ Always run code, tests, Docker before reporting
- ✅ Report issues in proper channels (.hypothesis/ files or chat)

### QA
- ❌ Writing "tests passed" without pytest output
- ❌ Skipping Playwright E2E tests
- ❌ Not requesting test data when needed
- ❌ Creating status/error MD files
- ✅ Always run tests, app, Docker; include all outputs
- ✅ Report all issues in 05_TEST_RESULTS.md

### Project Manager
- ❌ Accepting reports without evidence
- ❌ Not verifying terminal outputs
- ❌ Creating temporary status files
- ✅ Reject reports without real execution proof
- ✅ Update only BUILD_LOG.md for tracking

### Quality Gate
- ❌ Approving without verifying evidence
- ❌ Missing simulation/fake results
- ❌ Creating separate issue/status files
- ✅ Verify all terminal outputs are real
- ✅ Report decision in 06_QUALITY_GATE_REPORT.md only

## FINAL NOTES

- **This file** provides overview; see agent-specific files for details
- **All agents** must read this before starting
- **User communication**: In Russian
- **Agent instructions**: In English
- **Test early, test often** - no shortcuts on quality
