# %% [markdown]
# # Automation with Python
# 
# This notebook demonstrates the technical skills needed for effective AI-assisted development:
# - Refactoring code
# - Writing unit tests
# - Creating helper functions
# - Building API wrappers
# 
# These skills are essential for managing technical debt and maintaining code quality when working with AI tools.
# 

# %% [markdown]
# ## Learning Goals
# 
# After this lesson, you will be able to:
# 
# - [ ] Refactor code to improve maintainability and reduce technical debt
# - [ ] Write unit tests using pytest to ensure code quality
# - [ ] Create reusable helper functions following design patterns
# - [ ] Build API wrappers with error handling and retry logic
# - [ ] Apply these skills together in real-world automation scenarios
# 

# %% [markdown]
# ## Introduction
# 
# Building on the Python Low Code Fundamentals lesson, we'll now practice the technical skills needed for professional AI-assisted development. These skills help us:
# 
# - **Manage technical debt** by writing clean, maintainable code
# - **Ensure code quality** through comprehensive testing
# - **Improve reusability** with helper functions and design patterns
# - **Handle complexity** with API wrappers that abstract away implementation details
# 
# Remember: Code that is not tested is not usable. These practices are essential for professional development.
# 

# %% [markdown]
# ---
# 
# ## 1. Helper Functions
# 
# Helper functions are small, reusable functions that perform specific tasks. They improve code readability, testability, and maintainability by breaking complex operations into manageable pieces.
# 

# %% [markdown]
# ### Example: Messy Code Without Helpers
# 
# Let's start with an example of code that processes user data. Notice how everything is mixed together:
# 

# %%
# BAD: Everything in one place, hard to test and reuse
def process_users(users_data):
    results = []
    for user in users_data:
        # Validate email
        if '@' not in user.get('email', ''):
            continue
        
        # Format name
        name = user.get('name', '').strip().title()
        
        # Calculate age
        from datetime import datetime
        birth_year = user.get('birth_year', 0)
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # Create result
        result = {
            'name': name,
            'email': user['email'].lower(),
            'age': age,
            'status': 'active' if age >= 18 else 'minor'
        }
        results.append(result)
    return results

# This code is hard to test individual parts and reuse logic


# %% [markdown]
# ### Refactored Version with Helper Functions
# 
# Now let's break this down into helper functions:
# 

# %%
from datetime import datetime

# Helper function 1: Validate email
def is_valid_email(email):
    """Check if email contains @ symbol."""
    return bool(email and '@' in email)

# Helper function 2: Format name
def format_name(name):
    """Format name to title case."""
    return name.strip().title() if name else ''

# Helper function 3: Calculate age
def calculate_age(birth_year):
    """Calculate age from birth year."""
    if not birth_year or birth_year <= 0:
        return None
    return datetime.now().year - birth_year

# Helper function 4: Determine status
def get_user_status(age):
    """Determine user status based on age."""
    if age is None:
        return 'unknown'
    return 'active' if age >= 18 else 'minor'

# Helper function 5: Normalize email
def normalize_email(email):
    """Normalize email to lowercase."""
    return email.lower().strip() if email else ''

# Main function using helpers
def process_users(users_data):
    """Process user data using helper functions."""
    results = []
    for user in users_data:
        email = user.get('email', '')
        if not is_valid_email(email):
            continue
        
        result = {
            'name': format_name(user.get('name', '')),
            'email': normalize_email(email),
            'age': calculate_age(user.get('birth_year')),
            'status': get_user_status(calculate_age(user.get('birth_year')))
        }
        results.append(result)
    return results

# %% [markdown]
# ### Benefits of Helper Functions
# 
# **Reusability:** Helper functions can be used across different parts of your codebase.
# 
# **Testability:** Each helper function can be tested independently.
# 
# **Maintainability:** Changes to logic are isolated to specific functions.
# 
# **Readability:** The main function reads like a high-level description of what it does.
# 

# %% [markdown]
# ---
# 
# ## 2. Refactoring Code
# 
# Refactoring is the process of restructuring existing code without changing its external behavior. It improves code quality, reduces technical debt, and makes code easier to understand and maintain.
# 

# %% [markdown]
# ### Example: Monolithic Function That Needs Refactoring
# 
# Here's a function that does too much:
# 

# %%
# BAD: One function doing everything
def process_api_data(api_url, api_key, user_id, retry_count=3):
    import requests
    import json
    import time
    
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'user_id': user_id}
    
    for attempt in range(retry_count):
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process data
            processed = []
            for item in data.get('items', []):
                if item.get('status') == 'active':
                    processed.append({
                        'id': item['id'],
                        'name': item['name'].upper(),
                        'value': float(item.get('value', 0)) * 1.1
                    })
            
            return {'success': True, 'data': processed}
            
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)
                continue
            return {'success': False, 'error': 'Timeout after retries'}
        except requests.exceptions.HTTPError as e:
            return {'success': False, 'error': f'HTTP Error: {e}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    return {'success': False, 'error': 'Max retries exceeded'}


# %% [markdown]
# ### Step-by-Step Refactoring
# 
# Let's refactor this into smaller, focused functions:
# 

# %%
import requests
import time
from typing import Dict, List, Optional

# Step 1: Extract API request logic
def make_api_request(url: str, headers: Dict, params: Dict, timeout: int = 10) -> requests.Response:
    """Make HTTP GET request with timeout."""
    return requests.get(url, headers=headers, params=params, timeout=timeout)

# Step 2: Extract retry logic
def retry_request(func, max_retries: int = 3, backoff_factor: int = 2):
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
                continue
            raise
    raise Exception('Max retries exceeded')

# Step 3: Extract data processing logic
def process_items(items: List[Dict]) -> List[Dict]:
    """Process items, filtering active ones and transforming data."""
    processed = []
    for item in items:
        if item.get('status') == 'active':
            processed.append({
                'id': item['id'],
                'name': item['name'].upper(),
                'value': float(item.get('value', 0)) * 1.1
            })
    return processed

# Step 4: Extract error handling
def handle_api_errors(func):
    """Handle common API errors."""
    try:
        return {'success': True, 'data': func()}
    except requests.exceptions.Timeout as e:
        return {'success': False, 'error': f'Timeout: {str(e)}'}
    except requests.exceptions.HTTPError as e:
        return {'success': False, 'error': f'HTTP Error: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

# Step 5: Refactored main function
def process_api_data(api_url: str, api_key: str, user_id: str, retry_count: int = 3) -> Dict:
    """Process API data using refactored helper functions."""
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'user_id': user_id}
    
    def fetch_and_process():
        response = make_api_request(api_url, headers, params)
        response.raise_for_status()
        data = response.json()
        return process_items(data.get('items', []))
    
    def fetch_with_retry():
        return retry_request(fetch_and_process, max_retries=retry_count)
    
    return handle_api_errors(fetch_with_retry)


# %% [markdown]
# ### Refactoring Principles Applied
# 
# **Encapsulation:** Each function hides implementation details and exposes a clear interface.
# 
# **Composition:** The main function composes smaller functions to achieve its goal.
# 
# **Abstraction:** Higher-level functions don't need to know about HTTP details, retry logic, or data transformation specifics.
# 
# **Extensibility:** Easy to add new features (e.g., caching, logging) without modifying existing code.
# 

# %% [markdown]
# ---
# 
# ## 3. API Wrapper
# 
# An API wrapper is a class or module that provides a simplified interface to an API, handling authentication, error handling, retries, and other complexities. This abstraction makes API usage easier and more maintainable.
# 

# %% [markdown]
# ### Example: Direct API Calls (Messy and Repetitive)
# 
# Without a wrapper, API calls are repetitive and error-prone:
# 

# %%
# BAD: Repetitive OpenAI API calls without a wrapper
import os
from openai import OpenAI

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Call 1: Simple question - manual error handling every time
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What is Python?"}]
    )
    answer = response.choices[0].message.content
    print(f"Answer 1: {answer[:80]}...")
except Exception as e:
    print(f"Error: {e}")

# Call 2: Same pattern repeated with no retry logic
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What is JavaScript?"}]
    )
    answer = response.choices[0].message.content
    print(f"Answer 2: {answer[:80]}...")
except Exception as e:
    print(f"Error: {e}")

# Call 3: With system prompt - even more repetition
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain APIs in one sentence."}
        ]
    )
    answer = response.choices[0].message.content
    print(f"Answer 3: {answer[:80]}...")
except Exception as e:
    print(f"Error: {e}")

# %% [markdown]
# ### Creating an API Wrapper Class
# 
# Let's create a clean, reusable API wrapper:
# 

# %%
import os
import time
from openai import OpenAI
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

@dataclass
class APIResponse:
    """Standardized API response."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    usage: Optional[Dict] = None

class OpenAIWrapper:
    """Wrapper for OpenAI API with error handling and retry logic."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini",
                 timeout: int = 30, max_retries: int = 3):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
    
    def _make_request(self, messages: List[Dict], **kwargs):
        """Make API request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    timeout=self.timeout,
                    **kwargs
                )
                return response
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
    
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> APIResponse:
        """Send a chat message and get a response."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self._make_request(messages)
            return APIResponse(
                success=True,
                data=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Request failed: {str(e)}'
            )
    
    def chat_with_history(self, messages: List[Dict]) -> APIResponse:
        """Send a multi-turn conversation."""
        try:
            response = self._make_request(messages)
            return APIResponse(
                success=True,
                data=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f'Request failed: {str(e)}'
            )

# %% [markdown]
# 

# %%
# Initialize wrapper
ai = OpenAIWrapper(model="gpt-4o-mini")

# Clean, consistent API calls
response = ai.chat("What is Python?")
if response.success:
    print(f"Response: {response.data}")
    print(f"Tokens used: {response.usage}")
else:
    print(f"Error: {response.error}")

# With system prompt
response = ai.chat(
    prompt="Explain APIs in one sentence.",
    system_prompt="You are a concise technical writer."
)
if response.success:
    print(f"\nResponse: {response.data}")
    print(f"Tokens used: {response.usage}")

# Multi-turn conversation
response = ai.chat_with_history([
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "What is a variable?"},
    {"role": "assistant", "content": "A variable is a named container that stores a value."},
    {"role": "user", "content": "Give me an example in Python."}
])
if response.success:
    print(f"\nMulti-turn response: {response.data}")
    print(f"Tokens used: {response.usage}")

# %% [markdown]
# ### Benefits of API Wrappers
# 
# **Abstraction:** Hide implementation details (authentication, retries, error handling).
# 
# **Error Handling:** Centralized error handling logic.
# 
# **Maintainability:** Changes to API interaction logic happen in one place.
# 
# **Consistency:** All API calls follow the same pattern.
# 
# **Testability:** Easy to mock for testing.
# 

# %% [markdown]
# ---
# 
# ## 4. Unit Tests
# 
# **Remember: A code that is not tested is not usable.** Unit tests verify that individual functions work correctly and help prevent regressions when code changes.
# 

# %% [markdown]
# ### Installing pytest
# 
# First, let's install pytest (if not already installed):
# 

# %%
!pip install pytest


# %% [markdown]
# ### Example Function to Test
# 
# Let's use our helper functions from earlier:
# 

# %%
# Our helper functions (repeated for clarity in notebook)
from datetime import datetime

def is_valid_email(email):
    """Check if email contains @ symbol."""
    return bool(email and '@' in email)

def format_name(name):
    """Format name to title case."""
    return name.strip().title() if name else ''

def calculate_age(birth_year):
    """Calculate age from birth year."""
    if not birth_year or birth_year <= 0:
        return None
    return datetime.now().year - birth_year

def get_user_status(age):
    """Determine user status based on age."""
    if age is None:
        return 'unknown'
    return 'active' if age >= 18 else 'minor'

# %% [markdown]
# ### Writing Unit Tests with pytest
# 
# Now let's write comprehensive tests:
# 

# %%
import pytest
from datetime import datetime

# Test helper functions
class TestHelperFunctions:
    
    def test_is_valid_email_valid(self):
        """Test valid email addresses."""
        assert is_valid_email('user@example.com') == True
        assert is_valid_email('test.email@domain.co.uk') == True
    
    def test_is_valid_email_invalid(self):
        """Test invalid email addresses."""
        assert is_valid_email('notanemail') == False
        assert is_valid_email('') == False
        assert is_valid_email(None) == False
    
    def test_format_name(self):
        """Test name formatting."""
        assert format_name('john doe') == 'John Doe'
        assert format_name('  ALICE SMITH  ') == 'Alice Smith'
        assert format_name('') == ''
        assert format_name(None) == ''
    
    def test_calculate_age_valid(self):
        """Test age calculation with valid birth years."""
        current_year = datetime.now().year
        assert calculate_age(current_year - 25) == 25
        assert calculate_age(2000) == current_year - 2000
    
    def test_calculate_age_invalid(self):
        """Test age calculation with invalid inputs."""
        assert calculate_age(0) == None
        assert calculate_age(-1) == None
        assert calculate_age(None) == None
    
    def test_get_user_status(self):
        """Test user status determination."""
        assert get_user_status(25) == 'active'
        assert get_user_status(18) == 'active'
        assert get_user_status(17) == 'minor'
        assert get_user_status(0) == 'minor'
        assert get_user_status(None) == 'unknown'

# Run tests directly (Jupyter-compatible — __file__ is not available in notebooks)
test_suite = TestHelperFunctions()
for method_name in sorted(dir(test_suite)):
    if method_name.startswith('test_'):
        try:
            getattr(test_suite, method_name)()
            print(f"✓ {method_name} passed")
        except AssertionError as e:
            print(f"✗ {method_name} FAILED: {e}")

print("\nAll tests complete!")

# %% [markdown]
# 

# %%
def test_edge_cases():
    """Test edge cases for helper functions."""
    # Empty strings
    assert format_name('') == ''
    assert is_valid_email('') == False
    
    # None values
    assert format_name(None) == ''
    assert calculate_age(None) == None
    assert get_user_status(None) == 'unknown'
    
    # Boundary values
    assert get_user_status(18) == 'active'  # Exactly 18
    assert get_user_status(17) == 'minor'    # Just below 18
    assert get_user_status(0) == 'minor'     # Minimum age
    
    # Invalid inputs
    assert calculate_age(0) == None
    assert calculate_age(-100) == None
    assert calculate_age(3000) == datetime.now().year - 3000  # Future year (still valid)

test_edge_cases()
print("✓ All edge case tests passed!")

# %% [markdown]
# ### Test-Driven Development (TDD) Best Practices
# 
# 1. **Write tests first** (Red) - Define what you want before implementing
# 2. **Write minimal code** (Green) - Make tests pass
# 3. **Refactor** (Refactor) - Improve code while keeping tests green
# 
# 4. **Test coverage:** Aim for high coverage of critical paths
# 5. **Test isolation:** Each test should be independent
# 6. **Clear test names:** Test names should describe what they test
# 7. **Test edge cases:** Always test boundaries and error conditions
# 

# %% [markdown]
# ---
# 
# ## 5. Integration Example
# 
# Let's put it all together: helper functions, refactored code, API wrapper, and tests in a complete automation example.
# 

# %% [markdown]
# ### Complete Example: User Data Automation
# 
# This example demonstrates all concepts working together:
# 

# %%
# Complete automation example combining all concepts

class UserDataAutomation:
    """Complete automation system using helper functions, OpenAI wrapper, and proper structure."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.ai = OpenAIWrapper(model=model)
    
    def process_user(self, raw_user_data: Dict) -> Dict:
        """Process raw user data using helper functions."""
        if not is_valid_email(raw_user_data.get('email', '')):
            return {'error': 'Invalid email'}
        
        birth_year = raw_user_data.get('birth_year')
        age = calculate_age(birth_year)
        
        return {
            'id': raw_user_data.get('id'),
            'name': format_name(raw_user_data.get('name', '')),
            'email': raw_user_data.get('email', '').lower().strip(),
            'age': age,
            'status': get_user_status(age)
        }
    
    def enrich_user(self, user_data: Dict) -> Dict:
        """Use LLM to generate a professional summary for a user."""
        response = self.ai.chat(
            prompt=f"Write a one-sentence professional bio for someone named {user_data['name']}, "
                   f"age {user_data['age']}, status: {user_data['status']}.",
            system_prompt="You are a concise professional bio writer."
        )
        if response.success:
            user_data['bio'] = response.data
        return user_data
    
    def automate_user_processing(self, users_data: List[Dict], enrich: bool = False) -> List[Dict]:
        """Automate processing multiple users with optional LLM enrichment."""
        results = []
        
        for user in users_data:
            # Process data with helper functions
            processed = self.process_user(user)
            if 'error' in processed:
                results.append({'user': user.get('name', 'Unknown'), 'error': processed['error']})
                continue
            
            # Optionally enrich with LLM
            if enrich:
                processed = self.enrich_user(processed)
            
            results.append(processed)
        
        return results

# Example usage with local data
automation = UserDataAutomation(model="gpt-4o-mini")

# Sample user data
users = [
    {'id': '1', 'name': 'john doe', 'email': 'john@example.com', 'birth_year': 1990},
    {'id': '2', 'name': 'jane smith', 'email': 'jane@example.com', 'birth_year': 2010},
    {'id': '3', 'name': 'bad user', 'email': 'noemail', 'birth_year': 1985},
]

# Process without LLM enrichment (uses helper functions only)
results = automation.automate_user_processing(users)

for result in results:
    if 'error' in result:
        print(f"Error for {result.get('user', 'unknown')}: {result['error']}")
    else:
        print(f"Processed: {result['name']} ({result['status']})")

# %% [markdown]
# 

# %% [markdown]
# ### Real-World Application
# 
# This pattern is used in real-world automation:
# 
# - **Data pipelines:** Processing data from multiple sources
# - **API integrations:** Connecting different services
# - **Automated reporting:** Generating reports from various data sources
# - **Data validation:** Validating and transforming data before storage
# 
# The key is combining:
# 1. **Helper functions** for reusable logic
# 2. **Refactored code** with clear separation of concerns
# 3. **API wrappers** for consistent API interactions
# 4. **Unit tests** to ensure everything works correctly
# 

# %% [markdown]
# ---
# 
# ## Summary
# 
# ### Key Takeaways
# 
# 1. **Helper Functions:** Break complex operations into small, reusable, testable functions
# 2. **Refactoring:** Restructure code to improve maintainability without changing behavior
# 3. **API Wrappers:** Abstract API complexity with consistent interfaces and error handling
# 4. **Unit Tests:** Ensure code quality and prevent regressions
# 
# ### Best Practices
# 
# - **Write tests first** (TDD approach)
# - **Refactor incrementally** - small changes, test frequently
# - **Use helper functions** - don't repeat yourself (DRY principle)
# - **Abstract complexity** - hide implementation details in wrappers
# - **Test edge cases** - always test boundaries and error conditions
# 
# ### Next Steps
# 
# - Practice refactoring existing code
# - Write tests for your helper functions
# - Create API wrappers for APIs you use frequently
# - Apply these patterns in your labs and projects
# 
# Remember: **Code that is not tested is not usable.** These skills are essential for professional AI-assisted development and managing technical debt.
# 


