# Model Validation Prompts - Test Suite

**Date:** 2026-04-11
**Model:** qwen3.5-9b (local via LM Studio on M2)
**Goal:** Verify responses come from local model, not remote API

## Standard Prompts

### 1. Basic Arithmetic & Logic
> "What is 17 × 24 + 36 - 15 ÷ 3? Show your step-by-step calculation."

**Expected behavior:** Model should perform accurate math with reasoning steps.

---

### 2. Code Generation
> "Write a Python function that calculates the factorial of a number using recursion. Include type hints and docstring."

**Expected behavior:** Returns valid, well-documented Python code.

---

### 3. Creative Writing
> "Describe a quiet morning in an old library from the perspective of a dusty encyclopedia."

**Expected behavior:** Creative, first-person narrative with atmosphere.

---

### 4. Logical Reasoning (Chain-of-Thought)
> "If all Bloops are Razzies and no Razzies are Wazzles, can any Wazzle be a Bloop? Explain your reasoning step by step."

**Expected behavior:** Clear logical deduction with explanation.

---

### 5. Code Explanation & Debugging
> "What does this Python code do? What would happen if we changed line 4 to 'i = i * 2' instead?"

```python
for i in range(1, 6):
    print(i ** 3)
```

**Expected behavior:** Explains the pattern (cubic numbers), predicts output change.

---

## Execution Method

Run each prompt via LM Studio local connection:
- Endpoint: `http://localhost:1234/v1/chat/completions`
- Model: `qwen/qwen3.5-9b`
- Temperature: 0.7 (creative tasks), 0.2 (reasoning tasks)

## Validation Criteria

✅ **PASS:** Response is coherent, model-specific style detected  
❌ **FAIL:** Generic/no response or obvious API signature  

## Expected Model Signatures (Qwen3.5-9b)

- Thoughtful step-by-step reasoning
- Code formatting with comments/docstrings
- Creative writing with personality
- Clear logical explanations
- Natural conversational tone when appropriate
