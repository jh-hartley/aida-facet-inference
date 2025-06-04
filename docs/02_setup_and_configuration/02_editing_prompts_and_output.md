# Editing Prompts and Model Output: A Guide for Non-Coders

This guide explains how to adjust the main aspects of the system that affect the model's output. The changes are isolated to plain text changes for quick and easy testing.

---

## 1. Adjusting the Cosine Similarity Threshold

**What is it?**
- This controls how similar other products must be to the one being analysed, when the system looks for "similar products" to help make predictions. Lower values mean only very similar products are included.

**How to change it:**
1. Open the file: `src/config.py`
2. Find the line:
   ```python
   SIMILARITY_DEFAULT_DISTANCE: float = float(os.getenv("SIMILARITY_DEFAULT_DISTANCE", "0.6"))
   ```
3. Change the number (e.g., `0.6`) to your desired threshold. Lower = stricter, higher = more inclusive (max is 2.0, min is 0.0).
4. Alternatively, set the environment variable `SIMILARITY_DEFAULT_DISTANCE` in your deployment environment.

---

## 2. Changing the Number of Similar Products Returned

**What is it?**
- This controls how many similar products are shown to the model as examples.

**How to change it:**
1. Open the file: `src/config.py`
2. Find the line:
   ```python
   SIMILARITY_DEFAULT_LIMIT: int = int(os.getenv("SIMILARITY_DEFAULT_LIMIT", "10"))
   ```
3. Change the number (e.g., `10`) to your desired number of similar products.
4. Alternatively, set the environment variable `SIMILARITY_DEFAULT_LIMIT`.

---

## 3. Editing Confidence Levels

**What are they?**
- The model assigns a confidence score (0–1) to each prediction. These scores are grouped into bands (e.g., "Very High", "Moderate") with descriptions and examples.

**How to change them:**
1. Open the file: `src/core/domain/confidence_levels.py`
2. Find the section starting with `CONFIDENCE_BANDS = [`
3. Each band looks like this:
   ```python
   ConfidenceBand(
       name="VERY_HIGH",
       label="Very High",
       min_score=0.95,
       max_score=0.9799,
       range_str="95-98%",
       description="...",
       example="...",
   ),
   ```
4. Edit the `min_score`, `max_score`, `label`, `description`, or `example` as needed.
5. Save the file. (You may need a developer to re-deploy the system for changes to take effect.)

---

## 4. Editing the Wording of the System and Human Prompts

**What are they?**
- The system prompt gives the model its instructions and rules.
- The human prompt gives the model the specific product and attribute to predict.
- Example answers for confidence levels are also provided.

**How to change them:**
1. Open the following files in a text editor:
   - System prompt: `src/core/prompts/templates/system_prompt.txt`
   - Human prompt: `src/core/prompts/templates/human_prompt.txt`
   - Confidence examples: `src/core/prompts/templates/confidence_examples.txt`
2. Edit the text as you wish. You can change instructions, add clarifications, or update examples.
3. Save the files. (No code changes are needed—these are loaded automatically.)

---

## 5. Tips and Best Practices
- **Back up files** before making changes.
- **Test your changes** by running the system and checking the output.
- If you are unsure, ask a developer to review your edits before deploying to production.

---

**Still have questions?**
- Ask your technical team for help, or check the `README.md` and other documentation in the `docs/` folder for more details.
