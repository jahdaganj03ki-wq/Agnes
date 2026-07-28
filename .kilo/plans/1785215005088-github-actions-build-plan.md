# Plan: WinUI 3 → Avalonia UI + Cross-Platform Build

## 1. Ziel

WinUI 3 durch **Avalonia UI 12** ersetzen, sodass das gesamte Projekt auf Linux (`ubuntu-latest`) ohne Windows-CI gebaut, getestet und als portable Windows-App (`dotnet publish -r win-x64`) ausgeliefert werden kann.

## 2. Was bleibt unverändert

| Komponente | Grund |
|---|---|
| **AgnesWindows.Core** (net9.0) | Reine Models + Service-Interfaces, keine UI-Abhängigkeit |
| **AgnesWindows.Tests** | 24 Tests testen Core + Infrastructure, keine UI |
| **ChatViewModel** | Pure CommunityToolkit.Mvvm, kein WinUI-Code |
| **MainViewModel** | Pure CommunityToolkit.Mvvm, kein WinUI-Code |
| **SkillLoadViewModel** | Pure CommunityToolkit.Mvvm, kein WinUI-Code |
| **SettingsViewModel** | Pure CommunityToolkit.Mvvm, kein WinUI-Code |
| **HistoryViewModel** | Pure CommunityToolkit.Mvvm, kein WinUI-Code |
| **SettingsService, HistoryService** | Reine Datei-I/O, kein WinUI-Code |
| **AuthService, LocalStorageService** | Reflection + `OperatingSystem.IsWindows()` — bereits cross-platform |
| **appsettings.json** | Reine JSON-Konfiguration |
| **Assets/icon.ico** | Wird von Avalonia unterstützt (Window.Icon) |

**Nur 1 ViewModel wird geändert**: `ImageEditViewModel.cs` (WinRT-Referenzen in `BitmapImage`, `FileOpenPicker`, `WindowNative`).

## 3. Wesentliche Design-Entscheidungen

### 3.1 Image.Source in Avalonia
**Problem**: WinUI `Image.Source` akzeptiert URL-Strings. Avalonia `Image.Source` benötigt `IImage`.

**Lösung**: Code-Behind in `ImageBlock.xaml.cs` lädt Bilder asynchron (HTTP/Datei) in `Avalonia.Media.Imaging.Bitmap`. Zusätzlich ein `StringToImageConverter` für Dateipfade.

### 3.2 DataContext je Page
**Problem**: WinUI setzt DataContext pro Page über `Frame.Navigated`-Handler. Mit TabControl werden Pages statisch instantiiert.

**Lösung**: Jede Page ruft `Ioc.Default.GetRequiredService<ViewModelType>()` im Konstruktor auf und setzt `DataContext`. Das ist der einfachste Migrationspfad.

### 3.3 Navigation
WinUI: `NavigationView` (Pane) → `Frame.Navigate(Page)`  
Avalonia: `TabControl` → `TabItem` (statisch, keine Navigation-API nötig)

Die 3 Seiten (EditImage, History, Settings) werden als TabItems in MainWindow.axaml eingebettet.

### 3.4 Toshiba C660 (Intel HD Graphics 3000)
Avalonia + SkiaSharp nutzt standardmäßig DirectX 11. Intel HD 3000 unterstützt nur DirectX 10.1.  
**Lösung**: In `Program.cs` Software-Rendering als Fallback:
```csharp
.With(new Win32PlatformOptions { RenderingMode = [Win32RenderingMode.Software] })
```

Oder bei Bedarf automatisch:
```csharp
.With(new Win32PlatformOptions { AllowEglInitialization = false })
```

## 4. Projektstruktur nach Migration

```
AgnesWindows.sln (5 Projekte, baut auf Linux + Windows)
├── src/AgnesWindows.Core/                net9.0 → UNCHANGED
├── src/AgnesWindows.Infrastructure/      net9.0 → System.Drawing → SkiaSharp
├── src/AgnesWindows.UI/                  net9.0 → REWRITTEN (Avalonia)
├── src/AgnesWindows.App/                 net9.0 → REWRITTEN (Avalonia entry)
└── tests/AgnesWindows.Tests/             net9.0 → UNCHANGED
```

### Warum kein Windows-TFM mehr?
Alle Projekte targetieren `net9.0` (nicht `net9.0-windows10.0.19041.0`).  
Avalonia Apps laufen auf Windows, Linux und macOS mit `net9.0`.  
`dotnet publish -r win-x64` cross-compiliert auf Linux zu einer Windows-Exe.

## 5. Datei-für-Datei Änderungen

### 5.1 Lösche diese Dateien

| Datei | Grund |
|---|---|
| `src/AgnesWindows.App/AgnesWindows.App.wapproj` | MSIX-Packaging entfällt (portable Zip statt MSIX) |
| `Directory.Build.props` → `TargetPlatformMinVersion` | Nicht nötig bei net9.0 |
| `src/AgnesWindows.UI/Views/*.xaml` (6 Dateien) | Werden durch .axaml ersetzt |
| `src/AgnesWindows.UI/Views/*.xaml.cs` (6 Dateien) | Werden durch .axaml.cs ersetzt |
| `src/AgnesWindows.App/Pages/*.xaml` (3 Dateien) | Werden durch .axaml ersetzt |
| `src/AgnesWindows.App/Pages/*.xaml.cs` (3 Dateien) | Werden durch .axaml.cs ersetzt |
| `src/AgnesWindows.App/App.xaml` + `.xaml.cs` | Werden durch App.axaml + .axaml.cs ersetzt |
| `src/AgnesWindows.App/MainWindow.xaml` + `.xaml.cs` | Werden durch MainWindow.axaml + .axaml.cs ersetzt |
| `src/AgnesWindows.UI/Converters/EditImageStateToVisibilityConverter.cs` | Wird neu geschrieben (Avalonia IValueConverter) |
| `src/AgnesWindows.App/Converters/CommonConverters.cs` | Wird neu geschrieben (Avalonia IValueConverter) |
| `.github/workflows/ci.yml` | Wird neu geschrieben (ubuntu-latest, kein pwsh) |
| `.github/workflows/release.yml` | Wird neu geschrieben (ubuntu-latest, kein MSIX) |

### 5.2 Erstelle neue Dateien

| Datei | Beschreibung |
|---|---|
| `src/AgnesWindows.App/Program.cs` | Avalonia-Einstiegspunkt: `BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)` |
| `src/AgnesWindows.App/App.axaml` | Application + Resources + Styles (FluentTheme) |
| `src/AgnesWindows.App/App.axaml.cs` | DI-Container Initialisierung + `OnFrameworkInitializationCompleted` |
| `src/AgnesWindows.App/MainWindow.axaml` | TabControl + Input Bar |
| `src/AgnesWindows.App/MainWindow.axaml.cs` | File-Picker, Event-Handler |
| `src/AgnesWindows.App/Pages/EditImagePage.axaml` | UserControl statt Page |
| `src/AgnesWindows.App/Pages/EditImagePage.axaml.cs` | DataContext = `Ioc.Default.GetRequiredService<ChatViewModel>()` |
| `src/AgnesWindows.App/Pages/HistoryPage.axaml` | UserControl |
| `src/AgnesWindows.App/Pages/HistoryPage.axaml.cs` | DataContext = `Ioc.Default.GetRequiredService<HistoryViewModel>()` |
| `src/AgnesWindows.App/Pages/SettingsPage.axaml` | UserControl |
| `src/AgnesWindows.App/Pages/SettingsPage.axaml.cs` | DataContext = `Ioc.Default.GetRequiredService<SettingsViewModel>()` |
| `src/AgnesWindows.UI/Views/ChatView.axaml` | Avalonia XAML |
| `src/AgnesWindows.UI/Views/ChatView.axaml.cs` | `OnRetryClick` → `Command="..."` |
| `src/AgnesWindows.UI/Views/ActionToolbar.axaml` | Emoji-Buttons + ToolTip |
| `src/AgnesWindows.UI/Views/ActionToolbar.axaml.cs` | Nur InitializeComponent |
| `src/AgnesWindows.UI/Views/ImageBlock.axaml` | Async-Image-Loading |
| `src/AgnesWindows.UI/Views/ImageBlock.axaml.cs` | Async HTTPS/file-loader für Image.Source |
| `src/AgnesWindows.UI/Views/PromptEnhancementPanel.axaml` | TextBlock-Bindings |
| `src/AgnesWindows.UI/Views/PromptEnhancementPanel.axaml.cs` | Nur InitializeComponent |
| `src/AgnesWindows.UI/Views/AspectRatioSelector.axaml` | ComboBox + SelectedItem Binding |
| `src/AgnesWindows.UI/Views/AspectRatioSelector.axaml.cs` | SelectedRatio DP-artige Property |
| `src/AgnesWindows.UI/Views/SkillLoadCard.axaml` | TextBlock statt FontIcon |
| `src/AgnesWindows.UI/Views/SkillLoadCard.axaml.cs` | Nur InitializeComponent |
| `src/AgnesWindows.UI/Converters/AvaloniaConverters.cs` | Alle 7 Converter + UrlToImageConverter |

### 5.3 Ändere bestehende Dateien

| Datei | Änderung |
|---|---|
| `Directory.Build.props` | `TargetPlatformMinVersion` entfernen; TFM bleibt `net9.0` |
| `src/AgnesWindows.UI/AgnesWindows.UI.csproj` | TFM: `net9.0-windows10.0.19041.0` → `net9.0`; WinAppSDK → Avalonia 12.1.0 |
| `src/AgnesWindows.App/AgnesWindows.App.csproj` | TFM: `net9.0-windows10.0.19041.0` → `net9.0`; `UseWinUI`/`EnableMsixTooling` entfernt; WinAppSDK + CsWin32 → Avalonia 12.1.0 |
| `src/AgnesWindows.Infrastructure/AgnesWindows.Infrastructure.csproj` | `System.Drawing.Common` → `SkiaSharp 4.150.1`; `Microsoft.Windows.CsWin32` entfernen (nur in AuthService via Reflection) |
| `src/AgnesWindows.UI/ViewModels/ImageEditViewModel.cs` | `BitmapImage` → `Avalonia.Media.Imaging.Bitmap`; `FileOpenPicker` + WinRT → `StorageProvider.OpenFilePickerAsync()` |
| `src/AgnesWindows.Infrastructure/ImageUploadService.cs` | `System.Drawing.Image` → `SkiaSharp.SKBitmap`; `[SupportedOSPlatform("windows")]` entfernen |
| `AgnesWindows.UI.csproj` + `AgnesWindows.App.csproj` | `Avalonia.Diagnostics` (nur Debug) für DevTools-Overlay (F12) hinzufügen |

## 6. Detaillierte Code-Spezifikationen

### 6.1 Program.cs (NEU)

```csharp
using Avalonia;
using Avalonia.Win32;

namespace AgnesWindows.App;

public static class Program
{
    public static void Main(string[] args)
        => BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .With(new Win32PlatformOptions
            {
                RenderingMode = [Win32RenderingMode.Software] // Toshiba C660: Intel HD 3000 (DX10.1)
            })
            .LogToTrace();
}
```

### 6.2 App.axaml

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:conv="using:AgnesWindows.UI.Converters"
             x:Class="AgnesWindows.App.App">
    <Application.Styles>
        <FluentTheme />
    </Application.Styles>
    <Application.Resources>
        <!-- Dark Theme Colors (unverändert aus WinUI App.xaml) -->
        <SolidColorBrush x:Key="AppBackgroundBrush" Color="#000000"/>
        <SolidColorBrush x:Key="CardBackgroundBrush" Color="#1C1C1E"/>
        <SolidColorBrush x:Key="AccentCyanBrush" Color="#00BCD4"/>
        <SolidColorBrush x:Key="AccentBlueBrush" Color="#2962FF"/>
        <SolidColorBrush x:Key="TextPrimaryBrush" Color="#FFFFFF"/>
        <SolidColorBrush x:Key="TextSecondaryBrush" Color="#8E8E93"/>
        <SolidColorBrush x:Key="ErrorBrush" Color="#FF3B30"/>
        <SolidColorBrush x:Key="SuccessBrush" Color="#34C759"/>
        <FontFamily x:Key="DefaultFontFamily">Segoe UI</FontFamily>

        <!-- Converters (müssen in Application.Resources deklariert sein) -->
        <conv:CountToVisibilityConverter x:Key="CountToVisibilityConverter"/>
        <conv:BoolToStringConverter x:Key="BoolToStringConverter"/>
        <conv:EnumToBoolConverter x:Key="EnumToBoolConverter"/>
        <conv:EditImageStateToVisibilityConverter x:Key="StateToVisibilityConverter"/>
        <conv:EditImageStateToEnabledConverter x:Key="StateToEnabledConverter"/>
    </Application.Resources>
</Application>
```

### 6.3 App.axaml.cs

```csharp
using CommunityToolkit.Mvvm.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace AgnesWindows.App;

public partial class App : Application
{
    public static IServiceProvider Services { get; private set; } = null!;
    public static IConfiguration Configuration { get; private set; } = null!;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
        InitializeServices();
    }

    private void InitializeServices()
    {
        var serviceCollection = new ServiceCollection();

        var configBuilder = new ConfigurationBuilder()
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
            .AddEnvironmentVariables();
        Configuration = configBuilder.Build();
        serviceCollection.AddSingleton(Configuration);
        serviceCollection.AddSingleton<IConfiguration>(Configuration);

        serviceCollection.AddLogging(builder =>
        {
            builder.AddConsole();
            // AddDebug() entfernt — benötigt Microsoft.Extensions.Logging.Debug (Windows-only)
        });

        serviceCollection.AddSingleton<IStorageService, LocalStorageService>();
        serviceCollection.AddSingleton<IAuthService, AuthService>();
        serviceCollection.AddSingleton<IImageUploadService, ImageUploadService>();
        serviceCollection.AddSingleton<ISkillExtractor, SkillExtractor>();

        serviceCollection.AddSingleton<IImageGenerationBackend>(sp =>
        {
            var config = sp.GetRequiredService<IConfiguration>();
            var loggerFactory = sp.GetRequiredService<ILoggerFactory>();
            var apiKey = config["Agnes:ApiKey"]
                         ?? Environment.GetEnvironmentVariable("AGNES_API_KEY");
            return string.IsNullOrWhiteSpace(apiKey)
                ? new MockBackend(loggerFactory.CreateLogger<MockBackend>())
                : new AgnesPublicApiClient(config, loggerFactory.CreateLogger<AgnesPublicApiClient>());
        });

        serviceCollection.AddTransient<MainViewModel>();
        serviceCollection.AddTransient<ChatViewModel>();
        serviceCollection.AddTransient<ImageEditViewModel>();
        serviceCollection.AddTransient<SkillLoadViewModel>();
        serviceCollection.AddSingleton<SettingsService>();
        serviceCollection.AddSingleton<HistoryService>();

        Services = serviceCollection.BuildServiceProvider();
        Ioc.Default.ConfigureServices(Services);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = Services.GetRequiredService<MainWindow>();
        }
        base.OnFrameworkInitializationCompleted();
    }
}
```

### 6.4 MainWindow.axaml

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="using:AgnesWindows.UI.ViewModels"
        xmlns:views="using:AgnesWindows.UI.Views"
        xmlns:pages="using:AgnesWindows.App.Pages"
        x:Class="AgnesWindows.App.MainWindow"
        Title="Agnes Windows"
        MinWidth="1000" MinHeight="700"
        Width="1280" Height="850"
        Icon="Assets/icon.ico">
    <Window.DataContext>
        <vm:MainViewModel/>
    </Window.DataContext>

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Tab Navigation (ersetzt NavigationView) -->
        <TabControl Grid.Row="0" Background="{StaticResource CardBackgroundBrush}">
            <TabItem Header="Edit Image">
                <pages:EditImagePage/>
            </TabItem>
            <TabItem Header="History">
                <pages:HistoryPage/>
            </TabItem>
            <TabItem Header="Settings">
                <pages:SettingsPage/>
            </TabItem>
        </TabControl>

        <!-- Input Bar (wie WinUI) -->
        <Border Grid.Row="2" Background="{StaticResource CardBackgroundBrush}" Padding="16"
                IsVisible="{Binding CurrentState, Converter={StaticResource StateToVisibilityConverter}, ConverterParameter=Idle}">
            <Grid ColumnDefinitions="*,Auto,Auto" ColumnSpacing="12">
                <TextBox Grid.Column="0" 
                         PlaceholderText="Describe your edit..."
                         Text="{Binding Chat.UserPrompt, Mode=TwoWay}"
                         KeyDown="OnPromptKeyDown"/>
                <Button Grid.Column="1" Content="📎" Width="48" Height="48"
                        Background="{StaticResource AccentBlueBrush}"
                        Click="OnAttachImageClick"/>
                <Button Grid.Column="2" Content="Send" Width="96" Height="48"
                        Background="{StaticResource AccentCyanBrush}"
                        IsEnabled="{Binding CurrentState, Converter={StaticResource StateToEnabledConverter}}"
                        Click="OnSendClick"/>
            </Grid>
        </Border>
    </Grid>
</Window>
```

**Wichtig**: DataContext für Chat wird in den Pages (EditImagePage, HistoryPage) gesetzt, nicht mehr per ContentFrame_Navigated.

### 6.5 MainWindow.axaml.cs

```csharp
using CommunityToolkit.Mvvm.DependencyInjection;

namespace AgnesWindows.App;

public partial class MainWindow : Window
{
    private readonly ChatViewModel _chatViewModel;

    public MainWindow()
    {
        InitializeComponent();
        _chatViewModel = Ioc.Default.GetRequiredService<ChatViewModel>();
    }

    private void OnPromptKeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter && e.KeyModifiers != KeyModifiers.Shift)
        {
            e.Handled = true;
            OnSendClick(sender, null!);
        }
    }

    private async void OnAttachImageClick(object? sender, RoutedEventArgs e)
    {
        var files = await StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            AllowMultiple = false,
            FileTypeFilter = new[]
            {
                new FilePickerFileType("Images") { Patterns = new[] { "*.jpg", "*.jpeg", "*.png", "*.bmp" } }
            }
        });

        if (files.Count == 1)
        {
            _chatViewModel.InputImagePath = files[0].Path.LocalPath;
        }
    }

    private void OnSendClick(object? sender, RoutedEventArgs e)
    {
        if (_chatViewModel.SubmitCommand.CanExecute(null))
        {
            _chatViewModel.SubmitCommand.Execute(null);
        }
    }
}
```

### 6.6 ImageEditViewModel.cs (1 ViewModel-Änderung)

```csharp
using Avalonia.Media.Imaging;
using Avalonia.Platform.Storage;

public partial class ImageEditViewModel : ObservableObject
{
    private readonly ChatViewModel _chatViewModel;

    [ObservableProperty]
    private Bitmap? _sourceImage;  // War: BitmapImage

    [ObservableProperty]
    private bool _hasSourceImage;

    public ImageEditViewModel(ChatViewModel chatViewModel)
    {
        _chatViewModel = chatViewModel;
    }

    [RelayCommand]
    private async Task PickImageAsync()
    {
        var desktop = Application.Current?.ApplicationLifetime as IClassicDesktopStyleApplicationLifetime;
        if (desktop?.MainWindow is not Window window) return;

        var files = await window.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            AllowMultiple = false,
            FileTypeFilter = new[]
            {
                new FilePickerFileType("Images") { Patterns = new[] { "*.jpg", "*.jpeg", "*.png", "*.bmp" } }
            }
        });

        if (files.Count == 1)
        {
            var path = files[0].Path.LocalPath;
            using var stream = File.OpenRead(path);
            SourceImage = new Bitmap(stream);
            HasSourceImage = true;
            _chatViewModel.InputImagePath = path;
        }
    }

    [RelayCommand]
    private void ClearImage()
    {
        SourceImage = null;
        HasSourceImage = false;
        _chatViewModel.InputImagePath = null;
    }
}
```

### 6.7 Converter: EditImageStateToVisibilityConverter.cs (Avalonia-Version)

```csharp
using System.Globalization;
using Avalonia.Data.Converters;

namespace AgnesWindows.UI.Converters;

public class CountToVisibilityConverter : IValueConverter
{
    // Gibt bool zurück (nicht Visibility) — bindet an IsVisible
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is int count)
        {
            var inverse = parameter?.ToString()?.Equals("inverse", StringComparison.OrdinalIgnoreCase) ?? false;
            var visible = count > 0;
            return inverse ? !visible : visible;
        }
        return false;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}

public class BoolToStringConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool b && parameter is string param)
        {
            var parts = param.Split('|');
            return b ? (parts.Length > 0 ? parts[0] : "Yes") : (parts.Length > 1 ? parts[1] : "No");
        }
        return string.Empty;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}

public class EnumToBoolConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is Enum enumValue && parameter is string enumString)
        {
            return enumValue.ToString().Equals(enumString, StringComparison.OrdinalIgnoreCase);
        }
        return false;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool b && b && parameter is string enumString)
        {
            if (Enum.TryParse(typeof(EditImageState), enumString, true, out var enumValue))
                return enumValue;
            // Falls AppTheme aus CommonConverters
            if (Enum.TryParse(typeof(AppTheme), enumString, true, out var themeValue))
                return themeValue;
        }
        return Avalonia.Data.BindingOperations.DoNothing;
    }
}

public class EditImageStateToVisibilityConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        // Gibt bool zurück: true = sichtbar, false = collapsed
        if (value is EditImageState state && parameter is string param)
        {
            var targetStates = param.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
            return targetStates.Contains(state.ToString());
        }
        return false;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}

public class EditImageStateToEnabledConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is EditImageState state)
        {
            return state is EditImageState.Idle or EditImageState.PromptEnhanced or EditImageState.ResultReady or EditImageState.Error;
        }
        return false;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}

public class BoolToVisibilityConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool boolValue)
        {
            var invert = parameter?.ToString()?.Equals("invert", StringComparison.OrdinalIgnoreCase) == true;
            return boolValue ^ invert;
        }
        return false;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        // Für TwoWay-Bindungen nicht benötigt
        return value is bool b ? b : false;
    }
}

public class InverseBoolToVisibilityConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is bool boolValue) return !boolValue;
        return true;
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

### 6.8 UrlToImageConverter (NEU, in derselben Datei)

```csharp
public class UrlToImageConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is string path && !string.IsNullOrEmpty(path) && File.Exists(path))
        {
            return new Bitmap(path);
        }
        return null; // Wird durch async-Loader in ImageBlock.xaml.cs ergänzt
    }

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

### 6.9 ImageBlock.xaml + Code-Behind

```xml
<UserControl x:Class="AgnesWindows.UI.Views.ImageBlock"
             xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             MinHeight="300">
    <Border Background="#1A1A1C" CornerRadius="8" Padding="16">
        <StackPanel Spacing="12">
            <TextBlock Text="Generated Image" Foreground="{StaticResource TextPrimaryBrush}"
                       FontSize="14" FontWeight="SemiBold"/>
            <Border CornerRadius="8" Height="300" Background="#2C2C2E">
                <Image x:Name="ResultImage" Stretch="Uniform" />
            </Border>
            <StackPanel Orientation="Horizontal" Spacing="8" HorizontalAlignment="Center">
                <Button Content="👍" Width="40" Height="40"/>
                <Button Content="👎" Width="40" Height="40"/>
                <Button Content="📋" Width="40" Height="40"/>
                <Button Content="↗️" Width="40" Height="40"/>
            </StackPanel>
        </StackPanel>
    </Border>
</UserControl>
```

```csharp
public partial class ImageBlock : UserControl
{
    public ImageBlock()
    {
        InitializeComponent();
    }

    protected override void OnDataContextChanged(EventArgs e)
    {
        if (DataContext is ChatViewModel vm)
        {
            vm.PropertyChanged += (_, args) =>
            {
                if (args.PropertyName == nameof(ChatViewModel.LastResult))
                    LoadImageAsync(vm.LastResult?.ImageUrl);
            };
            LoadImageAsync(vm.LastResult?.ImageUrl);
        }
    }

    private async void LoadImageAsync(string? url)
    {
        if (string.IsNullOrEmpty(url)) return;
        try
        {
            if (url.StartsWith("http://") || url.StartsWith("https://"))
            {
                using var client = new HttpClient();
                var bytes = await client.GetByteArrayAsync(url);
                using var stream = new MemoryStream(bytes);
                ResultImage.Source = new Bitmap(stream);
            }
            else if (File.Exists(url))
            {
                ResultImage.Source = new Bitmap(url);
            }
        }
        catch { /* ignore image load errors */ }
    }
}
```

### 6.10 ImageUploadService.cs (SkiaSharp)

```csharp
using SkiaSharp;

public class ImageUploadService : IImageUploadService
{
    // [SupportedOSPlatform("windows")] ENTFERNT — läuft jetzt cross-platform

    public Task<UploadResult> TryConvertToBase64Async(string filePath, CancellationToken ct = default)
    {
        try
        {
            var fileInfo = new FileInfo(filePath);
            if (fileInfo.Length > 4 * 1024 * 1024)
                return Task.FromResult(new UploadResult { Succeeded = false, Reason = "File too large" });

            using var input = File.OpenRead(filePath);
            using var original = SKBitmap.Decode(input);
            using var image = SKImage.FromBitmap(original);
            using var data = image.Encode(SKEncodedImageFormat.Png, 80);
            var base64 = Convert.ToBase64String(data.ToArray());

            return Task.FromResult(new UploadResult { Succeeded = true, Base64Data = base64, MimeType = "image/png" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to convert image to Base64");
            return Task.FromResult(new UploadResult { Succeeded = false, Reason = ex.Message });
        }
    }

    public async Task<string?> UploadToTempUrlAsync(string filePath, CancellationToken ct = default)
    {
        await Task.CompletedTask;
        return null;
    }
}
```

### 6.11 Pages — DataContext-Muster

Jede Page setzt ihren DataContext im Konstruktor via `Ioc.Default`:

```csharp
// EditImagePage.xaml.cs
public partial class EditImagePage : UserControl
{
    public EditImagePage()
    {
        DataContext = Ioc.Default.GetRequiredService<ChatViewModel>();
        InitializeComponent();
    }
}

// HistoryPage.xaml.cs
public partial class HistoryPage : UserControl
{
    public HistoryPage()
    {
        DataContext = Ioc.Default.GetRequiredService<HistoryViewModel>();
        InitializeComponent();
    }
}

// SettingsPage.xaml.cs
public partial class SettingsPage : UserControl
{
    public SettingsPage()
    {
        DataContext = Ioc.Default.GetRequiredService<SettingsViewModel>();
        InitializeComponent();
    }

    private void OnSaveClick(object? sender, RoutedEventArgs e)
    {
        var tooltip = new ToolTip { Content = "Saved!", Placement = PlacementMode.Bottom };
        ToolTip.SetTip((Control)sender!, tooltip);
        tooltip.IsOpen = true;

        var timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1.5) };
        timer.Tick += (_, _) => { tooltip.IsOpen = false; timer.Stop(); };
        timer.Start();
    }
}
```

### 6.12 AspectRatioSelector — SelectedRatio als AvaloniaProperty

```csharp
public partial class AspectRatioSelector : UserControl
{
    public static readonly StyledProperty<string> SelectedRatioProperty =
        AvaloniaProperty.Register<AspectRatioSelector, string>(nameof(SelectedRatio), "1:1");

    public string SelectedRatio
    {
        get => GetValue(SelectedRatioProperty);
        set => SetValue(SelectedRatioProperty, value);
    }

    public AspectRatioSelector()
    {
        InitializeComponent();
    }
}
```

```xml
<UserControl x:Class="AgnesWindows.UI.Views.AspectRatioSelector"
             xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <ComboBox SelectedItem="{Binding SelectedRatio, RelativeSource={RelativeSource AncestorType=UserControl}}"
              Width="200" Background="#2C2C2E" Foreground="{StaticResource TextPrimaryBrush}" CornerRadius="6">
        <ComboBoxItem Content="1:1 (Square)" Tag="1:1"/>
        <ComboBoxItem Content="16:9 (Landscape)" Tag="16:9"/>
        ...
    </ComboBox>
</UserControl>
```

**Hinweis**: Bindung im MainWindow oder EditImagePage:
```xml
<views:AspectRatioSelector SelectedRatio="{Binding SelectedAspectRatio, Mode=TwoWay}"/>
```

## 7. Pre-Existing Bugs (im Rahmen der Migration fixen)

| Bug | Datei | Zeile | Fix |
|---|---|---|---|
| `sed 's/^#+//'` → `sed 's/^#*//'` | `scripts/extract-skills.sh` | 33 | GNU sed: `\+` für one-or-more. Fix: `sed 's/^#*//'` |
| `Converter={...}, ConverterParameter=Idle, Converter={...}` | `src/AgnesWindows.App/MainWindow.xaml` | 56 | Doppelter Converter. Fix auf einen Converter reduzieren: `Converter={StaticResource StateToVisibilityConverter}, ConverterParameter=Idle` |
| `SelectedRatio="{Binding ...}"` nicht definiert | `src/AgnesWindows.App/Pages/EditImagePage.xaml` | 25 | `AspectRatioSelector` hat kein `SelectedRatio`. Fix: siehe 6.12 |

## 8. CsWin32 und Infrastructure — Entfernen von Microsoft.Windows.CsWin32

`Microsoft.Windows.CsWin32` wird in `AgnesWindows.Infrastructure.csproj` referenziert, aber nur `AuthService` verwendet CsWin32-Generated-Code via `Windows.Win32` Namespace.

**Fix**: `Microsoft.Windows.CsWin32` aus `AgnesWindows.Infrastructure.csproj` entfernen. `AuthService` verwendet bereits `OperatingSystem.IsWindows()` und Reflection für `PasswordVault`. Der `using Windows.Win32` in AuthService muss in `MainWindow.xaml.cs` entfernt werden.

Prüfe ob `Windows.Win32` in AuthService tatsächlich importiert wird:
- Ja, `AuthService.cs` verwendet `Windows.Win32` für PInvoke. 
  → Entweder durch `[DllImport("advapi32.dll")]` ersetzen (cross-platform) oder den Code hinter `OperatingSystem.IsWindows()` guarden.
  → Da AuthService bereits fallback auf env var hat, kann der PInvoke-Teil hinter den Guard.

## 9. Logdatei-Funktion (File Logger)

### 9.1 Anforderung
- Logdatei im selben Ordner wie die ausführbare Datei (`AgnesWindows.exe`)
- Erfasst alle `ILogger<T>`-Ausgaben (Error, Warning, Information, Debug)
- Einfaches Textformat für Error-Analyse
- Log-Rotation (Größen-basiert) gegen übermäßigen Speicherverbrauch
- Keine neuen externen NuGet-Abhängigkeiten (eigener `ILoggerProvider`)

### 9.2 Datei-Struktur

```
src/AgnesWindows.App/Services/Logging/
├── FileLoggerProvider.cs    # ILoggerProvider + FileLogger (innere Klasse)
```

### 9.3 Log-Pfad

```csharp
var logPath = Path.Combine(AppContext.BaseDirectory, "AgnesWindows.log");
```

- **Development**: `src/AgnesWindows.App/bin/Release/net9.0/AgnesWindows.log`
- **Published (win-x64)**: `publish/win-x64/AgnesWindows.log`
- **Toshiba C660**: neben `AgnesWindows.exe`

### 9.4 Log-Format

```
[2026-07-28 08:15:30.123] [INF] [AgnesWindows.Infrastructure.AuthService] Initializing AuthService
[2026-07-28 08:15:31.789] [ERR] [AgnesWindows.Infrastructure.AgnesPublicApiClient] HTTP 500 from API
[2026-07-28 08:15:31.789] [!] Exception: System.Net.Http.HttpRequestException: Response status code does not indicate success: 500
```

**Format** je Zeile: `[Timestamp] [Level] [Category] Message`  
**Exception**: separate Zeile mit Stack.

### 9.5 Log-Rotation

| Parameter | Wert |
|---|---|
| Max Dateigröße | 10 MB |
| Max aufbewahrte Dateien | 3 |
| Rotationsmuster | `AgnesWindows.log` → `.1` → `.2` → `.3` (älteste gelöscht) |
| Rotation | Bei jedem Write nach Dateigröße geprüft |

### 9.6 Implementierung: `FileLoggerProvider.cs`

```csharp
using System.Text;
using Microsoft.Extensions.Logging;

namespace AgnesWindows.App.Services.Logging;

public class FileLoggerProvider : ILoggerProvider
{
    private readonly string _filePath;
    private readonly LogLevel _minLevel;
    private readonly long _maxFileSizeBytes;
    private readonly int _maxRetainedFiles;
    private readonly object _lock = new();
    private StreamWriter? _writer;

    public FileLoggerProvider(
        string filePath,
        LogLevel minLevel = LogLevel.Information,
        long maxFileSizeBytes = 10L * 1024 * 1024,
        int maxRetainedFiles = 3)
    {
        _filePath = filePath;
        _minLevel = minLevel;
        _maxFileSizeBytes = maxFileSizeBytes;
        _maxRetainedFiles = maxRetainedFiles;
    }

    public ILogger CreateLogger(string categoryName)
        => new FileLogger(this, categoryName, _minLevel);

    internal void Write(LogLevel logLevel, string category, string message, Exception? exception)
    {
        lock (_lock)
        {
            EnsureWriter();
            var ts = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
            var level = logLevel switch
            {
                LogLevel.Trace => "TRC",
                LogLevel.Debug => "DBG",
                LogLevel.Information => "INF",
                LogLevel.Warning => "WRN",
                LogLevel.Error => "ERR",
                LogLevel.Critical => "CRI",
                _ => "???"
            };
            _writer?.WriteLine($"[{ts}] [{level}] [{category}] {message}");
            if (exception != null)
                _writer?.WriteLine($"[{ts}] [!] {exception}");
            _writer?.Flush();
            CheckRotation();
        }
    }

    private void EnsureWriter()
    {
        if (_writer != null) return;
        var dir = Path.GetDirectoryName(_filePath);
        if (!string.IsNullOrEmpty(dir))
            Directory.CreateDirectory(dir);
        _writer = new StreamWriter(_filePath, append: true, Encoding.UTF8);
    }

    private void CheckRotation()
    {
        if (_writer == null) return;
        _writer.Flush();
        var fi = new FileInfo(_filePath);
        if (!fi.Exists || fi.Length < _maxFileSizeBytes) return;

        _writer.Dispose();
        _writer = null;

        for (int i = _maxRetainedFiles; i >= 0; i--)
        {
            var src = i == 0 ? _filePath : $"{_filePath}.{i}";
            var dst = $"{_filePath}.{i + 1}";
            if (File.Exists(dst)) File.Delete(dst);
            if (File.Exists(src)) File.Move(src, dst);
        }
    }

    public void Dispose()
    {
        lock (_lock)
        {
            _writer?.Dispose();
            _writer = null;
        }
    }
}

internal class FileLogger : ILogger
{
    private readonly FileLoggerProvider _provider;
    private readonly string _category;
    private readonly LogLevel _minLevel;

    public FileLogger(FileLoggerProvider provider, string category, LogLevel minLevel)
    {
        _provider = provider;
        _category = category;
        _minLevel = minLevel;
    }

    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

    public bool IsEnabled(LogLevel logLevel)
        => logLevel >= _minLevel && logLevel != LogLevel.None;

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
    {
        if (!IsEnabled(logLevel)) return;
        _provider.Write(logLevel, _category, formatter(state, exception), exception);
    }
}
```

### 9.7 Integration in `App.axaml.cs`

```csharp
using AgnesWindows.App.Services.Logging;

// In InitializeServices(), im AddLogging-Builder:

serviceCollection.AddLogging(builder =>
{
    builder.AddConsole();

    // File logger im Programmverzeichnis
    var logPath = Path.Combine(AppContext.BaseDirectory, "AgnesWindows.log");
    builder.AddProvider(new FileLoggerProvider(logPath, LogLevel.Information));
});
```

**Wichtig**: `builder.AddDebug()` entfernen (siehe Abschnitt CsWin32) — benötigt Windows-only `Microsoft.Extensions.Logging.Debug`-Paket. Console + File reichen aus.

### 9.8 Auswirkung auf bestehenden Code

| Komponente | Änderung |
|---|---|
| `App.axaml.cs` | `FileLoggerProvider` in DI registrieren |
| Alle `ILogger<T>` Services | **Keine** — injecten bereits `ILogger<T>`, logs gehen automatisch an alle registrierten Provider |
| Tests | **Keine** — `ILogger<T>` kann in Tests via `NullLogger<T>.Instance` oder `Mock<ILogger<T>>` ersetzt werden (besteht bereits so) |

## 10. CI Workflow

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: 9.0.x }
      - uses: actions/cache@v4
        with:
          path: ~/.nuget/packages
          key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj', '**/*.props') }}

      - run: bash scripts/extract-skills.sh
      - run: dotnet restore AgnesWindows.sln
      - run: dotnet build AgnesWindows.sln -c Release --no-restore

      - name: Validate build
        run: |
          for dll in AgnesWindows.Core.dll AgnesWindows.Infrastructure.dll AgnesWindows.UI.dll AgnesWindows.dll AgnesWindows.Tests.dll; do
            find . -name "$dll" | grep -q . || { echo "Missing: $dll"; exit 1; }
          done

      - run: dotnet test tests/AgnesWindows.Tests/AgnesWindows.Tests.csproj -c Release --no-build --collect "XPlat Code Coverage"
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-results
          path: tests/AgnesWindows.Tests/TestResults/**/coverage.cobertura.xml

      - name: Set version
        run: |
          tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0-ci")
          echo "VERSION=${tag#v}" >> $GITHUB_ENV

      - name: Publish win-x64 (cross-compile)
        run: |
          dotnet publish src/AgnesWindows.App/AgnesWindows.App.csproj \
            -c Release -r win-x64 --self-contained true \
            /p:Version=$VERSION -o publish/win-x64

      - name: Validate publish
        run: |
          [ -f publish/win-x64/AgnesWindows.exe ] || { echo "No exe"; exit 1; }
          size=$(stat -c%s publish/win-x64/AgnesWindows.exe)
          [ "$size" -ge 1000000 ] || { echo "Too small"; exit 1; }

      - uses: actions/upload-artifact@v4
        with:
          name: AgnesWindows-win-x64-${{ env.VERSION }}
          path: publish/win-x64/
```

## 11. Release Workflow

```yaml
name: Release
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # ... gleiche Steps wie CI (restore, build, test, publish) ...
      - uses: softprops/action-gh-release@v2
        with:
          files: publish/win-x64/**/*
          generate_release_notes: true
```

## 12. Implementierungs-Reihenfolge

1. **`Directory.Build.props`** — `TargetPlatformMinVersion` entfernen
2. **`.csproj` Änderungen** — UI, App, Infrastructure NuGet-Pakete + TFM
3. **`AgnesWindows.Infrastructure.csproj`** — `System.Drawing.Common` raus, `SkiaSharp` rein; `Microsoft.Windows.CsWin32` raus
4. **`ImageUploadService.cs`** — SkiaSharp-Migration
5. **`scripts/extract-skills.sh`** — `sed` Bugfix (Zeile 33)
6. **Converter-Dateien** — Beide Dateien neu schreiben (Avalonia IValueConverter + `bool` statt `Visibility`)
7. **`App.axaml` + `App.axaml.cs` + `Program.cs`** — Avalonia-Einstiegspunkt
8. **`MainWindow.axaml` + `.axaml.cs`** — TabControl + Input Bar + StorageProvider
9. **6 Views** (ChatView, ActionToolbar, ImageBlock, PromptEnhancementPanel, AspectRatioSelector, SkillLoadCard) — .axaml + .axaml.cs
10. **3 Pages** (EditImagePage, HistoryPage, SettingsPage) — .axaml + .axaml.cs
11. **`ImageEditViewModel.cs`** — StorageProvider + Bitmap
12. **Solution** — `*.wapproj` aus Solution entfernen (wird nicht referenziert, nur in `.sln` wenn doch hinzugefügt — prüfen)
13. **`.wapproj` + `*.pfx`** löschen
14. **`AuthService.cs`** — `using Windows.Win32` durch `[DllImport]` ersetzen oder guarden
15. **FileLoggerProvider** — `src/AgnesWindows.App/Services/Logging/FileLoggerProvider.cs` erstellen
16. **App.axaml.cs** — `FileLoggerProvider` in AddLogging-Builder registrieren
17. **Workflows** — `ci.yml` + `release.yml` neu schreiben
18. **Build-Test** — `dotnet build` + `dotnet test` + `dotnet publish -r win-x64`

## 13. Validierung

1. `dotnet build AgnesWindows.sln` → 5/5 Projekte, 0 Fehler, 0 Warnings
2. `dotnet test` → 24/24 Tests
3. `dotnet publish -r win-x64 --self-contained true src/AgnesWindows.App/AgnesWindows.App.csproj` → `AgnesWindows.exe` ≥ 1MB
4. CI-Workflow auf `ubuntu-latest` → grün
5. Release-Workflow mit Tag → GitHub Release + portables Zip
6. FileLogger erzeugt `AgnesWindows.log` im App-Verzeichnis beim ersten Log-Eintrag
7. Log-Rotation: `AgnesWindows.log` > 10 MB → wird zu `.1` verschoben, neuer File angelegt
8. `ILogger<T>`-Aufrufe in AuthService, ImageUploadService, etc. erscheinen in der Logdatei
