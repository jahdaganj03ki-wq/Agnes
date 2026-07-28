# Agnes CLI Skill

## CLI Best Practices

- Check API connectivity before generating
- Validate prompt length and content
- Handle rate limits with exponential backoff
- Log all requests for debugging

## Error Handling

- 400: Invalid request parameters
- 401: Authentication failed
- 429: Rate limit exceeded
- 500: Server error, retry with backoff
