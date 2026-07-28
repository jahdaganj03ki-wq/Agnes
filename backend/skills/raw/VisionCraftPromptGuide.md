# VisionCraft Prompt Guide — Image-to-Image Preservation

## The Preservation Principle

When editing an existing image, the model MUST understand:
- The original image is perfect except for ONE specific change
- Everything else must remain IDENTICAL

## Prompt Engineering for Image Models

### Critical Rules

1. **Describe the original first**: Before saying what to change, describe what exists
2. **"Change ONLY" pattern**: Always start the edit instruction with these exact words
3. **"PRESERVE" section**: List every element that must not change
4. **"NEGATIVE INSTRUCTION"**: Add explicit "do not change" directives

### Enhanced Prompt Template

```
ORIGINAL: [subject] in [setting], wearing [clothing], [lighting], [composition]

EDIT: Change ONLY [specific element(s)].
PRESERVE:
- Face and identity
- Pose and body position
- Background and setting
- Lighting and shadows
- All other clothing and accessories
- Image composition and style

DO NOT CHANGE: [anything not in the edit instruction]
```

### Why Current Prompts Fail

Bad prompt: `"A person with black clothes"` → model generates a NEW person with black clothes

Good prompt: 
```
"ORIGINAL IMAGE shows a person in a room wearing a red shirt and jeans. 
EDIT INSTRUCTION: Change ONLY the shirt color from red to black.
PRESERVE: face, hair, pose, background, jeans, shoes, lighting, composition exactly.
DO NOT CHANGE anything except the shirt color."
```

→ Model understands it should keep EVERYTHING and only recolor the shirt

## Preserving Composition

- Always describe: background details, object positions, framing
- Always specify: what NOT to generate (no new objects, no new people)
- Use preservation ratio: 80% of the prompt should describe what to KEEP, 20% what to CHANGE
