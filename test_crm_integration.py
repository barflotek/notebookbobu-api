#!/usr/bin/env python3
"""
Test script for CRM integration
Tests the new client management endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000/api"
API_KEY = "your-internal-api-key"  # Update with your actual API key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def test_crm_endpoints():
    """Test the new CRM endpoints"""
    
    async with httpx.AsyncClient() as client:
        
        print("🧪 Testing NotebookBobu CRM Integration")
        print("=" * 50)
        
        # Test 1: Health check
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ Health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test 2: Create client
        print("\n📋 Testing client creation...")
        client_data = {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "+1-555-123-4567",
            "client_type": "beginner",
            "equipment_preference": "sabre"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/clients", json=client_data, headers=headers)
            if response.status_code == 200:
                client_id = response.json().get("id")
                print(f"✅ Client created: {client_id}")
            else:
                print(f"⚠️  Client creation returned: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Client creation failed: {e}")
        
        # Test 3: List clients
        print("\n📑 Testing client listing...")
        try:
            response = await client.get(f"{BASE_URL}/clients", headers=headers)
            print(f"✅ Client listing: {response.status_code} - {len(response.json() or [])} clients")
        except Exception as e:
            print(f"❌ Client listing failed: {e}")
        
        # Test 4: CRM Dashboard
        print("\n📊 Testing CRM dashboard...")
        try:
            response = await client.get(f"{BASE_URL}/crm/dashboard", headers=headers)
            if response.status_code == 200:
                dashboard = response.json()
                print(f"✅ Dashboard loaded - {dashboard.get('stats', {}).get('active_clients', 0)} active clients")
            else:
                print(f"⚠️  Dashboard returned: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard failed: {e}")
        
        # Test 5: Create task
        print("\n📝 Testing task creation...")
        if 'client_id' in locals():
            task_data = {
                "client_id": client_id,
                "title": "Follow up call",
                "description": "Check on lesson progress",
                "type": "follow_up",
                "priority": "normal"
            }
            
            try:
                response = await client.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
                if response.status_code == 200:
                    task = response.json()
                    print(f"✅ Task created: {task.get('id')}")
                else:
                    print(f"⚠️  Task creation returned: {response.status_code}")
            except Exception as e:
                print(f"❌ Task creation failed: {e}")
        
        # Test 6: Document-client linking (mock)
        print("\n🔗 Testing document-client linking...")
        if 'client_id' in locals():
            link_data = {
                "client_id": client_id,
                "subject": "Email attachment analysis"
            }
            
            try:
                mock_doc_id = "test-document-123"
                response = await client.post(
                    f"{BASE_URL}/documents/{mock_doc_id}/link-client", 
                    json=link_data, 
                    headers=headers
                )
                print(f"✅ Document linking: {response.status_code}")
            except Exception as e:
                print(f"❌ Document linking failed: {e}")
        
        # Test 7: Client insights
        print("\n🤖 Testing AI insights...")
        if 'client_id' in locals():
            try:
                response = await client.get(f"{BASE_URL}/clients/{client_id}/insights", headers=headers)
                if response.status_code == 200:
                    insights = response.json()
                    print(f"✅ Insights generated - Risk level: {insights.get('risk_level')}")
                else:
                    print(f"⚠️  Insights returned: {response.status_code}")
            except Exception as e:
                print(f"❌ Insights failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 CRM Integration Test Complete!")
        print("\nNext steps:")
        print("1. Run the database schema: database/client_schema.sql")
        print("2. Implement repository classes with Supabase")
        print("3. Connect domain services to container")
        print("4. Test with real email processing workflow")


def test_entities():
    """Test the domain entities work correctly"""
    
    print("\n🏗️  Testing Domain Entities")
    print("-" * 30)
    
    from app.domain.client.entity import Client, ClientType, ClientStatus
    from app.domain.client.entity import Communication, CommunicationType
    from app.domain.client.entity import Task, TaskStatus
    
    # Test Client entity
    client = Client(
        user_id="test-user",
        name="Test Client",
        email="test@example.com",
        client_type=ClientType.BEGINNER,
        status=ClientStatus.ACTIVE
    )
    print(f"✅ Client entity: {client.name} ({client.client_type})")
    
    # Test Communication entity
    comm = Communication(
        client_id="client-123",
        user_id="user-123",
        type=CommunicationType.EMAIL,
        subject="Welcome email",
        occurred_at=datetime.now()
    )
    print(f"✅ Communication entity: {comm.type} - {comm.subject}")
    
    # Test Task entity
    task = Task(
        client_id="client-123",
        user_id="user-123",
        title="Follow up call",
        status=TaskStatus.PENDING
    )
    print(f"✅ Task entity: {task.title} ({task.status})")


if __name__ == "__main__":
    print("🚀 Starting NotebookBobu CRM Integration Tests")
    
    # Test entities first
    try:
        test_entities()
    except Exception as e:
        print(f"❌ Entity tests failed: {e}")
        exit(1)
    
    # Test API endpoints
    try:
        asyncio.run(test_crm_endpoints())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        exit(1)