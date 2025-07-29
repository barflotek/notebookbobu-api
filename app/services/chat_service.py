"""
Chat and query service for document interaction
"""

import asyncio
import uuid
from typing import Dict, Any, List
import openai

from app.core.config import settings


class ChatService:
    """Chat and query service for processed documents"""
    
    def __init__(self):
        self.openai_available = False
        
        # Initialize OpenAI if available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_available = True
            print("✅ OpenAI API configured")
        else:
            print("⚠️  OpenAI API key not found - using mock responses")
    
    async def query_documents(
        self, 
        question: str, 
        documents: List[Dict[str, Any]], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Query processed documents with natural language
        """
        
        if self.openai_available:
            return await self._query_with_openai(question, documents)
        else:
            return await self._query_mock(question, documents)
    
    async def _query_with_openai(
        self, 
        question: str, 
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Query documents using OpenAI"""
        
        try:
            # Prepare context from documents
            context = ""
            sources = []
            
            for doc in documents:
                context += f"\\n\\n--- Document: {doc['title']} ---\\n"
                if doc.get('summary'):
                    context += f"Summary: {doc['summary']}\\n"
                if doc.get('bullet_points'):
                    context += f"Key Points: {doc['bullet_points']}\\n"
                sources.append(doc['title'])
            
            # Create prompt
            prompt = f"""Based on the following documents, please answer the user's question.
            
Documents:
{context}

Question: {question}

Please provide a comprehensive answer based on the document content. If the answer cannot be found in the documents, please say so clearly.

Answer:"""
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents. Always cite your sources and be accurate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "sources": sources,
                "method": "openai"
            }
            
        except Exception as e:
            print(f"❌ OpenAI query failed: {e}")
            # Fall back to mock response
            return await self._query_mock(question, documents)
    
    async def _query_mock(
        self, 
        question: str, 
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock query response for development"""
        
        print(f"🎭 Mock query: {question}")
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        sources = [doc['title'] for doc in documents]
        
        answer = f"""🤖 **NotebookBobu AI Response**

Based on the {len(documents)} document(s) in your collection, here's what I found regarding your question: "{question}"

**Analysis:**
I've analyzed the content from your documents: {', '.join(sources)}. The information has been processed using advanced AI techniques to provide you with relevant insights.

**Key Findings:**
• Your documents contain valuable information related to your query
• Multiple perspectives and data points have been considered
• The analysis draws from comprehensive document processing
• Cross-references between documents have been identified where relevant

**Summary:**
This response synthesizes information from your document collection to address your specific question. The AI system has processed the content to provide contextually relevant insights based on the available information.

*Note: This is a mock response for development/testing. In production, this would use advanced AI models to provide specific, accurate answers based on your document content.*

**Sources consulted:** {', '.join(sources)}"""
        
        return {
            "answer": answer,
            "sources": sources,
            "method": "mock"
        }
    
    async def generate_podcast(
        self,
        documents: List[Dict[str, Any]],
        title: str,
        voice_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a podcast from documents
        """
        
        print(f"🎙️ Generating podcast: {title}")
        
        # Simulate podcast generation
        await asyncio.sleep(2)
        
        podcast_id = str(uuid.uuid4())
        
        # Create transcript
        transcript = f"""🎙️ **{title}**

Welcome to your personalized podcast generated by NotebookBobu AI!

Today we're exploring {len(documents)} documents from your collection:
{', '.join([doc['title'] for doc in documents])}

**Introduction**
This podcast has been automatically generated from your document collection, providing you with an audio summary of the key insights and information.

**Main Content**
Based on the documents you've provided, we'll cover the main themes, important findings, and actionable insights that have been extracted through AI analysis.

**Key Takeaways**
- Comprehensive analysis of your document collection
- Important themes and patterns identified
- Actionable insights highlighted
- Cross-document connections established

**Conclusion**
Thank you for listening to your NotebookBobu AI-generated podcast. This content was created specifically for you based on your document collection.

*Generated by NotebookBobu AI • Podcast ID: {podcast_id}*
"""
        
        return {
            "podcast_id": podcast_id,
            "title": title,
            "transcript": transcript,
            "audio_url": f"/api/podcast/{podcast_id}/audio",  # Mock URL
            "status": "completed"  # In real implementation, this would be "generating" initially
        }