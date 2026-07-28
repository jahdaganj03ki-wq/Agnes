# Agnes CLI Skill — Image Editing Pipeline

## Prompt Enhancement Instructions

When enhancing a user's edit prompt, follow this strict workflow:

### Step 1: Understand the edit
Identify EXACTLY what the user wants to change. Extract the specific element (clothing color, background, style, etc.)

### Step 2: Generate the enhanced prompt
Use the template from AgnesGenerationSkill:
1. Describe the original image in detail
2. State "Change ONLY: [the specific edit]"
3. List all elements to PRESERVE exhaustively
4. Add NEGATIVE INSTRUCTION

### Step 3: Quality checks
- Does the enhanced prompt clearly distinguish what changes vs. what stays?
- Does it list at minimum: face, pose, background, clothing-not-mentioned, lighting?
- Does it include a negative instruction?

## Pipeline Requirements

1. The enhanced prompt must be at least 3-4 sentences long
2. It must explicitly mention both "Change ONLY" and "PRESERVE"
3. It must be specific enough to guide image-to-image generation precisely
4. Vague prompts like "make it better" or "improve this" must be expanded with specific instructions
