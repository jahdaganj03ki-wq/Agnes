# Agnes Windows

A native Windows desktop application that replicates the Agnes AI Android "Edit Image" workflow.

## Features

- Real skill loading from bundled Agnes AI agent skills
- Real prompt enhancement via `agnes-2.0-flash`
- Image generation via `agnes-image-2.1-flash`
- Dark theme UI matching the Android app
- Aspect ratio selection (1:1, 16:9, 9:16, 4:3, 3:2, 21:9)
- Retry with cache on failure
- MSIX installer + portable ZIP

## Building

```bash
dotnet restore AgnesWindows.sln
dotnet build AgnesWindows.sln --configuration Release
```

## Testing

```bash
dotnet test tests/AgnesWindows.Tests/AgnesWindows.Tests.csproj
```

## Setup

1. Get an Agnes AI API key from https://platform.agnes-ai.com/
2. Configure the key in the app settings or via `AGNES_API_KEY` environment variable
3. Run the app

## License

MIT
