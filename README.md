

````md
## Agent-to-Agent Usage

This translation agent is designed for use by other agents in multi-agent workflows. It provides language translation as a service with per-character billing.

### API Endpoint
- **URL**: `https://your-agent-endpoint/translate`
- **Method**: `POST`
- **Content-Type**: `application/json`

### Input Format
```json
{
  "text": "Hello world!",
  "source_language": "en",
  "target_language": "es"
}
```

### Output Format
```json
{
  "original_text": "Hello world!",
  "translated_text": "¡Hola mundo!",
  "character_count": 12,
  "billing_amount": 0.00024
}
```

### Example Request
```python
import requests

url = "https://your-agent-endpoint/translate"
input_data = {
    "text": "Hello world!",
    "source_language": "en",
    "target_language": "es"
}
response = requests.post(url, json=input_data)
print(response.json())
```

### Example Response
```json
{
  "original_text": "Hello world!",
  "translated_text": "¡Hola mundo!",
  "character_count": 12,
  "billing_amount": 0.00024
}
```
Original: Hello world!
Translated: ¡Hola mundo!
Characters: 12, Cost: $0.00024
```


