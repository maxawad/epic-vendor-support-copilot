# Testing Guide

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_retriever.py -v
pytest tests/test_api.py -v
pytest tests/test_memory.py -v
```

## Test Coverage

### Retriever Tests (`test_retriever.py`)
- FAQ data loads correctly with 17 entries
- Authentication queries return auth-category results
- Billing queries return billing-category results
- Reporting queries return reporting-category results
- Empty/blank queries return no results
- Auth-related queries get relevance boosting

### API Tests (`test_api.py`)
- Health endpoint returns 200
- Chat endpoint accepts valid messages
- Chat endpoint returns sources
- Empty message returns 400 error
- Session ID is persisted across requests

### Memory Tests (`test_memory.py`)
- Messages are stored per session
- History is retrievable
- Memory used flag works correctly
- Session clearing works
- Long-term memory storage and retrieval
- Max history limit is enforced

## Manual Testing

### Demo Flow

1. **Ask**: "I forgot my password"
   - Expected: Routes to admin/support, cites Password Reset Help source
   - Memory: `false`

2. **Follow-up**: "I still can't log in"
   - Expected: Uses conversation context, references previous auth issue
   - Memory: `true`

3. **New topic**: "How do I view my invoices?"
   - Expected: Returns billing info, cites Invoice Management source
   - Memory: `true` (session continues)

4. **Ambiguous**: "help"
   - Expected: Asks for clarification
