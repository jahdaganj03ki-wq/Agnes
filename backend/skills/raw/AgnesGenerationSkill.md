# Agnes Generation Skill — Image Editing

## Core Principle

For image-to-image editing, the model must receive TWO things:
1. **What to change** (minimal, precise)
2. **What to preserve** (exhaustive, explicit)

## Prompt Structure for Image Editing

### Enhanced Prompt Format

Generate an image editing prompt in this exact format:

```
ORIGINAL IMAGE DESCRIPTION: [Detailed description of the original image: subject, pose, clothing, background, lighting, colors, style]

EDIT INSTRUCTION: Change ONLY: [precise description of what the user wants changed]
PRESERVE ALL OF THE FOLLOWING EXACTLY:
- The person's identity, face, facial features, expression, skin tone
- Hair style, color, and texture
- Body pose, posture, hand position, body proportions
- Background, setting, environment, location
- Lighting direction, intensity, shadows, highlights
- Image composition, framing, camera angle, perspective
- ALL other clothing items NOT mentioned in the edit (shoes, pants, accessories)
- Colors NOT mentioned in the edit
- Image quality, resolution, depth of field

NEGATIVE INSTRUCTION: Do NOT change anything about the person's identity, face, pose, background, or any detail not explicitly mentioned in the EDIT INSTRUCTION.
```

### Examples

**User:** "change color of clothes to black"
**Enhanced Prompt:**
```
ORIGINAL IMAGE DESCRIPTION: A person standing in an indoor room, wearing a red t-shirt and blue jeans, with short brown hair, standing against a white wall with natural window lighting.

EDIT INSTRUCTION: Change ONLY the color of the t-shirt/clothing from its original color to black.
PRESERVE ALL OF THE FOLLOWING EXACTLY:
- The person's identity, face, facial features, expression, skin tone
- Hair style, color, and texture  
- Body pose, posture, hand position, body proportions
- The exact background, room, wall, window lighting
- Lighting direction, intensity, shadows, highlights
- Image composition, framing, camera angle
- ALL other clothing details including pants/jeans and shoes
- All image colors except the shirt color

NEGATIVE INSTRUCTION: Do NOT change the background, the person's face, hair, pose, or any detail except the clothing color.
```

**User:** "make background tropical beach"
**Enhanced Prompt:**
```
ORIGINAL IMAGE DESCRIPTION: A person standing in front of a white wall indoors, wearing casual clothes, with natural lighting from the left.

EDIT INSTRUCTION: Change ONLY the background from the indoor wall to a tropical beach scene with ocean, sand, and palm trees.
PRESERVE ALL OF THE FOLLOWING EXACTLY:
- The person's identity, face, facial features, expression, skin tone
- Hair style, color, and texture
- Body pose, posture, hand position, body proportions
- ALL clothing items, colors, and details exactly as they are
- Lighting on the subject's face and body
- Image quality and resolution

NEGATIVE INSTRUCTION: Do NOT change the person, their clothes, their pose, or any detail about the subject. Only the background changes.
```

## Best Practices for Preservation

1. **Be exhaustive**: List every aspect to preserve. The model needs explicitly told what NOT to change.
2. **Be negative**: Add explicit "do not change" instructions.
3. **Describe the original**: Help the model understand what currently exists so it can preserve it.
4. **Change scope**: Always start with "Change ONLY:" followed by a precise description of exactly one thing.
5. **Reinforce**: End with what must NOT change.
