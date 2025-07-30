"""
Cost-optimized OpenAI service for NotebookBobu API
"""

import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings


class OpenAIService:
    """Cost-optimized OpenAI service with smart model selection"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Cost-optimized model configuration
        self.models = {
            # Ultra cheap for simple tasks (90% cheaper than GPT-4)
            "cheap": "gpt-4o-mini",  # $0.150/1M input, $0.600/1M output
            
            # Balanced for most tasks
            "balanced": "gpt-4o-mini",  # Same model, good quality/cost ratio 
            
            # Premium only when needed (for complex analysis)
            "premium": "gpt-4o",  # $2.50/1M input, $10.00/1M output
        }
        
        # Default to cheap model
        self.default_model = self.models["cheap"]
    
    async def analyze_document(self, content: str, title: str, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Analyze document with cost optimization
        Uses ultra-cheap model with token limits
        """
        
        # Truncate content if too long (save on input tokens)
        max_content_length = 8000  # ~2000 tokens
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...[truncated for cost efficiency]"
        
        prompt = f"""Analyze this document efficiently and concisely:

Title: {title}
Content: {content}

Provide a brief analysis with:
1. Summary (2-3 sentences max)
2. Key points (3-5 bullet points max)
3. Main topics (3 keywords max)

Be concise and direct."""

        try:
            response = await self._make_request(
                model=self.models["cheap"],  # Use cheapest model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,  # Limit output tokens
                temperature=0.3  # Lower temperature = more focused, less random
            )
            
            content = response.choices[0].message.content
            
            # Parse response into structured format
            return self._parse_analysis_response(content)
            
        except Exception as e:
            print(f"❌ OpenAI analysis failed: {e}")
            return self._get_fallback_analysis(title)
    
    async def generate_summary(self, content: str, max_tokens: int = 200) -> str:
        """Generate ultra-concise summary"""
        
        # Truncate for cost efficiency
        if len(content) > 6000:
            content = content[:6000] + "..."
        
        prompt = f"""Summarize this in exactly 2-3 sentences:

{content}

Summary:"""

        try:
            response = await self._make_request(
                model=self.models["cheap"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI summary failed: {e}")
            return f"Document summary unavailable. Title: {content[:100]}..."
    
    async def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """Extract key points with minimal token usage"""
        
        if len(content) > 5000:
            content = content[:5000] + "..."
        
        prompt = f"""Extract exactly {max_points} key points from this text.
Return only the bullet points, no introduction:

{content}

Key points:"""

        try:
            response = await self._make_request(
                model=self.models["cheap"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,  # Very limited
                temperature=0.1
            )
            
            points = response.choices[0].message.content.strip().split('\n')
            return [point.strip('- •').strip() for point in points if point.strip()][:max_points]
            
        except Exception as e:
            print(f"❌ OpenAI key points failed: {e}")
            return [f"Key point {i+1} from document" for i in range(max_points)]
    
    async def answer_question(self, question: str, context: str, max_tokens: int = 300) -> str:
        """Answer questions about documents with cost limits"""
        
        # Truncate context to save tokens
        if len(context) > 4000:
            context = context[:4000] + "..."
        
        prompt = f"""Based on this document context, answer the question briefly:

Context: {context}

Question: {question}

Answer (be concise):"""

        try:
            response = await self._make_request(
                model=self.models["cheap"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI Q&A failed: {e}")
            return "I couldn't process that question due to a service error."
    
    async def _make_request(self, **kwargs) -> Any:
        """Make OpenAI API request with error handling"""
        
        # Add cost-saving defaults
        defaults = {
            "temperature": 0.3,
            "max_tokens": 300,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        # Merge with provided kwargs
        params = {**defaults, **kwargs}
        
        # Make the request
        response = self.client.chat.completions.create(**params)
        return response
    
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse structured analysis response"""
        
        try:
            lines = content.split('\n')
            
            summary = ""
            key_points = []
            topics = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "summary" in line.lower():
                    current_section = "summary"
                elif "key points" in line.lower() or "points" in line.lower():
                    current_section = "points"
                elif "topics" in line.lower() or "keywords" in line.lower():
                    current_section = "topics"
                elif line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                    if current_section == "points":
                        key_points.append(line.lstrip('•-*123456789. ').strip())
                    elif current_section == "topics":
                        topics.append(line.lstrip('•-*123456789. ').strip())
                else:
                    if current_section == "summary":
                        summary += line + " "
            
            return {
                "summary": summary.strip() if summary else "Document processed successfully",
                "key_points": key_points[:5] if key_points else ["Key analysis completed"],
                "topics": topics[:3] if topics else ["General"],
                "confidence": "high" if summary and key_points else "medium"
            }
            
        except Exception as e:
            print(f"❌ Failed to parse analysis: {e}")
            return self._get_fallback_analysis("Unknown")
    
    def _get_fallback_analysis(self, title: str) -> Dict[str, Any]:
        """Fallback analysis when OpenAI fails"""
        return {
            "summary": f"Document '{title}' has been processed and is ready for analysis.",
            "key_points": [
                "Document content extracted",
                "Text processing completed", 
                "Ready for queries"
            ],
            "topics": ["Document", "Analysis"],
            "confidence": "low"
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = None) -> float:
        """Estimate API cost for transparency"""
        
        model = model or self.default_model
        
        # Cost per 1M tokens (as of 2024)
        costs = {
            "gpt-4o-mini": {"input": 0.150, "output": 0.600},
            "gpt-4o": {"input": 2.50, "output": 10.00},
        }
        
        if model not in costs:
            model = "gpt-4o-mini"
        
        input_cost = (input_tokens / 1_000_000) * costs[model]["input"]
        output_cost = (output_tokens / 1_000_000) * costs[model]["output"]
        
        return input_cost + output_cost


# Global service instance
openai_service = OpenAIService()