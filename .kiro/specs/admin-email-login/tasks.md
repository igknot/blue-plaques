# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Missing Email/Password Login Form
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Scope the property to concrete failing cases - verify email input, password input, and loginWithEmail method exist
  - Test that LoginPage component renders email and password input fields
  - Test that authStore exports a loginWithEmail method
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found: "LoginPage has no email input field", "LoginPage has no password input field", "authStore has no loginWithEmail method"
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Google OAuth and Session Management
  - **IMPORTANT**: Follow observation-first methodology
  - Observe: loginWithGoogle() calls supabase.auth.signInWithOAuth with provider 'google' on unfixed code
  - Observe: logout() calls supabase.auth.signOut() and clears auth state on unfixed code
  - Observe: init() calls supabase.auth.getSession() and sets up onAuthStateChange listener on unfixed code
  - Observe: LoginPage redirects authenticated users to '/' on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Fix for missing email/password login functionality

  - [x] 3.1 Add loginWithEmail method to authStore
    - Add `error: string | null` state to AuthState interface
    - Add `clearError: () => void` method to clear error state
    - Add `loginWithEmail: (email: string, password: string) => Promise<void>` method signature to AuthState interface
    - Implement loginWithEmail: call authApi.login(email, password), store access_token in localStorage as 'token', update auth state to authenticated
    - Handle errors by setting error state with appropriate message
    - Update logout to also clear 'token' from localStorage
    - _Bug_Condition: isBugCondition(input) where input.authMethod == 'email_password' AND loginWithEmailMethodExists() == false_
    - _Expected_Behavior: loginWithEmail stores JWT token and sets isAuthenticated = true on success_
    - _Preservation: logout() must continue to call supabase.auth.signOut() in addition to clearing localStorage_
    - _Requirements: 2.2, 2.3, 2.4, 3.2_

  - [x] 3.2 Add email/password login form to LoginPage
    - Add useState hooks for email, password, and loading state
    - Add email input field with type="email", placeholder, and onChange handler
    - Add password input field with type="password", placeholder, and onChange handler
    - Add submit button that calls loginWithEmail from authStore
    - Add form submission handler with loading state management
    - Add error display section to show authStore.error when present
    - Add visual separator ("or" divider) between email/password form and Google OAuth button
    - _Bug_Condition: isBugCondition(input) where emailPasswordFormExists() == false_
    - _Expected_Behavior: Form renders email input, password input, submit button, and error display_
    - _Preservation: Google OAuth button must remain unchanged and functional_
    - _Requirements: 2.1, 2.4, 3.1_

  - [x] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Email/Password Login Form Exists
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2_

  - [x] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Google OAuth and Session Management
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
