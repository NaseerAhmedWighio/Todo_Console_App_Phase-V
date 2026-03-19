"""Debug OpenAPI schema issue"""

from dotenv import load_dotenv

load_dotenv()

from app.api.todo_routes import TodoCreate, TodoResponse
from app.models.todo import Todo

print("Testing TodoCreate schema...")
try:
    schema = TodoCreate.model_json_schema()
    print(f"[OK] TodoCreate: {list(schema.get('properties', {}).keys())[:5]}")
except Exception as e:
    print(f"[FAIL] TodoCreate: {e}")

print("\nTesting TodoResponse schema...")
try:
    schema = TodoResponse.model_json_schema()
    print(f"[OK] TodoResponse: {list(schema.get('properties', {}).keys())[:5]}")
except Exception as e:
    print(f"[FAIL] TodoResponse: {e}")

print("\nTesting Todo schema...")
try:
    schema = Todo.model_json_schema()
    print(f"[OK] Todo: {list(schema.get('properties', {}).keys())[:5]}")
except Exception as e:
    print(f"[FAIL] Todo: {e}")

print("\n\nChecking field defaults...")
for field_name, field_info in Todo.model_fields.items():
    if field_info.default is not None and callable(field_info.default):
        print(f"  {field_name}: default={field_info.default} (callable)")
    if field_info.default_factory is not None:
        print(
            f"  {field_name}: default_factory={field_info.default_factory} (callable: {callable(field_info.default_factory)})"
        )
        import asyncio

        if asyncio.iscoroutinefunction(field_info.default_factory):
            print("    *** THIS IS A COROUTINE! ***")
