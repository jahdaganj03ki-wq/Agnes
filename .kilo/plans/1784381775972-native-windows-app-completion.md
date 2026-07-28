# Native Windows App Completion Plan — AgnesWindows

## Current State (✅ Done)
- Core, Infrastructure, Tests: **Build 0 warnings, 0 errors**
- CI/CD: **Passing** (Run 29671483660)
- All compiler warnings fixed: CS1998, CS8424, CS0414
- 3/3 Tests passing

## Gaps in UI/App Layer

| Area | Status | Issues |
|------|--------|--------|
| **DI Container** | ❌ Missing | No `Microsoft.Extensions.DependencyInjection` setup; ViewModels instantiated in XAML without constructor DI |
| **ViewModel Wiring** | ❌ Broken | `ChatView.xaml` creates `<vm:ChatViewModel/>` in XAML but ctor requires `IImageGenerationBackend` + `IStorageService`; `MainWindow.xaml.cs` also creates instance — conflict |
| **App.xaml Resources** | ⚠️ Partial | Converters not registered; theme brushes exist but not all referenced |
| **Navigation/Page Structure** | ❌ Not Implemented | `NavigationView` has 3 items (Edit/History/Settings) but only static `ChatView` shown — no `Frame` navigation |
| **Aspect Ratio Selector** | ⚠️ Exists, Unused | `AspectRatioSelector.xaml` exists but not integrated into ChatView |
| **Settings Page** | ❌ Missing | No UI, no persistence (`appsettings.json`) |
| **History Page** | ❌ Missing | No UI, no local history storage |
| **Skill Files** | ⚠️ Unknown | `AgnesPublicApiClient` expects `AgnesWindows.Skills/extracted/*.extracted.md` — need to verify |
| **DI Registration** | ❌ Missing | No `Microsoft.Extensions.DependencyInjection` + `CommunityToolkit.Mvvm.DependencyInjection` setup |

---

## Implementation Plan

### Phase 1: DI Container & Service Registration (Foundation)

**Files to Create/Modify:**
- `src/AgnesWindows.App/App.xaml.cs` — Add DI setup using `Microsoft.Extensions.DependencyInjection` + `CommunityToolkit.Mvvm.DependencyInjection`
- `src/AgnesWindows.App/Services/ServiceCollectionExtensions.cs` — Extension method to register all services
- `src/AgnesWindows.App/ViewModels/ViewModelLocator.cs` — Optional: static accessor for ViewModels

**Registrations:**
| Interface | Implementation | Lifetime |
|-----------|----------------|----------|
| `IImageGenerationBackend` | `AgnesPublicApiClient` (prod) / `MockBackend` (dev) | Singleton |
| `IStorageService` | `LocalStorageService` | Singleton |
| `IAuthService` | `AuthService` | Singleton |
| `IImageUploadService` | `ImageUploadService` | Singleton |
| `ISkillExtractor` | `SkillExtractor` | Singleton |
| `ChatViewModel` | `ChatViewModel` | Transient |
| `MainViewModel` | `MainViewModel` | Transient |
| `ImageEditViewModel` | `ImageEditViewModel` | Transient |
| `SkillLoadViewModel` | `SkillLoadViewModel` | Transient |

**Key Decision:** Use `MockBackend` when no API key configured, `AgnesPublicApiClient` when `AGNES_API_KEY` or `Agnes:ApiKey` in config exists.

---

### Phase 2: ViewModel Wiring & XAML Fixes

**Files to Modify:**
- `src/AgnesWindows.App/MainWindow.xaml.cs` — Remove manual `ChatViewModel` creation; resolve via DI
- `src/AgnesWindows.UI/Views/ChatView.xaml` — Remove `<vm:ChatViewModel/>`; set `DataContext` from parent/locator
- `src/AgnesWindows.App/App.xaml` — Add `EditImageStateToVisibilityConverter` to resources
- `src/AgnesWindows.App/App.xaml.cs` — Initialize DI on startup; set `Ioc.Default.ConfigureServices()`

**Pattern:** Use `Ioc.Default.GetRequiredService<T>()` in code-behind or `DataContext="{Binding ChatViewModel, Source={StaticResource Locator}}"` if using Locator.

---

### Phase 3: Navigation & Page Structure

**Files to Create/Modify:**
- `src/AgnesWindows.App/Pages/EditImagePage.xaml` — Extract `ChatView` content into a page
- `src/AgnesWindows.App/Pages/HistoryPage.xaml` — New page
- `src/AgnesWindows.App/Pages/SettingsPage.xaml` — New page
- `src/AgnesWindows.App/MainWindow.xaml` — Replace static content with `Frame` + NavigationView binding

**Navigation Logic:**
- `NavigationView.SelectionChanged` → `Frame.Navigate(typeof(EditImagePage))` etc.
- Pass `ChatViewModel` (or parent ViewModel) to pages via `Frame.Navigate(typeof(Page), viewModel)`

---

### Phase 4: Aspect Ratio Selector Integration

**Files to Modify:**
- `src/AgnesWindows.UI/Views/AspectRatioSelector.xaml` — Verify bindings work
- `src/AgnesWindows.UI/Views/ChatView.xaml` — Add `<views:AspectRatioSelector SelectedRatio="{Binding SelectedAspectRatio, Mode=TwoWay}"/>` in input bar area
- `ChatViewModel` — Already has `SelectedAspectRatio` property ✅

---

### Phase 5: Settings & Persistence

**Files to Create/Modify:**
- `src/AgnesWindows.App/Services/SettingsService.cs` — Wrapper around `IStorageService` for app settings
- `src/AgnesWindows.App/Pages/SettingsPage.xaml` — UI for: API Key input, Theme (Light/Dark/System), Default Aspect Ratio, Mock/Prod Backend toggle
- `src/AgnesWindows.App/ViewModels/SettingsViewModel.cs` — Bindable settings VM
- `src/AgnesWindows.Infrastructure/LocalStorageService.cs` — Add `SaveSettingAsync` / `GetSettingAsync` methods

**Settings to Persist:**
| Key | Type | Default |
|-----|------|---------|
| `Agnes:ApiKey` | string | "" |
| `App:Theme` | enum (Light/Dark/System) | System |
| `App:DefaultAspectRatio` | string | "1:1" |
| `App:UseMockBackend` | bool | true (dev) |

---

### Phase 6: History Page

**Files to Create:**
- `src/AgnesWindows.Core/Models/HistoryEntry.cs` — Model for history item
- `src/AgnesWindows.Infrastructure/HistoryService.cs` — Implements `IHistoryService` using `LocalStorageService` (JSON file)
- `src/AgnesWindows.App/Pages/HistoryPage.xaml` — ListView of history entries with image preview
- `src/AgnesWindows.App/ViewModels/HistoryViewModel.cs` — Load/save/delete history

---

### Phase 7: Skill Files Verification

**Action:**
```powershell
ls src/AgnesWindows.Skills/extracted/
```
**Expected files (from `AgnesPublicApiClient`):**
- `AgnesGenerationSkill.extracted.md` → skillName: `aigc-model-guide`
- `AgnesCliSkill.extracted.md` → skillName: `image-prompt-craft`
- `VisionCraftPromptGuide.extracted.md` → skillName: `image-generation`

**If missing:** Run `pwsh scripts/extract-skills.ps1` (or `./scripts/extract-skills.sh`) to generate from raw markdown.

---

### Phase 8: Theme & Polish

**Files to Modify:**
- `src/AgnesWindows.App/App.xaml` — Add missing converters, ensure all referenced brushes exist
- `src/AgnesWindows.App/MainWindow.xaml` — Add `TitleBar` customization (extend content into title bar)
- `src/AgnesWindows.UI/Views/*` — Consistent spacing, accessibility (`AutomationProperties`), high-contrast support

---

## Validation Checklist

| Check | How to Verify |
|-------|---------------|
| DI Container resolves all ViewModels | `dotnet run` — no `MissingMethodException` or `ActivationException` |
| ChatView loads with real backend | Send prompt → MockBackend returns placeholder image |
| Navigation works | Click History/Settings → page switches |
| Aspect ratio selector updates model | Change ratio → `SelectedAspectRatio` updates in ChatViewModel |
| Settings persist | Change API key → restart app → key retained |
| History saves | Generate image → History page shows entry |
| Build passes | `dotnet build AgnesWindows.sln -c Release` — 0 errors, 0 warnings |
| CI passes | Push to `main` → GitHub Actions green |

---

## File Inventory (New Files to Create)

```
src/AgnesWindows.App/
├── Services/
│   ├── ServiceCollectionExtensions.cs
│   ├── SettingsService.cs
│   └── HistoryService.cs
├── Pages/
│   ├── EditImagePage.xaml/.cs
│   ├── HistoryPage.xaml/.cs
│   └── SettingsPage.xaml/.cs
├── ViewModels/
│   ├── SettingsViewModel.cs
│   └── HistoryViewModel.cs
├── Converters/ (if any new)
├── App.xaml (update resources)
├── App.xaml.cs (DI init)
└── MainWindow.xaml (Frame navigation)
```

---

## Open Questions for User

1. **Backend Selection**: Default to `MockBackend` (offline) or `AgnesPublicApiClient` (requires API key)? → *Recommendation: MockBackend default, user can switch in Settings*

2. **History Storage Format**: JSON file in `LocalAppData` or SQLite? → *Recommendation: JSON for simplicity, migrate to SQLite if >1000 entries*

3. **Skill Files**: Should I run the extraction script now or assume user has raw markdown in `src/AgnesWindows.Skills/raw/`?

4. **Theme Default**: System / Light / Dark? → *Recommendation: System*

5. **Minimum Windows Version**: Currently `10.0.17763.0` (RS5). Target `10.0.19041.0` (20H1) for better WinUI 3 support? → *Recommendation: Keep 17763 for broad compat, but 19041 enables newer APIs*

---

## Next Step

Please confirm or adjust the open questions above. Once resolved, I'll write the final implementation plan to `.kilo/plans/` and call `plan_exit`.