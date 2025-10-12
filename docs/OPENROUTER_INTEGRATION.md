# OpenRouter Integration Guide for Brody
## Leveraging Multiple LLMs Through Single API

**OpenRouter Advantage**: Access to 100+ AI models through one API  
**Cost Efficiency**: Competitive pricing across providers  
**Flexibility**: Switch models based on task requirements

---

## 🔧 OpenRouter Setup & Integration

### 1. Environment Configuration

```bash
# .env file setup
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_MODEL=openai/gpt-4o-mini
```

### 2. OpenRouter Service Implementation

```python
# backend/services/openrouter_service.py
import openai
from typing import Dict, List, Optional
from pydantic import BaseModel

class OpenRouterService:
    """
    Unified AI service using OpenRouter for multiple LLM access
    """
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL")
        )
        
        # Model selection for different tasks
        self.model_config = {
            "email_classification": "anthropic/claude-3.5-sonnet",
            "task_generation": "openai/gpt-4o",
            "meeting_brief": "anthropic/claude-3.5-sonnet",
            "summarization": "openai/gpt-4o-mini",  # Cost-effective for simple tasks
            "complex_reasoning": "anthropic/claude-3.5-sonnet",
            "quick_analysis": "openai/gpt-4o-mini"
        }
    
    async def classify_email(self, email_content: str) -> EmailClassification:
        """
        Classify email using best model for analysis tasks
        """
        model = self.model_config["email_classification"]
        
        prompt = f"""
        Analyze this email and classify it:
        
        Subject: {email_content.get('subject', '')}
        From: {email_content.get('sender', '')}
        Body: {email_content.get('body', '')}
        
        Classify the email with:
        1. Urgency: high, medium, low
        2. Category: work, personal, promotional, newsletter, meeting, task
        3. Sentiment: positive, neutral, negative
        4. Action required: response_needed, fyi, action_item, meeting_invite
        5. Summary: Brief 1-sentence summary
        
        Return as JSON format.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert email classifier. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return EmailClassification.parse_raw(result)
            
        except Exception as e:
            # Fallback to simpler model
            return await self._fallback_classification(email_content)
    
    async def generate_task_suggestions(self, email: EmailMessage) -> List[TaskSuggestion]:
        """
        Generate intelligent task suggestions from email content
        """
        model = self.model_config["task_generation"]
        
        prompt = f"""
        Based on this email, suggest relevant tasks:
        
        Email Details:
        - Subject: {email.subject}
        - From: {email.sender}
        - Body: {email.body[:1000]}...
        - Timestamp: {email.timestamp}
        
        Generate 1-3 specific, actionable tasks that would naturally follow from this email.
        Consider:
        - What actions does the email request or imply?
        - What deadlines or timeframes are mentioned?
        - What level of priority should each task have?
        
        Return as JSON array with: title, description, priority, estimated_duration, due_date
        """
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a productivity expert. Generate practical, actionable tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        return self._parse_task_suggestions(response.choices[0].message.content)
    
    async def prepare_meeting_brief(self, meeting: CalendarEvent, related_emails: List[EmailMessage] = None) -> MeetingBrief:
        """
        Generate comprehensive meeting preparation using advanced reasoning
        """
        model = self.model_config["meeting_brief"]
        
        context = f"""
        Meeting: {meeting.title}
        Time: {meeting.start_time} - {meeting.end_time}
        Attendees: {', '.join(meeting.attendees)}
        Description: {meeting.description}
        """
        
        if related_emails:
            context += f"\nRelated Emails:\n"
            for email in related_emails[:3]:  # Limit context
                context += f"- From {email.sender}: {email.subject}\n"
        
        prompt = f"""
        Prepare a comprehensive meeting brief:
        
        {context}
        
        Generate:
        1. Meeting objective and expected outcomes
        2. Key discussion points and agenda items
        3. Background context and recent developments
        4. Action items to prepare beforehand
        5. Questions to ask during the meeting
        6. Post-meeting follow-up suggestions
        
        Make it concise but thorough - this should save the attendee 15+ minutes of prep time.
        """
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an executive assistant expert at meeting preparation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1200
        )
        
        return self._parse_meeting_brief(response.choices[0].message.content)
    
    async def intelligent_model_selection(self, task_type: str, complexity: str, cost_priority: str) -> str:
        """
        Dynamically select the best model based on task requirements
        """
        if cost_priority == "low_cost":
            return "openai/gpt-4o-mini"
        elif complexity == "high" or task_type == "reasoning":
            return "anthropic/claude-3.5-sonnet"
        elif task_type == "creative":
            return "openai/gpt-4o"
        else:
            return self.model_config.get(task_type, "openai/gpt-4o-mini")
```

### 3. Model Selection Strategy

```python
# backend/services/model_selector.py
class ModelSelector:
    """
    Intelligent model selection based on task requirements and cost optimization
    """
    
    MODEL_COSTS = {
        "openai/gpt-4o": {"input": 5.00, "output": 15.00},  # per 1M tokens
        "anthropic/claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "google/gemini-pro": {"input": 1.25, "output": 5.00}
    }
    
    MODEL_CAPABILITIES = {
        "openai/gpt-4o": {
            "reasoning": 9, "creativity": 9, "speed": 7, "cost_efficiency": 4
        },
        "anthropic/claude-3.5-sonnet": {
            "reasoning": 10, "creativity": 8, "speed": 8, "cost_efficiency": 6
        },
        "openai/gpt-4o-mini": {
            "reasoning": 7, "creativity": 6, "speed": 10, "cost_efficiency": 10
        },
        "google/gemini-pro": {
            "reasoning": 8, "creativity": 7, "speed": 9, "cost_efficiency": 8
        }
    }
    
    def select_optimal_model(self, 
                           task_type: str, 
                           complexity: str, 
                           speed_requirement: str,
                           cost_priority: str) -> str:
        """
        Select the best model based on multiple factors
        """
        
        # Task-specific preferences
        task_preferences = {
            "email_classification": {"reasoning": 8, "speed": 9, "cost_efficiency": 7},
            "task_generation": {"reasoning": 9, "creativity": 7, "cost_efficiency": 6},
            "meeting_brief": {"reasoning": 9, "creativity": 8, "cost_efficiency": 5},
            "summarization": {"reasoning": 6, "speed": 10, "cost_efficiency": 10}
        }
        
        preferences = task_preferences.get(task_type, {
            "reasoning": 7, "creativity": 6, "speed": 8, "cost_efficiency": 8
        })
        
        # Score each model
        scores = {}
        for model, capabilities in self.MODEL_CAPABILITIES.items():
            score = 0
            for factor, weight in preferences.items():
                score += capabilities[factor] * weight
            scores[model] = score
        
        # Return highest scoring model
        return max(scores, key=scores.get)
```

---

## 💰 Cost Optimization with OpenRouter

### 1. Intelligent Token Management

```python
# backend/services/cost_optimizer.py
class CostOptimizer:
    """
    Optimize AI costs while maintaining quality
    """
    
    def __init__(self):
        self.daily_budget = 50.00  # $50/day AI budget
        self.current_spend = 0.0
        self.request_cache = {}  # Cache similar requests
    
    async def should_use_premium_model(self, task_complexity: str, user_tier: str) -> bool:
        """
        Decide whether to use expensive models based on budget and user tier
        """
        if user_tier == "enterprise":
            return True
        
        if self.current_spend > self.daily_budget * 0.8:
            return False  # Use budget models when near limit
        
        if task_complexity == "high":
            return True
        
        return False
    
    async def optimize_prompt(self, original_prompt: str) -> str:
        """
        Optimize prompts to reduce token usage while maintaining quality
        """
        # Remove unnecessary whitespace and redundancy
        optimized = ' '.join(original_prompt.split())
        
        # Use concise instructions
        optimizations = {
            "Please analyze this email and provide": "Analyze email:",
            "Generate a comprehensive summary": "Summarize:",
            "Based on the following information": "Given:",
        }
        
        for old, new in optimizations.items():
            optimized = optimized.replace(old, new)
        
        return optimized
```

### 2. Caching Strategy

```python
# backend/services/ai_cache.py
import hashlib
import json
from datetime import datetime, timedelta

class AIResponseCache:
    """
    Cache AI responses to reduce API calls and costs
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = {
            "email_classification": timedelta(hours=24),
            "task_generation": timedelta(hours=12),
            "meeting_brief": timedelta(hours=6)
        }
    
    def get_cache_key(self, task_type: str, content: str) -> str:
        """
        Generate unique cache key for content
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{task_type}:{content_hash}"
    
    async def get_cached_response(self, task_type: str, content: str):
        """
        Retrieve cached response if valid
        """
        cache_key = self.get_cache_key(task_type, content)
        
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            expiry_time = cached_item["timestamp"] + self.cache_duration[task_type]
            
            if datetime.now() < expiry_time:
                return cached_item["response"]
        
        return None
    
    async def cache_response(self, task_type: str, content: str, response):
        """
        Cache AI response for future use
        """
        cache_key = self.get_cache_key(task_type, content)
        self.cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }
```

---

## 🚀 Implementation Priority for Phase 1

### Week 1: OpenRouter Foundation
1. **Set up OpenRouter API keys** and test connectivity
2. **Implement basic OpenRouterService** with email classification
3. **Add model selection logic** for different task types
4. **Create caching layer** to minimize API costs

### Week 2: Advanced Features
1. **Implement task suggestion AI** using GPT-4o for complex reasoning
2. **Add meeting brief generation** using Claude for detailed analysis
3. **Create cost optimization** system with daily budgets
4. **Add fallback mechanisms** for API failures

### Benefits of OpenRouter for Brody:

✅ **Single API Integration** - No need to manage multiple provider APIs  
✅ **Cost Optimization** - Access to most cost-effective models  
✅ **Model Flexibility** - Switch models based on task requirements  
✅ **Reduced Complexity** - Unified authentication and billing  
✅ **Competitive Pricing** - Often better rates than direct provider access  
✅ **Fallback Options** - Multiple models for reliability  

### Recommended Model Usage:
- **Email Classification**: Claude 3.5 Sonnet (best reasoning)
- **Task Generation**: GPT-4o (creative + structured output)
- **Quick Tasks**: GPT-4o Mini (cost-effective)
- **Meeting Briefs**: Claude 3.5 Sonnet (comprehensive analysis)
- **Summarization**: GPT-4o Mini (simple, fast, cheap)

This OpenRouter integration gives Brody a significant advantage - access to the best AI models while maintaining cost efficiency and implementation simplicity! 🎯