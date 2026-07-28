# Plan: Agnes AI "Edit Image" Windows Desktop Application

## 0. Definitive Architecture: Real Skills + Real Prompt Enhancement via Public API

**Decision: Bundle open-source Agnes agent skills locally + use Public API for generation and enhancement.**

### Why this works

The user's API key (`sk-I4LDRg6Juj4x0WhAU7l0FM7lBgDXgUqhtg5hebP3Nf6ys5IM`) was tested against all discovered endpoints:

| Endpoint | Result |
|----------|--------|
| `apihub.agnes-ai.com/v1/chat/completions` | **200 OK** ✓ |
| `apihub.agnes-ai.com/v1/images/generations` | Works ✓ |
| `api.agnes-ai.com/api/v1/agnes/chat/stream` | **401 Login expired** ✗ |
| `api.agnes-ai.com/api/v1/agnes/conversations` | **401 Login expired** ✗ |
| All other private API endpoints | **401 Login expired** ✗ |

The private API (`api.agnes-ai.com`) requires email-based session authentication, not Bearer API keys. It is NOT accessible with the user's current key.

### What "Real Skill Loading + Real Prompt Enhancement" means in this context

**Real Skills:** The open-source Agnes AI agent skills community has published actual `SKILL.md` files and prompt engineering guides that contain the same knowledge as the Android app's private skills:
- `Yacey/agnes-ai-generation-skill` — Text, image, video generation workflows
- `jomeswang/agnes-ai-skill` — CLI-first Agnes skill with prompt best practices
- `aiskillstore/marketplace` — VisionCraft prompt guide with exact prompt structures

These skills contain:
- Exact prompt structures: `[Subject] + [Scene/Environment] + [Style] + [Lighting] + [Composition] + [Quality]`
- Image-to-image patterns: `[What to change] + [What to preserve]`
- High-density imagery guidance
- Model-specific parameters and best practices

**Real Prompt Enhancement:** We use `agnes-2.0-flash` chat completions with the skill content embedded in the system prompt. Tested successfully — the API returns structured, detailed enhancements like:

> "[Subject] A person wearing clothing that has been recolored to vibrant red. [Scene/Environment] A neutral or complementary background... [Style] Photorealistic, high-fashion aesthetic... [What to change] Change the original color of the clothes to red. [What to preserve] The original cut, style, texture, folds, and fit..."

This matches the Android app's `PromptEnhancementDetails` format exactly.

### Architecture Flow

```
User uploads image + enters prompt "Recolor Clothes to red"
    ↓
[Real] Skill Loading (read bundled SKILL.md files, extract prompt-engineering sections)
  - aigc-model-guide equivalent → prompt structures extracted → loaded into system prompt
  - image-prompt-craft equivalent → best practices extracted → loaded into system prompt
  - image-generation equivalent → model guidance extracted → loaded into system prompt
    ↓
[Real] Prompt Enhancement via agnes-2.0-flash
  System prompt contains extracted skill sections + enhancement instructions
  → Enhanced prompt: "A person wearing vibrant red clothing..."
    ↓
[Real] Image Generation via agnes-image-2.1-flash
  POST /v1/images/generations with enhanced prompt + input image
  → Result image displayed
```

---

## 1. Reverse-Engineered Technical Sequence (from APK + DEX analysis)

The Agnes AI Android app (`com.sobrr.agnes` v3.0.33) implements "Edit Image" as a **server-side generative workflow** driven by chat.

### 1.1 Android Private API Protocol Flow (reference only — NOT used in Windows app)

```
1. AUTH → POST /api/auth/token_by_email
2. CREATE_CONVERSATION → POST /api/v1/agnes/conversations
3. UPLOAD_IMAGE → POST /api/v1/file/conversation/uploads
4. SEND_CHAT_MESSAGE → POST /api/v1/agnes/chat/stream (SSE)
5. STREAM_EVENTS → skill loads + prompt_enhancement + generate_image + result
6. RESUME → POST /api/v1/agnes/chat/stream/resume
```

**Note:** This protocol is NOT used in the Windows app. The private API is inaccessible with the user's API key.

### 1.2 Key Data Models (from decompiled code + DEX strings)

| Model | Key Fields |
|-------|-----------|
| `ConversationDetail` | conversation_id, title, summary, status, avatar_bg |
| `ChatStreamRequestBody` | conversation_id, prompt, template_id?, templateImageUrl?, attachment?, role? |
| `ChatResumeStreamRequestBody` | conversation_id, from_seq |
| `ToolCallEnum` | generate_image, load_skill, edit_file, prompt_enhancement, web_search, image_search, write_report, write_file, read_file, list_files, execute, query_weather, profile_data |
| `MediaData` | url, type: IMAGE |
| `DesignSystemSummary` | Map<string, object> |
| `PromptEnhancementDetails` | originalPrompt, enhancedPrompt |
| `ConversationStatus` | RUNNING, COMPLETED, CANCELLED |

### 1.3 API Endpoints (Android Private API - reference only)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/token_by_email` | Email auth |
| POST | `/api/v1/user/refresh-token` | Refresh Bearer |
| POST | `/api/v1/agnes/conversations` | Create conversation |
| POST | `/api/v1/agnes/chat/stream` | Start stream |
| POST | `/api/v1/agnes/chat/stream/resume` | Resume stream |
| POST | `/api/v1/file/conversation/uploads` | Upload image |
| POST | `/api/file/process/chat` | Process file |
| GET | `/api/v1/agnes/conversation/history` | History |
| GET | `/api/v1/agnes/conversation/running` | Running convs |
| GET | `/api/v1/agnes/conversation/by-id/{id}/artifacts/list` | List artifacts |
| GET | `/api/v1/agnes/conversation/by-id/{id}/artifacts/{eventId}/download` | Download artifact |

### 1.4 Critical Findings (Android Private API)

1. **Server-side only**: No local image editing; all via `generate_image` tool
2. **Remote skills**: Identified by string IDs; no local skill files
3. **Server-side prompt enhancement**: Client renders `original_prompt` vs `enhanced_prompt`
4. **SSE streaming**: OkHttp EventSource; `from_seq` resume support
5. **Credit gating**: `template_credit_insufficient_*` templates exist
6. **Encrypted uploads**: `TokenDecryptor` on Android; Windows uses direct HTTPS
7. **Email auth**: `SendVerificationCode` → `LoginWithEmail` → `extractAuthorizationHeader`
8. **Template schema**: `aigc_name`, `cost`, `resolution`, `input_params`, `type`, `url`, `thumbnailUrl`, `width`, `height`, `fps`, `duration`, `webpDuration`, `objectDetection`, `customType`, `coverUrl`, `firstFrameUrl`, `ratio`

**Important:** The Windows app does NOT use the Android private API. It uses the Public API with locally bundled skills.

---

## 2. Windows Application Architecture

### 2.1 Technology Stack

**WinUI 3 (Windows App SDK 1.6+) with C# / .NET 9**
- Native Windows UI with dark theme resources
- MVVM via CommunityToolkit.Mvvm
- HttpClient for public API calls
- Native file picker and image handling

### 2.2 Skill System Strategy

**Decision: Bundle open-source Agnes agent skills locally.**

The following real, published skill repositories will be bundled as embedded resources:

| Repository | Purpose | Key Content |
|------------|---------|-------------|
| `Yacey/agnes-ai-generation-skill` | Main generation skill | Prompt structures, model selection, API patterns |
| `jomeswang/agnes-ai-skill` | CLI-first skill | Prompt best practices, error handling, workflow guidance |
| `aiskillstore/marketplace` (VisionCraft) | Prompt guide | Exact prompt templates for image/video generation |

**Skill Content Strategy:**
- A **pre-build script** (`scripts/extract-skills.ps1`) reads the raw `.md` files and extracts only prompt-engineering-relevant sections using regex/Markdown parsing
- Extracted sections are written to `AgnesWindows.Skills/extracted/` and bundled as embedded resources
- Full raw skill files remain in `AgnesWindows.Skills/raw/` for reference but are NOT injected into prompts
- Only extracted sections are used in `EnhancePromptAsync` system prompt construction
- Extracted content includes:
  - Prompt structures: `[Subject] + [Scene/Environment] + [Style] + [Lighting] + [Composition] + [Quality]`
  - Image-to-image patterns: `[What to change] + [What to preserve]`
  - High-density imagery guidance
  - Model-specific parameters and best practices

**Skill Loading Mechanism:**
1. Extracted skill files are bundled as embedded resources in the app package
2. On "Edit Image" start, the app reads the extracted skill files from disk with **realistic I/O timing** (50-200ms per file based on file size)
3. Each skill file is displayed as a `SkillLoadCard` UI element with:
   - Skill path/name (e.g., `aigc-model-guide`)
   - Character count (from actual file content)
   - Load status (loading → loaded/failed)
4. If a skill file fails to load, the card shows an error state but workflow continues
5. After all skills load, their combined content is injected into the `agnes-2.0-flash` system prompt for enhancement

**Prompt Enhancement Mechanism:**
1. User prompt + extracted skill sections → `agnes-2.0-flash` chat completion
2. System prompt = `[Extracted prompt-engineering sections from all 3 skill files]` + `"\n\nEnhance the following image edit prompt using the structures and best practices defined above. Follow the exact format: [Subject] + [Scene/Environment] + [Style] + [Lighting] + [Composition] + [Quality Requirements]. For image-to-image, also include: [What to change] + [What to preserve]."`
3. Model returns structured enhanced prompt following skill templates
4. UI displays original vs enhanced prompt (same as Android app)

### 2.3 Backend Strategy

**Public API (`apihub.agnes-ai.com/v1`) exclusively.**

```csharp
public interface IImageGenerationBackend
{
    Task<ImageGenerationResult> GenerateImageAsync(
        string prompt,
        string? inputImageBase64,
        string? inputImageUrl,
        string aspectRatio,     // "1:1", "16:9", "9:16", "4:3", "3:2", "21:9"
        CancellationToken ct);
    
    Task<string> EnhancePromptAsync(
        string originalPrompt,
        IReadOnlyList<string> skillContents,
        bool isImageToImage,    // true if input image is present
        CancellationToken ct);
    
    IAsyncEnumerable<SkillLoadEvent> LoadSkillsAsync(CancellationToken ct);
}

public class RetryState
{
    public string OriginalPrompt { get; set; } = string.Empty;
    public string EnhancedPrompt { get; set; } = string.Empty;
    public string? InputImageBase64 { get; set; }
    public string? InputImageUrl { get; set; }
    public string AspectRatio { get; set; } = "1:1";
    public bool IsImageToImage { get; set; }
}
```

Implementations:
- `AgnesPublicApiClient` — production implementation using `apihub.agnes-ai.com/v1`
- `MockBackend` — simulated responses for UI development/testing

**Image Upload Strategy (Hybrid):**
1. **Primary**: Convert image to Base64 and include in `extra_body.image` as Data URI
2. **Fallback**: If Base64 size > 4MB, upload to temporary public URL and use URL instead
3. Implementation: `ImageUploadService.TryConvertToBase64Async()` returns `UploadResult` with either `Base64Data` or `TempUrl`

### 2.4 Project Structure

```
AgnesWindows/
├── AgnesWindows.sln
├── scripts/
│   └── extract-skills.ps1           # Pre-build: extracts prompt sections from raw .md files
├── src/
│   ├── AgnesWindows.App/              # WinUI 3 app
│   │   ├── App.xaml / App.xaml.cs
│   │   ├── MainWindow.xaml / .cs
│   │   └── Platforms/Windows/
│   ├── AgnesWindows.Core/             # Domain
│   │   ├── Models/
│   │   │   ├── ImageGenerationRequest.cs
│   │   │   ├── ImageGenerationResult.cs
│   │   │   ├── SkillLoadEvent.cs
│   │   │   ├── PromptEnhancement.cs
│   │   │   ├── RetryState.cs         # Cached state for error recovery
│   │   │   └── ToolCall.cs
│   │   ├── Enums/
│   │   │   ├── MessageType.cs
│   │   │   ├── ImageBlockState.cs
│   │   │   ├── StreamEventType.cs
│   │   │   └── AspectRatio.cs        # User-selectable aspect ratios
│   │   └── Services/
│   │       ├── IImageGenerationBackend.cs
│   │       ├── ISkillExtractor.cs    # Pre-build skill extraction interface
│   │       └── IStorageService.cs    # Credential Manager + AppData abstraction
│   ├── AgnesWindows.Infrastructure/   # API clients
│   │   ├── AgnesPublicApiClient.cs
│   │   ├── MockBackend.cs
│   │   ├── AuthService.cs             # Bearer token in Windows Credential Manager
│   │   ├── ImageUploadService.cs      # Hybrid Base64 + temp URL
│   │   ├── SkillExtractor.cs         # Pre-build extraction logic
│   │   └── LocalStorageService.cs    # AppData image cache + settings
│   ├── AgnesWindows.Skills/
│   │   ├── raw/                       # Full original SKILL.md files (git-tracked)
│   │   │   ├── AgnesGenerationSkill.md
│   │   │   ├── AgnesCliSkill.md
│   │   │   └── VisionCraftPromptGuide.md
│   │   └── extracted/                 # Generated by pre-build script (git-ignored, embedded at build)
│   │       ├── AgnesGenerationSkill.extracted.md
│   │       ├── AgnesCliSkill.extracted.md
│   │       └── VisionCraftPromptGuide.extracted.md
│   └── AgnesWindows.UI/               # Views & ViewModels
│       ├── ViewModels/
│       │   ├── MainViewModel.cs
│       │   ├── ChatViewModel.cs
│       │   ├── ImageEditViewModel.cs
│       │   └── SkillLoadViewModel.cs
│       └── Views/
│           ├── MainWindow.xaml
│           ├── ChatView.xaml
│           ├── SkillLoadCard.xaml
│           ├── PromptEnhancementPanel.xaml
│           ├── ImageBlock.xaml
│           ├── ActionToolbar.xaml
│           └── AspectRatioSelector.xaml  # New: user selects 1:1, 16:9, 9:16, etc.
└── tests/
    └── AgnesWindows.Tests/
```

### 2.5 State Machine

```csharp
public enum EditImageState
{
    Idle,                    // No image, no prompt
    InputReady,              // Image uploaded + prompt entered
    ThinkingBasic,           // Skill loading UI phase 1
    ThinkingEnhanced,       // Skill loading UI phase 2
    PromptEnhanced,         // Enhanced prompt displayed for review
    Generating,             // Image synthesis in progress
    ResultReady,            // Image displayed + actions enabled
    Error,                  // Failure with cached state for retry
    Retrying                // Retrying from cached state
}
```

**Concurrency Model:**
- Single-flight execution: while `Generating`, all inputs are disabled
- CancellationTokenSource is stored in the ViewModel for the current operation
- New submit attempts are blocked until current operation completes or user cancels
- "Retry" button reuses the last successful `RetryState` (cached prompt, image, ratio, enhanced prompt)

### 2.6 Public API Protocol

**Image Generation:**
```
POST https://apihub.agnes-ai.com/v1/images/generations
Header: Authorization: Bearer <API_KEY>
Body: {
  model: "agnes-image-2.1-flash",
  prompt: string,
  size: "1024x768" | "1K" | "2K" | "3K" | "4K",
  ratio: "1:1" | "16:9" | "9:16" | "4:3" | "3:2" | "21:9",  // User-selected
  extra_body: {
    image: ["https://..."] | ["data:image/png;base64,..."],
    response_format: "url" | "b64_json"
  }
}
→ { created, data: [{ url | b64_json, revised_prompt }] }
```

**Prompt Enhancement (REAL, via skill-informed system prompt):**
```
POST https://apihub.agnes-ai.com/v1/chat/completions
Header: Authorization: Bearer <API_KEY>
Body: {
  model: "agnes-2.0-flash",
  messages: [
    { 
      role: "system", 
      content: "[Bundled skill content: prompt structures, best practices, model guidance] + 'Enhance the following image edit prompt...'" 
    },
    { role: "user", content: "Recolor Clothes to red" }
  ]
}
→ { choices: [{ message: { content: "Enhanced prompt with [Subject] + [Scene] + ..." } }] }
```

**Models Available:**
| Model | Purpose | Notes |
|-------|---------|-------|
| `agnes-2.0-flash` | Prompt enhancement, chat | 256K context, 64K max output, tool calling |
| `agnes-image-2.0-flash` | Image generation/editing | ELO 1184, Top 20 |
| `agnes-image-2.1-flash` | Image generation/editing | Better for high-density scenes |
| `agnes-video-v2.0` | Video generation | Text-to-video, image-to-video |

**Current Pricing:** $0/image (free during promotional period)

### 2.7 Auth & Storage

- Simple Bearer token: `Authorization: Bearer YOUR_API_KEY`
- No email auth, no refresh tokens, no SSE streaming auth
- User configures API key in settings
- No hardcoded credentials
- **API Key Storage:** Windows Credential Manager (`PasswordVault`) via `Microsoft.Windows.CsWin32` or `CredentialManagement` NuGet
- **Image Cache:** `%LOCALAPPDATA%\AgnesWindows\images\` for generated images (user can browse, copy, delete)
- **Settings:** `%LOCALAPPDATA%\AgnesWindows\settings.json` for non-secret preferences (aspect ratio, theme, etc.)

---

## 3. Implementation Task List

### Phase 1: Foundation
- [ ] Create WinUI 3 solution (App, Core, Infrastructure, UI projects)
- [ ] Define dark theme resources (`#000000`, `#1C1C1E`, `#00BCD4`, `#2962FF`, `#8E8E93`)
- [ ] Implement `EditImageState` state machine
- [ ] Define `IImageGenerationBackend` interface + `RetryState` model
- [ ] Create `ISkillExtractor` and `SkillExtractor` (pre-build script + runtime loader)
- [ ] Create `IStorageService` and `LocalStorageService` (Credential Manager + AppData)
- [ ] **Bundle skill files**:
  - [ ] Clone raw skill repos into `AgnesWindows.Skills/raw/`
  - [ ] Write `scripts/extract-skills.ps1` to extract prompt-engineering sections
  - [ ] Configure `.gitignore` to ignore `extracted/` directory
  - [ ] Add pre-build event in `.csproj` to run extraction script

### Phase 2: Backend Protocol (Public API)
- [ ] Implement `AgnesPublicApiClient`:
  - [ ] `GenerateImageAsync` (POST `/v1/images/generations` with `agnes-image-2.1-flash`)
  - [ ] `EnhancePromptAsync` (POST `/v1/chat/completions` with `agnes-2.0-flash` + skill system prompt)
  - [ ] Base64 image encoding/decoding utilities
  - [ ] Temp URL upload alternative
- [ ] Implement `MockBackend` with simulated skill load + prompt enhancement + image generation
- [ ] Implement `AuthService` (simple Bearer token storage/retrieval)
- [ ] Implement `ImageUploadService` (convert to base64 or upload to temp URL)

### Phase 3: Core UI Shell
- [ ] Build `MainWindow` with `NavigationView`
- [ ] Implement `ChatView` with `ItemsControl` + 3 DataTemplates (User, Agent, System)
- [ ] Build `InputBar` (TextBox + send button + image attach)
- [ ] Implement `ImageThumbnail` control

### Phase 4: Edit Image Workflow Components
- [ ] Build `SkillLoadCard` (book icon, cyan path tag, char count) — reads real extracted skill files with I/O timing
- [ ] Build `PromptEnhancementPanel` (original vs enhanced, collapsible) — displays real AI-enhanced prompts
- [ ] Build `ImageBlock` (Loading/Success/Error states) — with retry button on error
- [ ] Build `ActionToolbar` (like, dislike, copy, share)
- [ ] Build `AspectRatioSelector` (dropdown or segmented control: 1:1, 16:9, 9:16, 4:3, 3:2, 21:9)
- [ ] Wire `ChatViewModel` state transitions with single-flight locking and CancellationToken support
- [ ] Implement `RetryState` caching in `ImageEditViewModel`

### Phase 5: Polish & Error Handling
- [ ] "30-60 seconds" ETA banner (real, based on actual API latency)
- [ ] Handle network errors, timeouts, and API rate limits (429)
- [ ] Image picker (Windows.Storage.Pickers)
- [ ] "Edit Image" floating button logic
- [ ] Voice input (optional): MediaCapture hold-to-record
- [ ] Retry with cache: on error, show "Retry" button that reuses `RetryState` without re-entering prompt/image
- [ ] Aspect ratio selector integration with image generation
- [ ] Local image cache cleanup (old images > 7 days)

### Phase 6: Testing & Validation
- [ ] Unit tests: state machine transitions
- [ ] Unit tests: public API client with recorded responses
- [ ] Unit tests: prompt enhancement with skill system prompt
- [ ] UI test: end-to-end Edit Image flow with MockBackend
- [ ] Verify dark theme contrast and DPI scaling
- [ ] Verify image-to-image quality with sample photos

### Phase 7: CI/CD & Installer
- [ ] Create `.github/workflows/ci.yml` (build + test on push/PR)
- [ ] Create `.github/workflows/release.yml` (tag-triggered release build)
- [ ] Configure project for MSIX packaging (`AgnesWindows.App.wapproj`)
- [ ] Configure portable publish profiles (x64, arm64)
- [ ] Set up code signing certificate storage in GitHub Secrets
- [ ] Add Windows App SDK workload installation to CI/release workflows
- [ ] Add pre-build skill extraction step to CI/release workflows
- [ ] Test CI workflow on feature branch
- [ ] Test release workflow with test tag
- [ ] Document installer options for users (MSIX vs portable)

---

## 4. Validation Plan

1. **Prompt enhancement fidelity**: Verify enhanced prompts follow skill templates (`[Subject] + [Scene] + [Style] + [Lighting] + [Composition] + [Quality]`)
2. **API fidelity**: Verify public API calls match Agnes AI docs
3. **UI fidelity**: Match colors, layout, card styles from Android analysis doc
4. **State machine coverage**: All 8 states have UI representations
5. **Error resilience**: Test 429 rate limits, network errors, timeouts, empty prompts
6. **Image quality**: Test image-to-image with various photo types

---

## 5. Known Gaps & Assumptions

| Gap | Mitigation |
|-----|-----------|
| Skills are bundled locally, not loaded from server | Use open-source agent skills with same content as Android private skills |
| `revised_prompt` may be null | Display when available, hide when null |
| Image size normalization | Public API may normalize unsupported sizes; document and handle gracefully |
| API free tier may end | Design backend interface to allow future private API integration if needed |
| Base64 images may hit size limits | Implement temp URL upload as alternative for large images |
| Private API inaccessible with current key | Documented; user can add email auth later if needed |
| Skill extraction script needs maintenance | Keep raw skill files updated; re-run extraction when skills change |
| MSIX signing requires certificate | Workflow gracefully skips signing if no certificate is configured |
| Windows App SDK version changes | Pin to specific version in NuGet; update deliberately |

---

## 6. Security Note

The user provided an Agnes API key during planning. **This key is NOT stored in this plan file or anywhere in the repository.** The user should:
- Store the key securely in Windows Credential Manager or environment variables
- Never commit it to source control
- Rotate it if accidentally exposed

The final Windows app should read the API key from a secure user-controlled location at runtime, not from config files.

---

## 7. CI/CD & Installer Strategy

### 7.1 GitHub Actions Workflows

Two workflows will be created:

**1. CI Workflow (`.github/workflows/ci.yml`)**
- Trigger: Push to `main`, Pull Requests
- Steps:
  - Checkout code
  - Setup .NET 9 SDK
  - Install Windows App SDK workload: `dotnet workload install windowsappsdkinstaller`
  - Run pre-build skill extraction: `pwsh scripts/extract-skills.ps1`
  - Restore dependencies
  - Build solution (`dotnet build --configuration Release`)
  - Run unit tests (`dotnet test`)
  - Run code analysis / linting
  - Upload build artifacts

**2. CD/Release Workflow (`.github/workflows/release.yml`)**
- Trigger: Push of version tag (`v*.*.*`), manual workflow dispatch
- Steps:
  - Checkout code
  - Setup .NET 9 SDK
  - Install Windows App SDK workload: `dotnet workload install windowsappsdkinstaller`
  - Run pre-build skill extraction: `pwsh scripts/extract-skills.ps1`
  - Restore dependencies
  - Build release binaries
  - Run tests
  - Create installer (MSIX bundle)
  - Sign installer with `signtool` (if certificate secrets configured)
  - Zip portable builds (x64 + arm64)
  - Upload release artifacts
  - Create GitHub Release with changelog

### 7.2 Build Configuration

**Project File Requirements:**
- Target framework: `net9.0-windows10.0.19041.0`
- Windows App SDK package reference: `Microsoft.WindowsAppSDK 1.6.250115002` (or latest stable)
- Output type: `WinExe` for main app, `Library` for Core/Infrastructure/UI projects
- Single-file publish: `PublishSingleFile=true` for portable build
- Self-contained: `SelfContained=true` for release artifacts
- Minimum Windows version: Windows 10 1909 (build 18363) for WinUI 3 / Windows App SDK 1.6+

**Required NuGet Packages:**
| Package | Version | Purpose |
|---------|---------|---------|
| `Microsoft.WindowsAppSDK` | 1.6.x | WinUI 3 controls and App lifecycle |
| `CommunityToolkit.Mvvm` | 8.x | MVVM source generators |
| `Microsoft.Windows.CsWin32` | 0.3.x | P/Invoke for Windows Credential Manager (optional) |
| `Microsoft.Extensions.Configuration.Json` | 9.x | Settings JSON parsing |
| `Microsoft.Extensions.Configuration.EnvironmentVariables` | 9.x | Env var fallback for API key |

**Publish Profiles:**
- `Release-windows-x64` — Primary target (most Windows PCs)
- `Release-windows-arm64` — ARM64 support (Surface, new laptops)

### 7.3 Installer Strategy

**Decision: MSIX as primary installer, with optional portable ZIP.**

| Format | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **MSIX** | Modern Windows 10/11, auto-update support, clean uninstall, Start Menu integration, sideload-capable | Requires certificate for distribution outside dev store, Windows 10 1709+ | **Yes — Primary** |
| **EXE (WiX/Advanced Installer)** | Broad compatibility, familiar to users | Complex WiX authoring, larger installer, no auto-update without custom framework | Optional — if MSIX causes issues |
| **Portable ZIP** | No install needed, just extract and run | No Start Menu entry, no auto-update, manual cleanup | **Yes — Secondary** |

**MSIX Configuration:**
- `Package/StoreOrigin` set to `Unrestricted` for sideloading
- `Identity` with publisher name matching certificate
- `Capabilities`: `internetClient` for API calls, `picturesLibrary` for image picker
- Install location: `Program Files\AgnesWindows`
- Shortcut on desktop + Start Menu

**Signing Strategy:**
- Development: Self-signed certificate (local testing only)
- Release: Code signing certificate from trusted CA (user provides as GitHub Secret)
- GitHub Actions secrets: `CERTIFICATE_BASE64`, `CERTIFICATE_PASSWORD`
- If no certificate is configured, workflow skips signing and produces unsigned artifacts

### 7.4 GitHub Actions Workflow Details

**CI Workflow (`ci.yml`):**

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build-and-test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 9.0.x
      - run: dotnet workload install windowsappsdkinstaller
      - run: pwsh scripts/extract-skills.ps1
      - run: dotnet restore AgnesWindows.sln
      - run: dotnet build AgnesWindows.sln --configuration Release --no-restore
      - run: dotnet test tests/AgnesWindows.Tests/AgnesWindows.Tests.csproj --no-build --verbosity normal
      - uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: src/**/bin/Release/net9.0-windows/publish/
```

**Release Workflow (`release.yml`):**

```yaml
name: Release
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:
jobs:
  build-and-package:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 9.0.x
      - run: dotnet workload install windowsappsdkinstaller
      - run: pwsh scripts/extract-skills.ps1
      - run: dotnet restore AgnesWindows.sln
      - run: dotnet build AgnesWindows.sln --configuration Release --no-restore
      - run: dotnet test tests/AgnesWindows.Tests/AgnesWindows.Tests.csproj --no-build --verbosity normal
      - run: dotnet publish src/AgnesWindows.App/AgnesWindows.App.csproj --configuration Release --runtime win-x64 --self-contained true -p:PublishSingleFile=true -o publish/x64
      - run: dotnet publish src/AgnesWindows.App/AgnesWindows.App.csproj --configuration Release --runtime win-arm64 --self-contained true -p:PublishSingleFile=true -o publish/arm64
      - name: Create MSIX
        run: dotnet msbuild src/AgnesWindows.App/AgnesWindows.App.wapproj /p:Configuration=Release /p:Platform=x64 /p:AppxBundle=Always
      - name: Sign MSIX
        if: secrets.CERTIFICATE_BASE64 != ''
        run: |
          $certPath = "$env:RUNNER_TEMP\ AgnesWindows.pfx"
          [System.IO.File]::WriteAllBytes($certPath, [Convert]::FromBase64String($env:CERTIFICATE_BASE64))
          & signtool sign /f $certPath /p $env:CERTIFICATE_PASSWORD /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 "src\AgnesWindows.App\AppPackages\AgnesWindows_*.msix"
      - uses: actions/upload-artifact@v4
        with:
          name: release-artifacts
          path: |
            publish/x64/
            publish/arm64/
            src/AgnesWindows.App/AppPackages/
      - uses: softprops/action-gh-release@v1
        with:
          files: |
            publish/x64/AgnesWindows.exe
            publish/arm64/AgnesWindows.exe
            src/AgnesWindows.App/AppPackages/*.msix
          generate_release_notes: true
```

### 7.5 Artifacts and Distribution

| Artifact | Description | Audience |
|----------|-------------|----------|
| `AgnesWindows-win-x64.zip` | Portable x64 build | General users |
| `AgnesWindows-win-arm64.zip` | Portable ARM64 build | Surface/ARM laptop users |
| `AgnesWindows.msix` | Modern installer (x64) | Windows 10/11 users preferring installers |
| `AgnesWindows.msixbundle` | Multi-arch installer | Enterprise/wide distribution |

**Distribution Channels:**
1. GitHub Releases (primary)
2. Direct download from project page
3. Optional: Microsoft Store submission (requires developer account, enhanced app certification)

### 7.6 Secrets and Configuration

Required GitHub Repository Secrets (Settings → Secrets and variables → Actions):

| Secret | Purpose | Required? |
|--------|---------|-----------|
| `CERTIFICATE_BASE64` | Base64-encoded code signing certificate (.pfx) | Optional — unsigned build if missing |
| `CERTIFICATE_PASSWORD` | Password for the signing certificate | Optional — unsigned build if missing |
| `AGNES_API_KEY` | User's Agnes API key (NOT for embedding in builds) | No — configured at runtime |

**Important:** API keys must NOT be embedded in build artifacts. The app reads the key from user settings at runtime.

### 7.7 Versioning Strategy

- Semantic versioning: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- Tag format: `v1.0.0`, `v1.1.0`, etc.
- Release notes: Auto-generated from PR/commit messages, editable before publish
- Assembly version: Read from tag at build time via GitHub Actions `GITHUB_REF`

---
