

````md
## Sample Usage

Below is a simple example showing how to call this translation agent
from Python and how to calculate the billed character count:

```python
from translator import translate_text
from pricing import calculate_billing

# Text to translate
text = "Hello world!"

# Perform translation
translated = translate_text(text, "EN", "ES")

# Calculate billing
billing = calculate_billing(text)

print("Original:", text)
print("Translated:", translated)
print(
    f"Characters: {billing['character_count']}, "
    f"Cost: ${billing['amount']}"
)
````

Expected output example:

```
Original: Hello world!
Translated: ¡Hola mundo!
Characters: 12, Cost: $0.00024
```


