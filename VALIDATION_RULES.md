# Enterprise-Level Registration Validation Rules

## Overview
This document outlines the strict, bank-level validation rules implemented for the UnBoreMe registration system.

---

## Validation Rules by Field

### 1. USERNAME
**Requirements:**
- ✅ Minimum 4 characters, maximum 32 characters
- ✅ Must start with a letter
- ✅ Can contain only letters, numbers, and underscores
- ✅ Reserved usernames blocked: admin, root, system, administrator, test, user, guest, null, undefined
- ✅ Must be unique (no duplicates)

**Error Messages:**
- "Username is required"
- "Username must be at least 4 characters long"
- "Username cannot exceed 32 characters"
- "Username must start with a letter and contain only letters, numbers, and underscores"
- "This username is reserved and cannot be used"
- "Username already exists. Please choose another one"

---

### 2. EMAIL
**Requirements:**
- ✅ RFC 5322 compliant format
- ✅ Must not exceed 254 characters
- ✅ No double dots (..) or invalid sequences
- ✅ Disposable email domains blocked (tempmail, throwaway, guerrilla, 10minute, mailinator)
- ✅ Must be unique (no duplicates)

**Error Messages:**
- "Email address is required"
- "Invalid email format. Please enter a valid email address"
- "Email address is too long"
- "Email contains invalid character sequences"
- "Disposable email addresses are not allowed"
- "Email address already registered. Please use another email or login"

---

### 3. PASSWORD
**Requirements (Banking-Level):**
- ✅ Minimum 12 characters, maximum 128 characters
- ✅ Must contain at least one uppercase letter (A-Z)
- ✅ Must contain at least one lowercase letter (a-z)
- ✅ Must contain at least one digit (0-9)
- ✅ Must contain at least one special character (!@#$%^&*()_+-=[]{};:'",.<>?/\|`~)
- ✅ No 3+ consecutive repeated characters
- ✅ No common patterns (password, 123456, qwerty, admin, username)
- ✅ No sequential characters (abc, 123, etc.)

**Error Messages:**
- "Password is required"
- "Password must be at least 12 characters long"
- "Password is too long (maximum 128 characters)"
- "Password must contain at least one uppercase letter"
- "Password must contain at least one lowercase letter"
- "Password must contain at least one number"
- "Password must contain at least one special character (!@#$%^&*-_+=)"
- "Password contains too many repeated characters"
- "Password is too common or contains username. Choose a stronger password"
- "Password contains sequential characters. Choose a more secure password"

---

### 4. CONFIRM PASSWORD
**Requirements:**
- ✅ Must match password exactly

**Error Messages:**
- "Please confirm your password"
- "Passwords do not match"

---

### 5. FIRST NAME
**Requirements:**
- ✅ Minimum 2 characters, maximum 50 characters
- ✅ Can contain only letters, spaces, hyphens, and apostrophes
- ✅ No excessive spacing (2+ consecutive spaces)

**Error Messages:**
- "First name is required"
- "First name must be at least 2 characters long"
- "First name is too long (maximum 50 characters)"
- "First name can only contain letters, spaces, hyphens, and apostrophes"
- "First name contains excessive spacing"

---

### 6. MIDDLE NAME (Optional)
**Requirements:**
- ✅ Maximum 50 characters
- ✅ Can contain only letters, spaces, hyphens, and apostrophes
- ✅ No excessive spacing (2+ consecutive spaces)

**Error Messages:**
- "Middle name is too long (maximum 50 characters)"
- "Middle name can only contain letters, spaces, hyphens, and apostrophes"
- "Middle name contains excessive spacing"

---

### 7. LAST NAME
**Requirements:**
- ✅ Minimum 2 characters, maximum 50 characters
- ✅ Can contain only letters, spaces, hyphens, and apostrophes
- ✅ No excessive spacing (2+ consecutive spaces)

**Error Messages:**
- "Last name is required"
- "Last name must be at least 2 characters long"
- "Last name is too long (maximum 50 characters)"
- "Last name can only contain letters, spaces, hyphens, and apostrophes"
- "Last name contains excessive spacing"

---

### 8. BIRTHDAY (Optional)
**Requirements:**
- ✅ Must be a valid date (YYYY-MM-DD format)
- ✅ Cannot be in the future
- ✅ User must be at least 13 years old
- ✅ User cannot be older than 120 years

**Error Messages:**
- "Birthday cannot be in the future"
- "You must be at least 13 years old to register"
- "Invalid birth date. Please verify your date of birth"
- "Invalid date format. Please use YYYY-MM-DD format"

---

### 9. CONTACT NUMBER (Optional)
**Requirements:**
- ✅ Minimum 10 digits, maximum 15 digits
- ✅ Can contain numbers and valid separators (+, -, space, parentheses)
- ✅ Philippine format validation: +63 9XXXXXXXXX (if starts with +63 or 63)

**Error Messages:**
- "Contact number must contain only numbers and valid separators (+, -, space, parentheses)"
- "Contact number is too short (minimum 10 digits)"
- "Contact number is too long (maximum 15 digits)"
- "Invalid Philippine mobile number format (should be 9XXXXXXXXX)"

---

## User Experience Features

### ✅ NO Input Clearing on Error
- All entered values are preserved when validation fails
- Users don't have to re-enter correct information

### ✅ Inline Error Messages
- Errors appear directly below invalid fields
- No intrusive alert popups

### ✅ Visual Error Highlighting
- Invalid fields are highlighted with red border
- Red glow effect for visibility
- Subtle background tint

### ✅ Field-Specific Errors
- Each field shows its own specific error message
- Multiple fields can show errors simultaneously

### ✅ Professional Error Messages
- Clear, actionable feedback
- Banking-level professional language
- Specific guidance on how to fix issues

---

## Security Features

### 🔒 Server-Side Validation Only
- All validation happens on the backend
- No reliance on client-side validation
- Protection against tampering

### 🔒 Input Sanitization
- Automatic trimming of whitespace
- Email normalization (lowercase)
- Prevention of injection attacks

### 🔒 Reserved Username Protection
- Common administrative usernames blocked
- Prevents social engineering attacks

### 🔒 Disposable Email Blocking
- Prevents abuse from temporary email services
- Ensures legitimate user registration

### 🔒 Strong Password Enforcement
- Prevents weak, common passwords
- Blocks sequential and repeated patterns
- Banking-level complexity requirements

---

## Testing Examples

### Valid Registration Example:
```
Username: john_doe2024
Email: john.doe@gmail.com
Password: MySecure@Pass123
First Name: John
Middle Name: Michael
Last Name: Doe
Birthday: 1995-05-15
Contact: +63 912 345 6789
```

### Invalid Examples (Will Show Errors):

**Weak Password:**
```
Password: test123
Error: "Password must be at least 12 characters long"
```

**Invalid Username:**
```
Username: 123user
Error: "Username must start with a letter"
```

**Disposable Email:**
```
Email: test@tempmail.com
Error: "Disposable email addresses are not allowed"
```

**Sequential Password:**
```
Password: Abcdef123456!
Error: "Password contains sequential characters"
```

**Underage User:**
```
Birthday: 2015-01-01
Error: "You must be at least 13 years old to register"
```

---

## Implementation Details

### Files Modified:
1. **app/auth/routes.py** - Added `validate_registration_data()` function with all validation logic
2. **templates/auth/register.html** - Updated to show inline errors and preserve user input

### Key Features:
- Comprehensive field validation
- Error dictionary with field-specific messages
- Form data preservation on error
- No route or database changes
- Compatible with existing application structure

---

## Summary

This implementation provides **bank-level security** and **enterprise-grade user experience** for registration validation:

✅ Strict server-side validation
✅ Professional error handling
✅ Input preservation
✅ Inline error messages
✅ Field highlighting
✅ No alerts or popups
✅ Security best practices
✅ User-friendly feedback
