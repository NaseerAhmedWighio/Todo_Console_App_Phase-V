# Tasks: Advanced Todo Features Implementation

**Input**: Design documents from `/specs/004-advanced-todo-impl/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.yaml

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

- [X] T001 Create project structure per implementation plan (backend/app/models/, backend/app/services/, backend/app/api/, backend/app/events/, backend/app/dapr/, backend/app/workers/)
- [X] T002 [P] Add backend dependencies to backend/requirements.txt (kafka-python>=2.0.2, dapr-sdk>=1.10.0, dapr-ext-fastapi>=1.10.0, celery>=5.3.0, redis>=4.5.0, python-dateutil>=2.8.2, pytz>=2023.3)
- [X] T003 [P] Add frontend dependencies to frontend/package.json (date-fns@^2.30.0, react-tag-autocomplete@^7.0.0, @dnd-kit/core@^6.0.0)
- [X] T004 [P] Create dapr/components/ directory structure for Dapr configuration files
- [X] T005 [P] Create backend/app/events/ directory for Kafka event publisher/consumer
- [X] T006 [P] Create backend/app/workers/ directory for Celery background workers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create database migration script for new tables (backend/app/database/migrations/001_add_advanced_features.py) - tags, task_tags, reminders, recurring_tasks, domain_events, dapr_state tables
- [X] T008 [P] Create database migration for task table extensions (backend/app/database/migrations/002_extend_task_model.py) - priority, due_date, timezone, is_recurring, recurring_task_id columns
- [X] T009 [P] Create database migration for user table extensions (backend/app/database/migrations/003_extend_user_model.py) - timezone, notification_preferences, default_task_priority columns
- [X] T010 [P] Create GIN index migration for full-text search (backend/app/database/migrations/005_add_search_indexes.py) - idx_tasks_search_vector, idx_tasks_priority, idx_tasks_due_date
- [X] T011 [P] Implement Dapr state store component (dapr/components/statestore.yaml) - PostgreSQL state store configuration for NeonDB
- [X] T012 [P] Implement Dapr pub/sub component (dapr/components/pubsub.yaml) - Kafka pub/sub configuration
- [X] T013 Create Dapr state manager service (backend/app/dapr/state.py) - DaprStateManager class with save_state, get_state, delete_state methods
- [X] T014 [P] Create Kafka event publisher (backend/app/events/publisher.py) - EventPublisher class with publish() method using kafka-python
- [X] T015 [P] Create Kafka event consumer (backend/app/events/consumer.py) - EventConsumer class with subscribe() and process() methods
- [X] T016 Create event schemas module (backend/app/events/schemas.py) - Pydantic models for task.created, task.updated, task.completed, task.deleted events
- [X] T017 Create Celery app configuration (backend/app/workers/celery_app.py) - Celery configuration with Redis broker
- [X] T018 [P] Update docker-compose.yml to add Kafka service (confluentinc/cp-kafka:7.4.0) with Zookeeper
- [X] T019 [P] Update docker-compose.yml to add Redis service for Celery broker
- [X] T020 Create domain event model (backend/app/models/event.py) - DomainEvent SQLModel with event_type, aggregate_id, payload, published, processed fields
- [X] T021 Create event service (backend/app/services/event_service.py) - EventService for publishing and tracking domain events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Complete Task Management with Priorities (Priority: P1) 🎯 MVP

**Goal**: Implement priority levels for tasks (low, medium, high, urgent) with visual indicators and filtering/sorting support

**Independent Test**: Can be fully tested by assigning different priority levels and verifying sorting/filtering behavior

### Implementation for User Story 1

- [X] T022 [P] [US1] Extend Task model with priority field (backend/app/models/todo.py) - Add priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
- [X] T023 [P] [US1] Add priority index to Task model (backend/app/models/todo.py) - Add Index definition for idx_tasks_priority
- [X] T024 [US1] Update TaskCreate and TaskUpdate schemas (backend/app/api/schemas/todo_schemas.py) - Add priority field with validation
- [X] T025 [US1] Extend TaskService with priority filtering (backend/app/services/task_service.py) - Add filter_by_priority() and sort_by_priority() methods
- [X] T026 [US1] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add priority query parameter for filtering
- [X] T027 [US1] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add sort_by and sort_order query parameters supporting priority sorting
- [X] T028 [US1] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept priority field in request body
- [X] T029 [US1] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating priority field
- [X] T030 [P] [US1] Create PrioritySelector component (frontend/src/components/PrioritySelector/PrioritySelector.tsx) - Dropdown with color-coded priority options (red=urgent, orange=high, yellow=medium, gray=low)
- [X] T031 [US1] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add priority selector field
- [X] T032 [US1] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display priority with color indicator
- [X] T033 [US1] Update TaskList component (frontend/src/components/TaskList/TaskList.tsx) - Add sort by priority option
- [X] T034 [US1] Create TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by priority dropdown
- [X] T035 [US1] Update task API service (frontend/src/services/tasks.ts) - Add priority parameter to API calls
- [X] T036 [US1] Update task store (frontend/src/stores/taskStore.ts) - Add priority to task state and filters

**Checkpoint**: User Story 1 complete - priorities can be assigned, filtered, and sorted independently

---

## Phase 4: User Story 2 - Task Organization with Tags (Priority: P1)

**Goal**: Enable users to create, assign, and manage tags for flexible task organization with filtering support

**Independent Test**: Can be fully tested by creating tags, assigning them to tasks, and filtering by tag

### Implementation for User Story 2

- [X] T037 [P] [US2] Create Tag model (backend/app/models/tag.py) - SQLModel with user_id, name, color, created_at fields
- [X] T038 [P] [US2] Create TaskTag join model (backend/app/models/task_tag.py) - SQLModel for many-to-many relationship with composite primary key
- [X] T039 [US2] Create TagService (backend/app/services/tag_service.py) - TagService with create_tag(), assign_tag_to_task(), unassign_tag(), delete_tag(), get_tasks_by_tag() methods
- [X] T040 [US2] Add tag name uniqueness validation (backend/app/services/tag_service.py) - Check duplicate per user (case-insensitive)
- [X] T041 [US2] Create GET /tags endpoint (backend/app/api/tag_routes.py) - List user's tags with usage_count
- [X] T042 [US2] Create POST /tags endpoint (backend/app/api/tag_routes.py) - Create new tag with name and color
- [X] T043 [US2] Create PUT /tags/{id} endpoint (backend/app/api/tag_routes.py) - Update tag name or color
- [X] T044 [US2] Create DELETE /tags/{id} endpoint (backend/app/api/tag_routes.py) - Delete tag (cascade removes from tasks)
- [X] T045 [US2] Create POST /tags/{id}/assign endpoint (backend/app/api/tag_routes.py) - Assign tag to task
- [X] T046 [US2] Create DELETE /tags/{id}/unassign endpoint (backend/app/api/tag_routes.py) - Remove tag from task
- [ ] T047 [US2] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept tags array of tag IDs
- [ ] T048 [US2] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating tags (replace existing)
- [ ] T049 [US2] Add tag filtering to GET /todos (backend/app/api/todo_routes.py) - Support tag_id query parameter
- [ ] T050 [US2] Update TaskService (backend/app/services/task_service.py) - Add get_tags_for_task() and assign_tags() helper methods
- [X] T051 [P] [US2] Create TagManager component (frontend/src/components/TagManager/TagManager.tsx) - UI for creating tags and managing tag assignments
- [ ] T052 [US2] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add tag selection with autocomplete
- [ ] T053 [US2] Create tags API service (frontend/src/services/tags.ts) - listTags(), createTag(), assignTag(), unassignTag(), deleteTag() functions
- [ ] T054 [US2] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display tags as colored badges
- [ ] T055 [US2] Update TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by tag dropdown
- [ ] T056 [US2] Add tag colors to task store (frontend/src/stores/taskStore.ts) - Store tag color information for display

**Checkpoint**: User Story 2 complete - tags can be created, assigned, and filtered independently

---

## Phase 5: User Story 3 - Due Dates and Time Management (Priority: P1)

**Goal**: Enable users to set due dates for tasks with timezone awareness, overdue detection, and date-based sorting/filtering

**Independent Test**: Can be fully tested by setting due dates, verifying database storage, and confirming overdue visual indicators and date-based sorting work correctly

### Implementation for User Story 3

- [ ] T057 [P] [US3] Extend Task model with due_date and timezone fields (backend/app/models/todo.py) - Add due_date: datetime and timezone: str fields
- [ ] T058 [P] [US3] Create due_date index migration (backend/app/database/migrations/add_due_date_index.py) - Create idx_tasks_due_date index
- [ ] T059 [US3] Update TaskCreate and TaskUpdate schemas (backend/app/api/schemas/todo_schemas.py) - Add due_date and timezone fields with validation
- [ ] T060 [US3] Extend TaskService with due date filtering (backend/app/services/task_service.py) - Add filter_by_due_date_range() and sort_by_due_date() methods
- [ ] T061 [US3] Implement overdue detection logic (backend/app/services/task_service.py) - is_overdue() function comparing UTC timestamps
- [ ] T062 [US3] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add due_date_from and due_date_to query parameters
- [ ] T063 [US3] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept due_date and timezone fields
- [ ] T064 [US3] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating due_date and timezone
- [ ] T065 [P] [US3] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add due date picker with timezone selection
- [ ] T066 [US3] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display due date and overdue indicator (red styling for overdue)
- [ ] T067 [US3] Update TaskList component (frontend/src/components/TaskList/TaskList.tsx) - Add sort by due date option
- [ ] T068 [US3] Update TaskFilters component (frontend/src/components/TaskFilters/TaskFilters.tsx) - Add filter by due date range
- [ ] T069 [US3] Update task API service (frontend/src/services/tasks.ts) - Add due_date and timezone parameters to API calls
- [ ] T070 [US3] Add timezone conversion utility (frontend/src/utils/timezone.ts) - Convert UTC to user's local time for display

**Checkpoint**: User Story 3 complete - due dates and overdue detection work independently

---

## Phase 6: User Story 4 - Powerful Search and Filtering (Priority: P1)

**Goal**: Implement full-text search across task titles, descriptions, and tags with fast results and combined filter support

**Independent Test**: Can be fully tested by entering search queries and applying various filter combinations, verifying accurate database query results

### Implementation for User Story 4

- [X] T071 [P] [US4] Create search vector column migration (backend/app/database/migrations/005_add_search_indexes.py) - Add search_vector tsvector column to tasks table
- [X] T072 [P] [US4] Create GIN index for search (backend/app/database/migrations/005_add_search_indexes.py) - Create idx_tasks_search_vector GIN index
- [X] T073 [P] [US4] Create search trigger function migration (backend/app/database/migrations/005_add_search_indexes.py) - Auto-update search_vector on task changes
- [X] T074 [P] [US4] Create SearchService (backend/app/services/search_service.py) - search_tasks() method with full-text search using tsvector @@ query
- [ ] T075 [US4] Add relevance ranking to search (backend/app/services/search_service.py) - Use ts_rank() for ordering results by relevance
- [ ] T076 [US4] Create search response schema (backend/app/api/schemas/search_schemas.py) - SearchResponse with results, total, query, filters fields
- [X] T077 [US4] Create GET /search endpoint (backend/app/api/search_routes.py) - Search endpoint with q, priority, status, tag_id parameters
- [ ] T078 [US4] Extend TaskService filter method (backend/app/services/task_service.py) - Add support for combined filters (status, priority, tag_id, date range)
- [ ] T079 [US4] Update GET /todos endpoint (backend/app/api/todo_routes.py) - Add support for combining multiple filter parameters
- [ ] T080 [US4] Add pagination support to GET /todos (backend/app/api/todo_routes.py) - Add limit and offset parameters with pagination metadata in response
- [X] T081 [P] [US4] Create TaskSearch component (frontend/src/components/TaskSearch/TaskSearch.tsx) - Search input with debounced search
- [ ] T083 [US4] Update TaskSort component (frontend/src/components/TaskSort/TaskSort.tsx) - Sort controls with options: due_date, priority, created_at, title
- [ ] T084 [US4] Update TaskList component (frontend/src/components/TaskList/TaskList.tsx) - Integrate TaskFilters and TaskSort components
- [ ] T085 [US4] Create filter store (frontend/src/stores/filterStore.ts) - Zustand store for filter and sort state management
- [X] T086 [US4] Create search API service (frontend/src/services/search.ts) - searchTasks() function calling GET /search
- [ ] T087 [US4] Update task API service (frontend/src/services/tasks.ts) - Pass filter and sort parameters to backend
- [ ] T088 [US4] Add filter store persistence (frontend/src/stores/filterStore.ts) - Persist filter preferences to localStorage

**Checkpoint**: User Story 4 complete - search and filtering work independently with all combinations

---

## Phase 7: User Story 5 - Recurring Tasks Automation (Priority: P2)

**Goal**: Enable users to create recurring tasks with patterns (daily, weekly, monthly, yearly, custom) and automatic instance generation

**Independent Test**: Can be fully tested by creating a recurring task with various patterns and verifying automatic instance generation is scheduled and stored in the database

### Implementation for User Story 5

- [ ] T089 [P] [US5] Create RecurringTask model (backend/app/models/recurring_task.py) - SQLModel with recurrence_pattern, interval, by_weekday, by_monthday, by_month, end_condition, end_occurrences, end_date, series_id, next_due_date, is_active fields
- [ ] T090 [P] [US5] Extend Task model with recurring fields (backend/app/models/todo.py) - Add is_recurring and recurring_task_id foreign key
- [ ] T091 [P] [US5] Create recurring task indexes migration (backend/app/database/migrations/add_recurring_indexes.py) - idx_recurring_tasks_series_id, idx_recurring_tasks_next_due
- [ ] T092 [US5] Create RecurringService (backend/app/services/recurring_service.py) - RecurringService with calculate_next_occurrence() and generate_instances() methods
- [ ] T093 [US5] Implement recurrence pattern validation (backend/app/services/recurring_service.py) - Validate pattern configuration using python-dateutil.rrule
- [ ] T094 [US5] Handle month-end edge cases (backend/app/services/recurring_service.py) - Logic for 31st → 28th/29th/30th adjustment using dateutil
- [ ] T095 [US5] Add timezone-aware recurrence (backend/app/services/recurring_service.py) - Use pytz for timezone handling in date calculations
- [ ] T096 [US5] Create POST /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Configure recurring pattern for a task
- [ ] T097 [US5] Create GET /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Get recurring configuration
- [ ] T098 [US5] Create PUT /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Update recurring configuration
- [ ] T099 [US5] Create DELETE /todos/{id}/recurring endpoint (backend/app/api/recurring_routes.py) - Remove recurring configuration with delete_all_instances option
- [ ] T100 [US5] Create GET /recurring-tasks endpoint (backend/app/api/recurring_routes.py) - List all recurring tasks with is_active filter
- [ ] T101 [US5] Create RecurringWorker (backend/app/workers/recurring_worker.py) - Celery task to generate recurring instances based on next_due_date
- [ ] T102 [US5] Schedule recurring worker (backend/app/workers/celery_app.py) - Celery beat schedule to run every hour
- [ ] T103 [US5] Publish recurring.instance_generated event (backend/app/services/event_service.py) - Emit event when new instance created
- [ ] T104 [P] [US5] Create RecurringConfig component (frontend/src/components/RecurringConfig/RecurringConfig.tsx) - UI for configuring recurrence pattern (daily/weekly/monthly/yearly, interval, weekdays, end condition)
- [ ] T105 [US5] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add "Make recurring" toggle and RecurringConfig integration
- [ ] T106 [US5] Create recurring API service (frontend/src/services/recurring.ts) - configureRecurring(), getRecurringConfig(), updateRecurring(), deleteRecurring() functions
- [ ] T107 [US5] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display recurring indicator icon for recurring tasks
- [ ] T108 [US5] Add recurring info to task response (backend/app/api/schemas/todo_schemas.py) - Include recurring_info object with is_recurring, recurrence_pattern, next_due_date

**Checkpoint**: User Story 5 complete - recurring tasks can be created and instances auto-generated independently

---

## Phase 8: User Story 6 - Reminders and Notifications (Priority: P2)

**Goal**: Enable users to configure reminders for tasks with scheduling and delivery processing

**Independent Test**: Can be fully tested by setting reminders, verifying they are scheduled in the database, and confirming reminder processing logic works correctly

### Implementation for User Story 6

- [ ] T109 [P] [US6] Create Reminder model (backend/app/models/reminder.py) - SQLModel with task_id, timing_minutes, timing_days, delivery_channel, scheduled_time, sent_at, status, error_message fields
- [ ] T110 [P] [US6] Create reminder indexes migration (backend/app/database/migrations/add_reminder_indexes.py) - idx_reminders_task_id, idx_reminders_scheduled_time, idx_reminders_pending partial index
- [ ] T111 [US6] Create ReminderService (backend/app/services/reminder_service.py) - ReminderService with schedule_reminder() and send_reminder() methods
- [ ] T112 [US6] Calculate scheduled_time from due_date (backend/app/services/reminder_service.py) - Logic: scheduled_time = due_date - timing_minutes
- [ ] T113 [US6] Implement in-app notification delivery (backend/app/services/reminder_service.py) - _send_in_app_notification() method creating notification record
- [ ] T114 [US6] Implement email notification delivery (backend/app/services/reminder_service.py) - _send_email_notification() method (placeholder for future email service)
- [ ] T115 [US6] Add retry logic for failed deliveries (backend/app/services/reminder_service.py) - Exponential backoff with max 3 retries
- [ ] T116 [US6] Create ReminderWorker (backend/app/workers/reminder_worker.py) - Celery task to process pending reminders due now
- [ ] T117 [US6] Schedule reminder worker (backend/app/workers/celery_app.py) - Celery beat schedule to run every minute
- [ ] T118 [US6] Create POST /reminders endpoint (backend/app/api/reminder_routes.py) - Create reminder for a task
- [ ] T119 [US6] Create GET /reminders endpoint (backend/app/api/reminder_routes.py) - List user's reminders
- [ ] T120 [US6] Create DELETE /reminders/{id} endpoint (backend/app/api/reminder_routes.py) - Delete/cancel reminder
- [ ] T121 [US6] Cancel reminders on task completion (backend/app/services/task_service.py) - Logic to set status='cancelled' when task completed
- [ ] T122 [US6] Publish task.reminder_sent event (backend/app/services/event_service.py) - Emit event when reminder delivered
- [ ] T123 [US6] Update POST /todos endpoint (backend/app/api/todo_routes.py) - Accept reminders array in task creation
- [ ] T124 [US6] Update PUT /todos/{id} endpoint (backend/app/api/todo_routes.py) - Support updating reminders (create/update/delete)
- [ ] T125 [P] [US6] Create ReminderConfig component (frontend/src/components/ReminderConfig/ReminderConfig.tsx) - UI for setting reminder timing (15 min, 1 hour, 1 day before) and delivery channel
- [ ] T126 [US6] Update TaskForm component (frontend/src/components/TaskForm/TaskForm.tsx) - Add due date picker and ReminderConfig integration
- [ ] T127 [US6] Create reminders API service (frontend/src/services/reminders.ts) - createReminder(), listReminders(), deleteReminder() functions
- [ ] T128 [US6] Update TaskItem component (frontend/src/components/TaskItem/TaskItem.tsx) - Display reminder indicator icon
- [ ] T129 [US6] Add reminders list to dashboard (frontend/src/app/dashboard/page.tsx) - Show upcoming reminders panel
- [ ] T130 [US6] Update task response schema (backend/app/api/schemas/todo_schemas.py) - Include reminders array in task details

**Checkpoint**: User Story 6 complete - reminders can be scheduled and processed independently

---

## Phase 9: User Story 7 - Event-Driven Architecture (Priority: P2)

**Goal**: Publish events for all task operations enabling real-time updates and future integrations

**Independent Test**: Can be fully tested by performing actions and verifying events are published to Kafka and consumed correctly

### Implementation for User Story 7

- [ ] T131 [P] [US7] Create Kafka topic configuration (backend/app/events/publisher.py) - Define topics: todo.tasks.created, todo.tasks.updated, todo.tasks.completed, todo.tasks.deleted, todo.reminder.sent, todo.recurring.generated
- [ ] T132 [US7] Update TaskService create (backend/app/services/task_service.py) - Publish task.created event after task creation
- [ ] T133 [US7] Update TaskService update (backend/app/services/task_service.py) - Publish task.updated event after task modification
- [ ] T134 [US7] Update TaskService complete (backend/app/services/task_service.py) - Publish task.completed event after task completion
- [ ] T135 [US7] Update TaskService delete (backend/app/services/task_service.py) - Publish task.deleted event after task deletion
- [ ] T136 [US7] Create event retention logic (backend/app/events/publisher.py) - Retry failed publishes with exponential backoff
- [ ] T137 [US7] Implement idempotent event processing (backend/app/events/consumer.py) - Use event_id to prevent duplicate processing
- [ ] T138 [US7] Create dead letter queue handler (backend/app/events/consumer.py) - Store failed events for manual review
- [ ] T139 [US7] Add WebSocket integration (backend/app/api/websocket_manager.py) - Broadcast events to connected clients in real-time
- [ ] T140 [US7] Update domain_events table (backend/app/models/event.py) - Track published and processed status
- [ ] T141 [US7] Create event monitoring endpoint (backend/app/api/event_routes.py) - GET /events for monitoring event flow
- [ ] T142 [US7] Add event metrics logging (backend/app/services/event_service.py) - Log latency, success rate, queue size

**Checkpoint**: User Story 7 complete - events are published and consumed reliably

---

## Phase 10: User Story 8 - Distributed Application Runtime (Priority: P2)

**Goal**: Use Dapr for state management, pub/sub messaging, and service-to-service communication

**Independent Test**: Can be fully tested by verifying Dapr sidecar communication and state management functionality

### Implementation for User Story 8

- [ ] T143 [P] [US8] Create Dapr pub/sub service (backend/app/dapr/pubsub.py) - DaprPubSub class with publish() and subscribe() methods
- [ ] T144 [US8] Update event publisher (backend/app/events/publisher.py) - Use Dapr pub/sub for publishing events to Kafka
- [ ] T145 [US8] Create Dapr service discovery config (backend/app/dapr/config.py) - Configure service-to-service communication
- [ ] T146 [US8] Update reminder worker (backend/app/workers/reminder_worker.py) - Use Dapr state for worker coordination
- [ ] T147 [US8] Update recurring worker (backend/app/workers/recurring_worker.py) - Use Dapr state for worker coordination
- [ ] T148 [US8] Add Dapr health check endpoint (backend/app/api/health_routes.py) - /health/dapr endpoint checking sidecar connectivity
- [ ] T149 [US8] Create Dapr integration tests (backend/tests/integration/test_dapr_integration.py) - Test state management and pub/sub
- [ ] T149 [US8] Update Dockerfile (backend/Dockerfile) - Add Dapr sidecar configuration for containerized deployment

**Checkpoint**: User Story 8 complete - Dapr runtime is integrated and functional

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T150 [P] Update API documentation (backend/README.md) - Document all new endpoints and request/response formats
- [ ] T151 [P] Update frontend documentation (frontend/README.md) - Document new components and services
- [ ] T152 Code cleanup and refactoring across all stories
- [ ] T153 Performance optimization for database queries (verify indexes are used)
- [ ] T154 Security hardening (validate all user inputs, check authorization)
- [ ] T155 Run quickstart.md validation checklist - Verify all features work end-to-end
- [ ] T156 [P] Update .env.example (backend/.env.example) - Add Kafka, Dapr, Redis configuration examples
- [ ] T157 [P] Update docker-compose.yml - Add all services (Kafka, Zookeeper, Redis, Dapr)

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

- **User Story 1 (P1) - Priorities**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Tags**: Can start after Foundational (Phase 2) - Independent
- **User Story 3 (P1) - Due Dates**: Can start after Foundational (Phase 2) - Independent
- **User Story 4 (P1) - Search/Filter**: Can start after Foundational (Phase 2) - May integrate with US1, US2, US3
- **User Story 5 (P2) - Recurring Tasks**: Can start after Foundational (Phase 2) - Independent
- **User Story 6 (P2) - Reminders**: Can start after Foundational (Phase 2) - Depends on US3 (due dates)
- **User Story 7 (P2) - Events**: Can start after Foundational (Phase 2) - Cross-cutting concern
- **User Story 8 (P2) - Dapr**: Can start after Foundational (Phase 2) - Cross-cutting concern

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T002, T003, T004, T005, T006 can all run in parallel
- **Foundational Phase**: T008, T009, T010, T011, T012, T014, T018, T019 can run in parallel
- **User Stories**: Once Foundational completes, all P1 stories (US1, US2, US3, US4) can start in parallel
- **Within Stories**: Model creation tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Priorities)

```bash
# Launch all models for User Story 1 together:
Task: "T022 [P] [US1] Extend Task model with priority field in backend/app/models/todo.py"
Task: "T023 [P] [US1] Add priority index to Task model in backend/app/models/todo.py"

# Launch all frontend components in parallel:
Task: "T030 [P] [US1] Create PrioritySelector component in frontend/src/components/PrioritySelector/PrioritySelector.tsx"
```

---

## Parallel Example: User Story 2 (Tags)

```bash
# Launch all models for User Story 2 together:
Task: "T037 [P] [US2] Create Tag model in backend/app/models/tag.py"
Task: "T038 [P] [US2] Create TaskTag join model in backend/app/models/task_tag.py"

# Launch frontend components in parallel:
Task: "T051 [P] [US2] Create TagManager component in frontend/src/components/TagManager/TagManager.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Priorities)
4. **STOP and VALIDATE**: Test priorities independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Priorities) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Tags) → Test independently → Deploy/Demo
4. Add User Story 3 (Due Dates) → Test independently → Deploy/Demo
5. Add User Story 4 (Search/Filter) → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Priorities)
   - Developer B: User Story 2 (Tags)
   - Developer C: User Story 3 (Due Dates)
   - Developer D: User Story 4 (Search/Filter)
3. Stories complete and integrate independently
4. Then tackle P2 stories (Recurring, Reminders, Events, Dapr)

---

## Task Summary

| Phase | User Story | Task Count | Priority |
|-------|-----------|------------|----------|
| 1 | Setup | 6 | N/A |
| 2 | Foundational | 15 | N/A |
| 3 | US1 - Priorities | 15 | P1 |
| 4 | US2 - Tags | 20 | P1 |
| 5 | US3 - Due Dates | 14 | P1 |
| 6 | US4 - Search/Filter | 18 | P1 |
| 7 | US5 - Recurring Tasks | 20 | P2 |
| 8 | US6 - Reminders | 22 | P2 |
| 9 | US7 - Events | 12 | P2 |
| 10 | US8 - Dapr | 8 | P2 |
| 11 | Polish | 8 | N/A |
| **Total** | | **158** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
