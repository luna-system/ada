# Build Your First Specialist

**Extend Ada with custom capabilities in 30 minutes.**

Specialists are Ada's plugin system. Drop a Python file in `brain/specialists/` and your AI gains new powers - web search, image analysis, weather lookups, whatever you imagine.

This tutorial builds a **weather specialist** from scratch, teaching you the pattern for ANY specialist.

---

## What You'll Build

A specialist that:
- Activates when users ask about weather
- Calls a weather API
- Returns formatted data the AI can use
- Works bidirectionally (AI can invoke it mid-response)

**Time required:** 30 minutes  
**Difficulty:** Intermediate (basic Python knowledge)

---

## Prerequisites

1. Ada running locally (`docker compose up`)
2. Python 3.13+ (for local testing)
3. A weather API key (we'll use OpenWeatherMap free tier)

### Get a Weather API Key

1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Generate API key (takes ~10 minutes to activate)
4. Save it - we'll use it in Step 3

---

## Step 1: Understand the Specialist Protocol

All specialists inherit from `BaseSpecialist` and implement two methods:

```python
from brain.specialists.protocol import BaseSpecialist, SpecialistResult

class MySpecialist(BaseSpecialist):
    def should_activate(self, request_context: dict) -> bool:
        """Should this specialist run for this request?"""
        return 'my_trigger' in request_context
    
    async def process(self, **kwargs) -> SpecialistResult:
        """Do the actual work and return results."""
        return SpecialistResult(
            specialist_name="my_specialist",
            success=True,
            data={"message": "Hello!"}
        )
```

**Key concepts:**
- `should_activate()` - When to run (user uploaded image? Mentioned "weather"?)
- `process()` - What to do (call API, analyze data, return results)
- `SpecialistResult` - Standard return format

---

## Step 2: Create the File

```bash
cd brain/specialists
touch weather_specialist.py
```

The `_specialist.py` suffix is required for auto-discovery.

---

## Step 3: Write the Specialist

Open `brain/specialists/weather_specialist.py`:

```python
"""
Weather specialist - provides current weather information via OpenWeatherMap API.

@ai-specialist: weather
@ai-activation-trigger: User asks about weather/temperature/forecast
@ai-priority: MEDIUM
"""
import os
import httpx
from typing import Optional
from .protocol import BaseSpecialist, SpecialistCapability, SpecialistResult, SpecialistPriority

class WeatherSpecialist(BaseSpecialist):
    """Fetches current weather data for locations."""
    
    def __init__(self):
        """Initialize with API key from environment."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self._capability = SpecialistCapability(
            name="weather",
            description="Get current weather conditions for any location",
            context_priority=SpecialistPriority.MEDIUM,
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or 'City, Country'"
                    }
                },
                "required": ["location"]
            },
            tags=["weather", "real-time", "api"]
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        """Return capability metadata."""
        return self._capability
    
    def should_activate(self, request_context: dict) -> bool:
        """
        Activate if:
        - User message mentions weather/temperature/forecast keywords
        - Weather tag present (for bidirectional calls)
        """
        user_message = request_context.get("user_message", "").lower()
        
        # Check for weather keywords
        weather_keywords = ["weather", "temperature", "forecast", "hot", "cold", 
                          "rain", "snow", "sunny", "cloudy"]
        
        if any(keyword in user_message for keyword in weather_keywords):
            return True
        
        # Check for bidirectional activation
        if request_context.get("specialist_request") == "weather":
            return True
        
        return False
    
    def can_handle(self, request_context: dict) -> bool:
        """Alias for should_activate (required by protocol)."""
        return self.should_activate(request_context)
    
    async def process(self, location: Optional[str] = None, **kwargs) -> SpecialistResult:
        """
        Fetch weather data for the specified location.
        
        Args:
            location: City name (e.g., "Chicago" or "London, UK")
        
        Returns:
            SpecialistResult with weather data or error
        """
        specialist_name = "weather"
        
        # Validate we have API key
        if not self.api_key:
            return SpecialistResult(
                specialist_name=specialist_name,
                success=False,
                error="Weather API key not configured. Set OPENWEATHER_API_KEY environment variable."
            )
        
        # Validate location provided
        if not location:
            # Try to extract from kwargs or return error
            request_context = kwargs.get("request_context", {})
            user_message = request_context.get("user_message", "")
            
            # Simple extraction: look for city names (you could use NER here)
            # For now, return an error asking for location
            return SpecialistResult(
                specialist_name=specialist_name,
                success=False,
                error="Please specify a location. Example: 'weather in Chicago'"
            )
        
        # Call OpenWeatherMap API
        try:
            async with httpx.AsyncClient() as client:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"  # Celsius
                }
                
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            # Extract relevant information
            weather_info = {
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature_celsius": data["main"]["temp"],
                "temperature_fahrenheit": (data["main"]["temp"] * 9/5) + 32,
                "feels_like_celsius": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "timestamp": data["dt"]
            }
            
            # Format for LLM consumption
            formatted_response = (
                f"Current weather in {weather_info['location']}, {weather_info['country']}:\n"
                f"- Temperature: {weather_info['temperature_celsius']:.1f}°C / "
                f"{weather_info['temperature_fahrenheit']:.1f}°F\n"
                f"- Feels like: {weather_info['feels_like_celsius']:.1f}°C\n"
                f"- Conditions: {weather_info['description'].capitalize()}\n"
                f"- Humidity: {weather_info['humidity']}%\n"
                f"- Wind speed: {weather_info['wind_speed']} m/s"
            )
            
            return SpecialistResult(
                specialist_name=specialist_name,
                success=True,
                data=weather_info,
                message=formatted_response,
                context_note=f"Weather data for {location}"
            )
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return SpecialistResult(
                    specialist_name=specialist_name,
                    success=False,
                    error=f"Location '{location}' not found. Try being more specific (e.g., 'London, UK')."
                )
            return SpecialistResult(
                specialist_name=specialist_name,
                success=False,
                error=f"Weather API error: {e}"
            )
        
        except Exception as e:
            return SpecialistResult(
                specialist_name=specialist_name,
                success=False,
                error=f"Failed to fetch weather: {str(e)}"
            )
```

**What this does:**
- `__init__()` - Loads API key, defines capability metadata
- `should_activate()` - Checks for weather keywords in user message
- `process()` - Calls OpenWeatherMap API, formats response
- Returns structured data the AI can use naturally

---

## Step 4: Add API Key to Environment

Edit `.env` in project root:

```bash
# Add this line
OPENWEATHER_API_KEY=your_api_key_here
```

---

## Step 5: Restart Services

```bash
docker compose restart brain
```

The specialist is automatically discovered - no registration needed!

---

## Step 6: Test It

### Via Web Interface

Visit http://localhost:5000 and ask:

> "What's the weather like in Tokyo?"

You should see:
1. A notice that the weather specialist activated
2. Current weather data
3. The AI using that data to respond naturally

### Via API

```bash
curl -X POST http://localhost:5000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Weather in Paris?", "stream": false}'
```

### Check Specialist Registration

Visit http://localhost:5000/api/specialists

Your weather specialist should appear in the list with full capability metadata!

---

## Step 7: Enable Bidirectional Mode (Advanced)

Let the AI invoke weather lookups mid-response:

1. **Modify activation pattern**

Already done! Our `should_activate()` checks for `specialist_request == "weather"`.

2. **Update system instructions** (optional)

Edit `brain/config.py` to mention weather in `SPECIALIST_INSTRUCTIONS`:

```python
- weather: Get current weather for any location
  Example: SPECIALIST_REQUEST[weather:{"location":"Chicago"}]
```

3. **Test bidirectional**

Ask something like:

> "Compare the weather in New York and London right now."

The AI should:
- Recognize it needs weather data
- Emit specialist requests for both cities
- Receive results
- Compare them naturally

---

## Understanding the Code

### Key Patterns

**1. Activation Logic**
```python
def should_activate(self, request_context: dict) -> bool:
    # Check user message
    if "weather" in request_context.get("user_message", "").lower():
        return True
    
    # Check bidirectional request
    if request_context.get("specialist_request") == "weather":
        return True
    
    return False
```

**2. Error Handling**
```python
try:
    # ... do work ...
    return SpecialistResult(success=True, data=result)
except SpecificError:
    return SpecialistResult(success=False, error="Friendly message")
```

**3. LLM-Friendly Formatting**
```python
# Return BOTH structured data AND formatted message
return SpecialistResult(
    data={"temp": 72, "conditions": "sunny"},  # Structured
    message="Temperature: 72°F, sunny skies"   # Formatted
)
```

The AI gets both - structured for processing, formatted for natural language.

---

## Common Patterns

### File Upload Specialist

```python
def should_activate(self, request_context: dict) -> bool:
    return request_context.get("has_file_upload", False)

async def process(self, file_path: str, **kwargs) -> SpecialistResult:
    # Read file, analyze, return results
    with open(file_path, 'r') as f:
        content = f.read()
    # ...
```

### Database Query Specialist

```python
async def process(self, query: str, **kwargs) -> SpecialistResult:
    async with db_pool.acquire() as conn:
        results = await conn.fetch(query)
    return SpecialistResult(success=True, data=results)
```

### External API Specialist

```python
async def process(self, search_term: str, **kwargs) -> SpecialistResult:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/search?q={search_term}")
    return SpecialistResult(success=True, data=response.json())
```

---

## Testing Your Specialist

### Unit Test

Create `tests/test_weather_specialist.py`:

```python
import pytest
from brain.specialists.weather_specialist import WeatherSpecialist

@pytest.mark.asyncio
async def test_weather_specialist_activation():
    specialist = WeatherSpecialist()
    
    # Should activate on weather keywords
    context = {"user_message": "What's the weather like today?"}
    assert specialist.should_activate(context) == True
    
    # Should not activate on unrelated messages
    context = {"user_message": "Hello, how are you?"}
    assert specialist.should_activate(context) == False

@pytest.mark.asyncio
async def test_weather_specialist_process():
    specialist = WeatherSpecialist()
    
    # Test with valid location
    result = await specialist.process(location="London")
    
    if specialist.api_key:  # Only if API key configured
        assert result.success == True
        assert "temperature_celsius" in result.data
    else:
        assert result.success == False
        assert "not configured" in result.error
```

Run tests:

```bash
docker compose run --rm scripts pytest tests/test_weather_specialist.py -v
```

---

## Debugging Tips

**Specialist not activating?**

Check brain logs:

```bash
docker compose logs brain -f
```

You'll see which specialists are discovered and why they activate/don't activate.

**API errors?**

Add logging in your `process()` method:

```python
import logging
logger = logging.getLogger(__name__)

async def process(self, **kwargs):
    logger.info(f"Weather specialist processing: {kwargs}")
    # ...
```

**Want to see all specialist activity?**

Visit http://localhost:5000/api/info and check the `specialists` section.

---

## Next Steps

Now that you've built a specialist:

1. **Add it to the registry** - Update `.ai/specialist-registry.json`
2. **Write tests** - Add to `tests/test_specialists.py`
3. **Document it** - Add usage examples
4. **Share it!** - Submit a PR or publish separately

### Ideas for More Specialists

- **Calendar** - Check your schedule, add events
- **Code execution** - Run Python snippets safely
- **Database** - Query your personal databases
- **Home automation** - Control smart home devices
- **Translation** - Real-time language translation
- **Calculations** - Complex math via SymPy
- **Email** - Read/send emails
- **Git operations** - Commit, push, create PRs
- **RSS feeds** - Check news from sources you follow

The pattern is always the same - implement the protocol, drop it in `specialists/`, restart.

---

## Need Help?

- **Protocol documentation:** See `brain/specialists/protocol.py`
- **Example specialists:** Check existing ones in `brain/specialists/`
- **Issues:** https://github.com/yourusername/ada/issues

Remember: Your weird specialist idea might be exactly what someone else needs! 🚀
