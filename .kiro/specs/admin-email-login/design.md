# Admin Email Login Bugfix Design

## Overview

The admin login functionality is incomplete - the frontend only provides Google OAuth authentication while admin users need email/password authentication to access the existing backend `POST /api/v1/auth/login` endpoint. This fix adds an email/password login form to the LoginPage component and a corresponding `loginWithEmail` method to the authStore, enabling administrators to authenticate and access protected operations.

## Glossary

- **Bug_Condition (C)**: The condition where an admin user attempts to authenticate with email/password credentials but no form or method exists to do so
- **Property (P)**: The desired behavior where email/password credentials are accepted, validated via the backend API, and result in proper authentication state
- **Preservation**: Existing Google OAuth login flow, logout functionality, session restoration, and authenticated user redirect must remain unchanged
- **authStore**: The Zustand store in `frontend/src/stores/authStore.ts` that manages authentication state
- **LoginPage**: The React component in `frontend/src/components/Admin/LoginPage.tsx` that renders the login UI
- **authApi**: The API service in `frontend/src/services/api.ts` that communicates with the backend

## Bug Details

### Bug Condition

The bug manifests when an admin user visits the login page and needs to authenticate with email/password credentials. The LoginPage component only renders a Google OAuth button, and the authStore only provides a `loginWithGoogle()` method with no support for email/password authentication.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type { authMethod: string, credentials?: { email: string, password: string } }
  OUTPUT: boolean
  
  RETURN input.authMethod == 'email_password'
         AND input.credentials IS NOT NULL
         AND loginWithEmailMethodExists() == false
         AND emailPasswordFormExists() == false
END FUNCTION
```

### Examples

- Admin visits `/login` and wants to enter email "admin@example.com" and password "secret123" → No form fields exist to enter credentials
- Admin has valid credentials stored in the `users` table → Cannot authenticate because frontend lacks email/password support
- Admin tries to access protected endpoints (create/update/delete plaques) → Cannot obtain JWT token without email/password login
- Admin with invalid credentials attempts login → No mechanism exists to even attempt the login and receive an error

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Google OAuth login via "Sign in with Google" button must continue to work exactly as before
- Logout functionality must continue to clear auth state and stored tokens
- Session restoration on page load must continue to check for existing sessions
- Authenticated users visiting `/login` must continue to be redirected to home page
- The visual styling and layout of the existing Google OAuth button must remain consistent

**Scope:**
All inputs that do NOT involve email/password authentication should be completely unaffected by this fix. This includes:
- Google OAuth authentication flow
- Logout operations
- Session state management
- Navigation and routing behavior

## Hypothesized Root Cause

Based on the bug description, the root cause is incomplete implementation:

1. **Missing UI Form**: The `LoginPage.tsx` component was built with only Google OAuth in mind, lacking email/password input fields and form submission handling

2. **Missing Store Method**: The `authStore.ts` only implements `loginWithGoogle()` and lacks a `loginWithEmail()` method to handle email/password authentication

3. **Unused API Endpoint**: The `authApi.login()` method exists in `api.ts` but is never called from the frontend because there's no UI or store method to trigger it

4. **No Token Storage for Email Login**: While the API returns a JWT token, there's no code path to store it in localStorage and update the auth state for email/password logins

## Correctness Properties

Property 1: Bug Condition - Email/Password Login Form Exists

_For any_ admin user visiting the login page, the fixed LoginPage component SHALL display email and password input fields with a submit button, allowing credentials to be entered and submitted.

**Validates: Requirements 2.1**

Property 2: Bug Condition - Email/Password Authentication Works

_For any_ valid email/password credentials submitted through the login form, the fixed system SHALL call the backend `POST /api/v1/auth/login` endpoint, store the returned JWT token in localStorage, update the auth state to authenticated, and redirect to the home page.

**Validates: Requirements 2.2, 2.3**

Property 3: Bug Condition - Invalid Credentials Show Error

_For any_ invalid email/password credentials submitted through the login form, the fixed system SHALL display an appropriate error message to the user without crashing or leaving the UI in an inconsistent state.

**Validates: Requirements 2.4**

Property 4: Preservation - Google OAuth Continues Working

_For any_ user clicking "Sign in with Google", the fixed code SHALL produce exactly the same behavior as the original code, preserving the Supabase OAuth authentication flow.

**Validates: Requirements 3.1**

Property 5: Preservation - Logout and Session Management

_For any_ logout operation or page load session check, the fixed code SHALL produce exactly the same behavior as the original code, preserving session management functionality.

**Validates: Requirements 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

**File**: `frontend/src/stores/authStore.ts`

**Changes**:
1. **Add AdminUser type**: Create a type to represent admin users from the backend (distinct from Supabase User)
2. **Extend AuthState interface**: Add `loginWithEmail(email: string, password: string): Promise<void>` method signature
3. **Add error state**: Add `error: string | null` to track login errors
4. **Implement loginWithEmail**: 
   - Call `authApi.login(email, password)`
   - Store returned `access_token` in localStorage as `'token'`
   - Update auth state to authenticated
   - Handle errors by setting error state
5. **Update logout**: Clear the `'token'` from localStorage in addition to Supabase signOut
6. **Update init**: Check for existing JWT token in localStorage and restore admin session

**File**: `frontend/src/components/Admin/LoginPage.tsx`

**Changes**:
1. **Add form state**: Use `useState` for email, password, and loading state
2. **Add email input field**: Text input with proper type, placeholder, and validation
3. **Add password input field**: Password input with proper type and placeholder
4. **Add submit button**: Button to trigger email/password login
5. **Add error display**: Show error message from authStore when login fails
6. **Add form submission handler**: Call `loginWithEmail` from authStore
7. **Add visual separator**: "or" divider between email/password form and Google OAuth button

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, verify the bug exists on unfixed code by confirming no email/password form exists, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Confirm the bug exists BEFORE implementing the fix by verifying the absence of email/password login functionality.

**Test Plan**: Inspect the LoginPage component and authStore to confirm no email/password support exists.

**Test Cases**:
1. **No Email Input Test**: Verify LoginPage has no email input field (will pass on unfixed code, confirming bug)
2. **No Password Input Test**: Verify LoginPage has no password input field (will pass on unfixed code, confirming bug)
3. **No loginWithEmail Method Test**: Verify authStore has no loginWithEmail method (will pass on unfixed code, confirming bug)

**Expected Counterexamples**:
- Email input field is missing from LoginPage
- Password input field is missing from LoginPage
- loginWithEmail method is missing from authStore

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := loginWithEmail_fixed(input.credentials.email, input.credentials.password)
  ASSERT emailFormExists()
  ASSERT passwordFormExists()
  IF validCredentials(input.credentials) THEN
    ASSERT localStorage.getItem('token') IS NOT NULL
    ASSERT authState.isAuthenticated == true
  ELSE
    ASSERT errorMessageDisplayed()
  END IF
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT loginWithGoogle_original() = loginWithGoogle_fixed()
  ASSERT logout_original() = logout_fixed()
  ASSERT init_original() = init_fixed()
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for Google OAuth login, logout, and session management, then write tests to verify this behavior continues after fix.

**Test Cases**:
1. **Google OAuth Preservation**: Verify clicking "Sign in with Google" triggers Supabase OAuth flow
2. **Logout Preservation**: Verify logout clears auth state and calls Supabase signOut
3. **Session Restoration Preservation**: Verify init() checks for existing Supabase session
4. **Redirect Preservation**: Verify authenticated users are redirected from /login to /

### Unit Tests

- Test LoginPage renders email and password input fields
- Test LoginPage renders submit button for email/password login
- Test loginWithEmail calls authApi.login with correct parameters
- Test loginWithEmail stores token in localStorage on success
- Test loginWithEmail sets error state on failure
- Test loginWithGoogle continues to work unchanged
- Test logout clears both Supabase session and localStorage token

### Property-Based Tests

- Generate random valid email/password combinations and verify successful authentication flow
- Generate random invalid credentials and verify error handling
- Test that all Google OAuth interactions continue to work across many scenarios

### Integration Tests

- Test full email/password login flow from form submission to authenticated state
- Test full Google OAuth login flow remains unchanged
- Test switching between email/password and Google OAuth login methods
- Test error recovery after failed login attempt
