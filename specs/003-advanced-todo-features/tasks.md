# Tasks: Advanced Todo Features - Phase III

**Input**: Design documents from `/specs/003-advanced-todo-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md

**Tests**: Tests are OPTIONAL for this feature - only include them if TDD approach is requested or explicitly required in spec.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source, `frontend/tests/` for tests
- **Infrastructure**: `dapr/components/`, root `docker-compose.yml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (backend/app/models/, backend/app/services/, backend/app/api/, backend/app/events/, backend/app/dapr/, backend/app/workers/)
- [ ] T002 [P] Add backend dependencies to backend/requirements.txt (kafka-python>=2.0.2, dapr-sdk>=1.10.0, celery>=5.3.0, redis>=4.5.0, python-dateutil>=2.8.2, pytz>=2023.3)
- [ ] T003 [P] Add frontend dependencies to frontend/package.json (date-fns@^2.30.0, react-tag-autocomplete@^7.0.0, @dnd-kit/core@^6.0.0)
- [ ] T004 [P] Create dapr/components/ directory structure for Dapr configuration files
- [ ] T005 [P] Create backend/app/events/ directory for Kafka event publisher/consumer
- [ ] T006 [P] Create backend/app/workers/ directory for Celery background workers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create database migration script for new tables (backend/app/database/migrations/add_advanced_features.py) - tags, task_tags, reminders, recurring_tasks, domain_events, dapr_state tables
- [ ] T008 [P] Create database migration for task table extensions (backend/app/database/migrations/extend_task_model.py) - priority, due_date, timezone, is_recurring, recurring_task_id columns
- [ ] T009 [P] Create database migration for user table extensions (backend/app/database/migrations/extend_user_model.py) - timezone, notification_preferences, default_task_priority columns
- [ ] T010 [P] Create GIN index migration for full-text search (backend/app/database/migrations/add_search_indexes.py) - idx_tasks_search_vector, idx_tasks_priority, idx_tasks_due_date
- [ ] T011 [P] Implement Dapr state store component (dapr/components/statestore.yaml) - PostgreSQL state store configuration
- [ ] T012 [P] Implement Dapr pub/sub component (dapr/components/pubsub.yaml) - Kafka pub/sub configuration
- [ ] T013 Create Dapr state manager service (backend/app/dapr/state.py) - DaprStateManager class with save_state, get_state, delete_state methods
- [ ] T014 [P] Create Kafka event publisher (backend/app/events/publisher.py) - EventPublisher class with publish() method using kafka-python
- [ ] T015 [P] Create Kafka event consumer (backend/app/events/consumer.py) - EventConsumer class with subscribe() and process() methods
- [ ] T016 Create event schemas module (backend/app/events/schemas.py) - Pydantic models for task.created, task.updated, task.completed, task.deleted events
- [ ] T017 Create Celery app configuration (backend/app/workers/celery_app.py) - Celery configuration with Redis broker
- [ ] T018 [P] Update docker-compose.yml to add Kafka service (confluentinc/cp-kafka:7.4.0) with Zookeeper
- [ ] T019 [P] Update docker-compose.yml to add Redis service for Celery broker
- [ ] T020 Create domain event model (backend/app/models/event.py) - DomainEvent SQLModel with event_type, aggregate_id, payload, published, processed fields
- [ ] T021 Create event service (backend/app/services/event_service.py) - EventService for publishing and tracking domain events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 3 - Task Priorities (Priority: P1) 🎯 MVP

**Goal**: Implement priority levels for tasks (low, medium, high, urgent) with visual indicators and filtering/sorting support

**Independent Test**: Can be fully tested by assigning different priority levels and verifying sorting/filtering behavior

### Implementation for User Story 3

- [ ] T022 [P] [US3] Extend Task model with priority field (backend/app/models/todo.py) - Add priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
- [ ] T023 [P] [US3] Add priority index to Task model (backend/app/models/todo.py) - Add Index definition for idx_tasks_priority
- [ ] T024 [US3] Update TaskCreate and TaskUpdate schemas (backend/app/api/schemas/todo_schemas.py) - Add priority field with validation
- [ ] T025 [US3] Extend TaskService with priority filtering (backend/app/services/task_service.py) - Add filter_by_priority() and sort_by_priority() methods
- [ ] T026 [US3] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add priority query parameter for filtering
- [ ] T027 [US3] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add sort_by and sort_order query parameters supporting priority sorting
- [ ] T028 [US3] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept priority field in request body
- [ ] T029 [US3] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating priority field
- [ ] T030 [P] [US3] Create PrioritySelector component (frontend/src/components/PrioritySelector/PrioritySelector.tsx) - Dropdown with color-coded priority options
- [ ] T031 [US3] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add priority selector field
- [ ] T032 [US3] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display priority with color indicator (red=urgent, orange=high, yellow=medium, gray=low)
- [ ] T033 [US3] Update TaskList component (frontend/src/components/TaskList/TaskList.tsx) - Add sort by priority option
- [ ] T034 [US3] Create TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by priority dropdown
- [ ] T035 [US3] Update task API service (frontend/src/services/tasks.ts) - Add priority parameter to API calls
- [ ] T036 [US3] Update task store (frontend/src/stores/taskStore.ts) - Add priority to task state and filters

**Checkpoint**: User Story 3 complete - priorities can be assigned, filtered, and sorted independently

---

## Phase 4: User Story 6 - Filter & Sort Options (Priority: P1) 🎯 MVP

**Goal**: Enable users to filter tasks by various criteria (status, priority, tags, due date) and sort by different attributes (due date, priority, created date, alphabetically)

**Independent Test**: Can be fully tested by applying various filters and sort options and verifying correct task ordering

### Implementation for User Story 6

- [ ] T037 [P] [US6] Create TaskSort component (frontend/src/components/TaskSort/TaskSort.tsx) - Sort controls with options: due_date, priority, created_at, title
- [ ] T038 [US6] Extend TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by status, due date range, tags
- [ ] T039 [US6] Update TaskList component (frontend/src/components/TaskList/TaskList.tsx) - Integrate TaskFilters and TaskSort components
- [ ] T040 [US6] Create filter store (frontend/src/stores/filterStore.ts) - Zustand store for filter and sort state management
- [ ] T041 [US6] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add tag_id, due_date_from, due_date_to query parameters
- [ ] T042 [US6] Extend TaskService filter method (backend/app/services/task_service.py) - Add support for combined filters (status, priority, tag_id, date range)
- [ ] T043 [US6] Update TaskList API call (frontend/src/services/tasks.ts) - Pass filter and sort parameters to backend
- [ ] T044 [US6] Add pagination support to GET /todos (backend/app/api/todo_routes.py) - Add limit and offset parameters with pagination metadata in response
- [ ] T045 [US6] Update filter store persistence (frontend/src/stores/filterStore.ts) - Persist filter preferences to localStorage

**Checkpoint**: User Story 6 complete - filters and sorting work independently with all combinations

---

## Phase 5: User Story 5 - Search Functionality (Priority: P1) 🎯 MVP

**Goal**: Implement full-text search across task titles, descriptions, and tags with fast results (<3 seconds for 10,000 tasks)

**Independent Test**: Can be fully tested by entering search queries and verifying accurate result matching

### Implementation for User Story 5

- [ ] T046 [P] [US5] Create search vector column migration (backend/app/database/migrations/add_search_vector.py) - Add search_vector tsvector column to tasks table
- [ ] T047 [P] [US5] Create GIN index for search (backend/app/database/migrations/add_search_vector.py) - Create idx_tasks_search_vector GIN index
- [ ] T048 [P] [US5] Create SearchService (backend/app/services/search_service.py) - search_tasks() method with full-text search using tsvector @@ query
- [ ] T049 [US5] Create search response schema (backend/app/api/schemas/search_schemas.py) - SearchResponse with results, total, query, filters fields
- [ ] T050 [US5] Create GET /search endpoint (backend/app/api/search_routes.py) - Search endpoint with q, priority, status, tag_id parameters
- [ ] T051 [US5] Add relevance ranking to search (backend/app/services/search_service.py) - Use ts_rank() for ordering results by relevance
- [ ] T052 [P] [US5] Create TaskSearch component (frontend/src/components/TaskSearch/TaskSearch.tsx) - Search input with debounced search
- [ ] T053 [US5] Create search API service (frontend/src/services/search.ts) - searchTasks() function calling GET /search
- [ ] T054 [US5] Update dashboard page (frontend/src/app/dashboard/page.tsx) - Integrate TaskSearch component
- [ ] T055 [US5] Add search results display (frontend/src/components/TaskList/TaskList.tsx) - Show relevance score and highlight matches
- [ ] T056 [US5] Add "no results" state (frontend/src/components/TaskSearch/TaskSearch.tsx) - Display appropriate message when no matches found
- [ ] T057 [US5] Add search analytics tracking (backend/app/services/search_service.py) - Log popular searches and zero-result queries to domain_events

**Checkpoint**: User Story 5 complete - search returns relevant results independently

---

## Phase 6: User Story 1 - Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create recurring tasks with patterns (daily, weekly, monthly, yearly, custom) and automatic instance generation

**Independent Test**: Can be fully tested by creating a recurring task with various patterns and verifying automatic instance generation

### Implementation for User Story 1

- [ ] T058 [P] [US1] Create RecurringTask model (backend/app/models/recurring_task.py) - SQLModel with recurrence_pattern, interval, by_weekday, by_monthday, by_month, end_condition, end_occurrences, end_date, series_id, next_due_date, is_active fields
- [ ] T059 [P] [US1] Extend Task model with recurring fields (backend/app/models/todo.py) - Add is_recurring and recurring_task_id foreign key
- [ ] T060 [P] [US1] Create recurring task indexes migration (backend/app/database/migrations/add_recurring_indexes.py) - idx_recurring_tasks_series_id, idx_recurring_tasks_next_due
- [ ] T061 [US1] Create RecurringService (backend/app/services/recurring_service.py) - RecurringService with calculate_next_occurrence() and generate_instances() methods
- [ ] T062 [US1] Implement recurrence pattern validation (backend/app/services/recurring_service.py) - Validate pattern configuration matches RFC 5545 patterns
- [ ] T063 [US1] Handle month-end edge cases (backend/app/services/recurring_service.py) - Logic for 31st → 28th/29th/30th adjustment
- [ ] T064 [US1] Add timezone-aware recurrence (backend/app/services/recurring_service.py) - Use pytz/zoneinfo for timezone handling in date calculations
- [ ] T065 [US1] Create POST /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Configure recurring pattern for a task
- [ ] T066 [US1] Create GET /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Get recurring configuration
- [ ] T067 [US1] Create PUT /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Update recurring configuration
- [ ] T068 [US1] Create DELETE /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Remove recurring configuration with delete_all_instances option
- [ ] T069 [US1] Create GET /recurring-tasks endpoint (backend/app/api/recurring_routes.py) - List all recurring tasks with is_active filter
- [ ] T070 [US1] Create RecurringWorker (backend/app/workers/recurring_worker.py) - Celery task to generate recurring instances based on next_due_date
- [ ] T071 [US1] Schedule recurring worker (backend/app/workers/celery_app.py) - Celery beat schedule to run every hour
- [ ] T072 [US1] Publish recurring.instance_generated event (backend/app/services/event_service.py) - Emit event when new instance created
- [ ] T073 [P] [US1] Create RecurringConfig component (frontend/src/components/RecurringConfig/RecurringConfig.tsx) - UI for configuring recurrence pattern (daily/weekly/monthly/yearly, interval, weekdays, end condition)
- [ ] T074 [US1] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add "Make recurring" toggle and RecurringConfig integration
- [ ] T075 [US1] Create recurring API service (frontend/src/services/recurring.ts) - configureRecurring(), getRecurringConfig(), updateRecurring(), deleteRecurring() functions
- [ ] T076 [US1] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display recurring indicator icon for recurring tasks
- [ ] T077 [US1] Add recurring info to task response (backend/app/api/schemas/todo_schemas.py) - Include recurring_info object with is_recurring, recurrence_pattern, next_due_date

**Checkpoint**: User Story 1 complete - recurring tasks can be created and instances auto-generated independently

---

## Phase 7: User Story 2 - Due Dates & Reminders (Priority: P1) 🎯 MVP

**Goal**: Enable users to set due dates and configure reminders delivered via email or in-app notifications

**Independent Test**: Can be fully tested by setting due dates and reminders, then verifying notification delivery at scheduled times

### Implementation for User Story 2

- [ ] T078 [P] [US2] Extend Task model with due_date and timezone (backend/app/models/todo.py) - Add due_date: datetime and timezone: str fields
- [ ] T079 [P] [US2] Create due_date index migration (backend/app/database/migrations/add_due_date_index.py) - Create idx_tasks_due_date index
- [ ] T080 [P] [US2] Create Reminder model (backend/app/models/reminder.py) - SQLModel with task_id, timing_minutes, timing_days, delivery_channel, scheduled_time, sent_at, status, error_message fields
- [ ] T081 [P] [US2] Create reminder indexes migration (backend/app/database/migrations/add_reminder_indexes.py) - idx_reminders_task_id, idx_reminders_scheduled_time, idx_reminders_pending partial index
- [ ] T082 [US2] Create ReminderService (backend/app/services/reminder_service.py) - ReminderService with schedule_reminder() and send_reminder() methods
- [ ] T083 [US2] Calculate scheduled_time from due_date (backend/app/services/reminder_service.py) - Logic: scheduled_time = due_date - timing_minutes
- [ ] T084 [US2] Implement in-app notification delivery (backend/app/services/reminder_service.py) - _send_in_app_notification() method creating notification record
- [ ] T085 [US2] Implement email notification delivery (backend/app/services/reminder_service.py) - _send_email_notification() method using SendGrid/AWS SES
- [ ] T086 [US2] Add retry logic for failed deliveries (backend/app/services/reminder_service.py) - Exponential backoff with max 3 retries
- [ ] T087 [US2] Create ReminderWorker (backend/app/workers/reminder_worker.py) - Celery task to process pending reminders due now
- [ ] T088 [US2] Schedule reminder worker (backend/app/workers/celery_app.py) - Celery beat schedule to run every minute
- [ ] T089 [US2] Create POST /reminders endpoint (backend/app/api/reminder_routes.py) - Create reminder for a task
- [ ] T090 [US2] Create GET /reminders endpoint (backend/app/api/reminder_routes.py) - List user's reminders
- [ ] T091 [US2] Create DELETE /reminders/{id} endpoint (backend/app/api/reminder_routes.py) - Delete/cancel reminder
- [ ] T092 [US2] Cancel reminders on task completion (backend/app/services/task_service.py) - Logic to set status='cancelled' when task completed
- [ ] T093 [US2] Publish task.reminder_sent event (backend/app/services/event_service.py) - Emit event when reminder delivered
- [ ] T094 [US2] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept reminders array in task creation
- [ ] T095 [US2] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating reminders (create/update/delete)
- [ ] T096 [P] [US2] Create ReminderConfig component (frontend/src/components/ReminderConfig/ReminderConfig.tsx) - UI for setting reminder timing (15 min, 1 hour, 1 day before) and delivery channel
- [ ] T097 [US2] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add due date picker and ReminderConfig integration
- [ ] T098 [US2] Create reminders API service (frontend/src/services/reminders.ts) - createReminder(), listReminders(), deleteReminder() functions
- [ ] T099 [US2] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display due date and overdue indicator (red styling for overdue)
- [ ] T100 [US2] Add reminders list to dashboard (frontend/src/app/dashboard/page.tsx) - Show upcoming reminders panel
- [ ] T101 [US2] Update task response schema (backend/app/api/schemas/todo_schemas.py) - Include reminders array in task details

**Checkpoint**: User Story 2 complete - due dates and reminders work independently with delivery confirmation

---

## Phase 8: User Story 4 - Tags & Categories (Priority: P2)

**Goal**: Enable users to create, assign, and manage tags for flexible task organization with filtering support

**Independent Test**: Can be fully tested by creating tags, assigning them to tasks, and filtering by tag

### Implementation for User Story 4

- [ ] T102 [P] [US4] Create Tag model (backend/app/models/tag.py) - SQLModel with user_id, name, color, created_at fields
- [ ] T103 [P] [US4] Create TaskTag join model (backend/app/models/task_tag.py) - SQLModel for many-to-many relationship with composite primary key
- [ ] T104 [P] [US4] Create tags migration (backend/app/database/migrations/add_tags_tables.py) - Create tags and task_tags tables with unique constraint on user_id+name
- [ ] T105 [P] [US4] Create tag indexes migration (backend/app/database/migrations/add_tags_indexes.py) - idx_tags_user_id, idx_task_tags_task_id, idx_task_tags_tag_id
- [ ] T106 [US4] Create TagService (backend/app/services/tag_service.py) - TagService with create_tag(), assign_tag_to_task(), unassign_tag(), delete_tag(), get_tasks_by_tag() methods
- [ ] T107 [US4] Add tag name uniqueness validation (backend/app/services/tag_service.py) - Check duplicate per user (case-insensitive)
- [ ] T108 [US4] Create GET /tags endpoint (backend/app/api/tag_routes.py) - List user's tags with usage_count
- [ ] T109 [US4] Create POST /tags endpoint (backend/app/api/tag_routes.py) - Create new tag with name and color
- [ ] T110 [US4] Create PUT /tags/{id} endpoint (backend/app/api/tag_routes.py) - Update tag name or color
- [ ] T111 [US4] Create DELETE /tags/{id} endpoint (backend/app/api/tag_routes.py) - Delete tag (cascade removes from tasks)
- [ ] T112 [US4] Create POST /tags/{id}/assign endpoint (backend/app/api/tag_routes.py) - Assign tag to task
- [ ] T113 [US4] Create DELETE /tags/{id}/unassign endpoint (backend/app/api/tag_routes.py) - Remove tag from task
- [ ] T114 [US4] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept tags array of tag IDs
- [ ] T115 [US4] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating tags (replace existing)
- [ ] T116 [US4] Add tag filtering to GET /todos (backend/app/api/todo_routes.py) - Support tag_id query parameter
- [ ] T117 [US4] Update TaskService (backend/app/services/task_service.py) - Add get_tags_for_task() and assign_tags() helper methods
- [ ] T118 [P] [US4] Create TagManager component (frontend/src/components/TagManager/TagManager.tsx) - UI for creating tags and managing tag assignments
- [ ] T119 [US4] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add tag selection with autocomplete
- [ ] T120 [US4] Create tags API service (frontend/src/services/tags.ts) - listTags(), createTag(), assignTag(), unassignTag(), deleteTag() functions
- [ ] T121 [US4] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display tags as colored badges
- [ ] T122 [US4] Update TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by tag dropdown
- [ ] T123 [US4] Add tag colors to task store (frontend/src/stores/taskStore.ts) - Store tag color information for display

**Checkpoint**: User Story 4 complete - tags can be created, assigned, and filtered independently

---

## Phase 9: User Story 7 - Event-Driven Architecture (Priority: P2)

**Goal**: Publish events for all task operations enabling real-time updates, activity feeds, and future integrations

**Independent Test**: Can be fully tested by performing actions and verifying events are published and consumed correctly

### Implementation for User Story 7

- [ ] T124 [P] [US7] Create Kafka topic configuration (backend/app/events/publisher.py) - Define topics: todo.tasks.created, todo.tasks.updated, todo.tasks.completed, todo.tasks.deleted
- [ ] T125 [US7] Update TaskService create (backend/app/services/task_service.py) - Publish task.created event after task creation
- [ ] T126 [US7] Update TaskService update (backend/app/services/task_service.py) - Publish task.updated event after task modification
- [ ] T127 [US7] Update TaskService complete (backend/app/services/task_service.py) - Publish task.completed event after task completion
- [ ] T128 [US7] Update TaskService delete (backend/app/services/task_service.py) - Publish task.deleted event after task deletion
- [ ] T129 [US7] Create event retention logic (backend/app/events/publisher.py) - Retry failed publishes with exponential backoff
- [ ] T130 [US7] Create event consumer service (backend/app/events/consumer.py) - Subscribe to Kafka topics and process events
- [ ] T131 [US7] Implement idempotent event processing (backend/app/events/consumer.py) - Use event_id to prevent duplicate processing
- [ ] T132 [US7] Create dead letter queue handler (backend/app/events/consumer.py) - Store failed events for manual review
- [ ] T133 [US7] Add WebSocket integration (backend/app/api/websocket_manager.py) - Broadcast events to connected clients in real-time
- [ ] T134 [US7] Update domain_events table (backend/app/models/event.py) - Track published and processed status
- [ ] T135 [US7] Create event monitoring endpoint (backend/app/api/event_routes.py) - GET /events for monitoring event flow
- [ ] T136 [US7] Add event metrics logging (backend/app/services/event_service.py) - Log latency, success rate, queue size

**Checkpoint**: User Story 7 complete - events are published and consumed reliably

---

## Phase 10: User Story 8 - Distributed Application Runtime (Priority: P2)

**Goal**: Use Dapr for state management, pub/sub messaging, and service-to-service communication

**Independent Test**: Can be fully tested by verifying Dapr sidecar communication and state management functionality

### Implementation for User Story 8

- [ ] T137 [P] [US8] Create Dapr pub/sub service (backend/app/dapr/pubsub.py) - DaprPubSub class with publish() and subscribe() methods
- [ ] T138 [US8] Update event publisher (backend/app/events/publisher.py) - Use Dapr pub/sub for publishing events to Kafka
- [ ] T139 [US8] Create Dapr service discovery config (backend/app/dapr/config.py) - Configure service-to-service communication
- [ ] T140 [US8] Update reminder worker (backend/app/workers/reminder_worker.py) - Use Dapr state for worker coordination
- [ ] T141 [US8] Update recurring worker (backend/app/workers/recurring_worker.py) - Use Dapr state for worker coordination
- [ ] T142 [US8] Add Dapr health check endpoint (backend/app/api/health_routes.py) - /health/dapr endpoint checking sidecar connectivity
- [ ] T143 [US8] Create Dapr integration tests (backend/tests/integration/test_dapr_integration.py) - Test state save/get/delete via Dapr
- [ ] T144 [US8] Update docker-compose.yml (docker-compose.yml) - Add Dapr sidecar service configuration
- [ ] T145 [US8] Create Dapr configuration file (dapr/config.yaml) - Dapr configuration for tracing, metrics, logging

**Checkpoint**: User Story 8 complete - Dapr runtime manages state and pub/sub

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T146 [P] Update API documentation (specs/003-advanced-todo-features/contracts/api-contracts.md) - Ensure all endpoints are documented with examples
- [ ] T147 [P] Update quickstart guide (specs/003-advanced-todo-features/quickstart.md) - Add troubleshooting section and verification steps
- [ ] T148 Code cleanup - Remove unused imports, fix linting issues across all files
- [ ] T149 [P] Add comprehensive logging - Add structured logging for all service operations with correlation IDs
- [ ] T150 [P] Security hardening - Add rate limiting to search endpoint (30 req/min), validate all user inputs
- [ ] T151 [P] Performance optimization - Add database connection pooling, optimize slow queries with EXPLAIN ANALYZE
- [ ] T152 [P] Update environment variables documentation (backend/.env.example, frontend/.env.example) - Document all new configuration options
- [ ] T153 Run quickstart.md validation - Execute all verification tests from quickstart guide
- [ ] T154 [P] Create database rollback scripts (backend/app/database/migrations/downgrade_003.py) - Migration downgrade scripts for all changes
- [ ] T155 [P] Add monitoring dashboard queries (docs/monitoring_queries.sql) - SQL queries for monitoring task counts, event latency, reminder delivery

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

| User Story | Priority | Dependencies | Independent Test |
|------------|----------|--------------|------------------|
| **US3 - Priorities** | P1 | Foundational (Phase 2) | ✅ Assign priority, filter/sort by priority |
| **US6 - Filter & Sort** | P1 | Foundational + US3 (optional) | ✅ Apply filters, verify ordering |
| **US5 - Search** | P1 | Foundational | ✅ Search returns relevant results |
| **US1 - Recurring Tasks** | P1 | Foundational | ✅ Create recurring, instances auto-generated |
| **US2 - Due Dates & Reminders** | P1 | Foundational | ✅ Set due date, reminder delivered |
| **US4 - Tags** | P2 | Foundational | ✅ Create tag, assign, filter by tag |
| **US7 - Event-Driven** | P2 | Foundational | ✅ Events published and consumed |
| **US8 - Dapr Runtime** | P2 | Foundational | ✅ Dapr state/pubsub working |

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T005, T006 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T007, T008, T009, T010 can run in parallel (different migration files)
- T011, T012, T014, T015, T018, T019 can run in parallel (different infrastructure files)

**User Stories**:
- Once Foundational phase completes, all user stories (US1-US8) can start in parallel
- Each user story is independently implementable and testable

**Within User Story 3 (Priorities)**:
- T022, T023 can run in parallel (model changes)
- T030, T031, T032, T033, T034 can run in parallel (frontend components)

**Within User Story 5 (Search)**:
- T046, T047, T048 can run in parallel (backend search setup)
- T052, T053, T054 can run in parallel (frontend search components)

---

## Parallel Example: User Story 3 (Priorities)

```bash
# Launch all backend model changes together:
Task: "T022 [P] [US3] Extend Task model with priority field"
Task: "T023 [P] [US3] Add priority index to Task model"

# Launch all frontend components together:
Task: "T030 [P] [US3] Create PrioritySelector component"
Task: "T031 [US3] Update TaskForm component"
Task: "T032 [US3] Update TaskItem component"
Task: "T033 [US3] Update TaskList component"
Task: "T034 [P] [US3] Create TaskFilters component"
```

---

## Parallel Example: User Story 5 (Search)

```bash
# Launch backend search setup together:
Task: "T046 [P] [US5] Create search vector column migration"
Task: "T047 [P] [US5] Create GIN index for search"
Task: "T048 [P] [US5] Create SearchService"

# Launch frontend search components together:
Task: "T052 [P] [US5] Create TaskSearch component"
Task: "T053 [US5] Create search API service"
Task: "T054 [US5] Update dashboard page"
```

---

## Implementation Strategy

### MVP First (User Story 3 - Priorities Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 3 (Priorities)
4. **STOP and VALIDATE**: Test priority assignment, filtering, sorting
5. Deploy/demo if ready - MVP delivers immediate value

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US3 (Priorities) → Test independently → Deploy/Demo (MVP!)
3. Add US6 (Filter & Sort) → Test independently → Deploy/Demo
4. Add US5 (Search) → Test independently → Deploy/Demo
5. Add US1 (Recurring) → Test independently → Deploy/Demo
6. Add US2 (Reminders) → Test independently → Deploy/Demo
7. Add US4 (Tags) → Test independently → Deploy/Demo
8. Add US7 (Events) + US8 (Dapr) → Test independently → Deploy/Demo
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase:

- Developer A: User Story 3 (Priorities) + User Story 6 (Filter & Sort)
- Developer B: User Story 5 (Search) + User Story 1 (Recurring)
- Developer C: User Story 2 (Reminders) + User Story 4 (Tags)
- Developer D: User Story 7 (Events) + User Story 8 (Dapr)

All stories complete and integrate independently.

---

## Task Summary

| Phase | User Story | Task Count | Priority |
|-------|-----------|------------|----------|
| Phase 1 | Setup | 6 | - |
| Phase 2 | Foundational | 15 | - |
| Phase 3 | US3 - Priorities | 15 | P1 |
| Phase 4 | US6 - Filter & Sort | 9 | P1 |
| Phase 5 | US5 - Search | 12 | P1 |
| Phase 6 | US1 - Recurring Tasks | 20 | P1 |
| Phase 7 | US2 - Due Dates & Reminders | 24 | P1 |
| Phase 8 | US4 - Tags & Categories | 22 | P2 |
| Phase 9 | US7 - Event-Driven | 13 | P2 |
| Phase 10 | US8 - Dapr Runtime | 9 | P2 |
| Phase 11 | Polish | 10 | - |
| **Total** | | **155 tasks** | |

### Task Count per User Story

- **US1 (Recurring Tasks)**: 20 tasks (T058-T077)
- **US2 (Due Dates & Reminders)**: 24 tasks (T078-T101)
- **US3 (Priorities)**: 15 tasks (T022-T036)
- **US4 (Tags)**: 22 tasks (T102-T123)
- **US5 (Search)**: 12 tasks (T046-T057)
- **US6 (Filter & Sort)**: 9 tasks (T037-T045)
- **US7 (Event-Driven)**: 13 tasks (T124-T136)
- **US8 (Dapr Runtime)**: 9 tasks (T137-T145)

### Suggested MVP Scope

**Minimum Viable Product**: User Story 3 (Priorities) only
- Tasks: T001-T021 (Setup + Foundational) + T022-T036 (US3)
- Total: 36 tasks
- Delivers: Basic task management with priority levels, filtering, and sorting

**MVP+1**: Add User Story 6 (Filter & Sort)
- Additional: T037-T045 (9 tasks)
- Total: 45 tasks
- Delivers: Enhanced task organization with combined filters

**MVP+2**: Add User Story 5 (Search)
- Additional: T046-T057 (12 tasks)
- Total: 57 tasks
- Delivers: Full-text search for quick task discovery

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Format Validation

✅ **ALL 155 tasks follow the required checklist format**:
- Checkbox: `- [ ]`
- Task ID: Sequential (T001-T155)
- [P] marker: Included for parallelizable tasks
- [Story] label: Included for user story phase tasks (US1-US8)
- Description: Clear action with exact file path
