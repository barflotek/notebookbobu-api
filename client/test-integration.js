/**
 * Simple Node.js test script to verify NotebookBobu integration
 * Run with: node test-integration.js
 */

const https = require('https');

const API_BASE = 'https://notebookbobu-g1wdc943m-sentinel-io.vercel.app';
const API_KEY = 'inbox-zero-api-key-2024';

function makeRequest(path, options = {}) {
  return new Promise((resolve, reject) => {
    const url = `${API_BASE}/api${path}`;
    const requestOptions = {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      method: options.method || 'GET'
    };

    const req = https.request(url, requestOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(jsonData);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${jsonData.detail || JSON.stringify(jsonData)}`));
          }
        } catch (e) {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

async function testBasicAuth() {
  console.log('🔐 Testing API Authentication...');
  
  try {
    const health = await makeRequest('/health');
    console.log('✅ Authentication successful');
    console.log('📊 API Status:', health.status);
    console.log('🔧 Environment:', health.environment);
    console.log('🔑 API Keys configured:', health.api_keys.main_configured && health.api_keys.inbox_configured);
    return true;
  } catch (error) {
    console.error('❌ Authentication failed:', error.message);
    return false;
  }
}

async function testDocumentsList() {
  console.log('\n📋 Testing Documents List...');
  
  try {
    const documents = await makeRequest('/documents');
    console.log(`✅ Successfully retrieved ${documents.length} documents`);
    
    if (documents.length > 0) {
      console.log('📄 Sample document:', {
        id: documents[0].id,
        title: documents[0].title,
        status: documents[0].status
      });
    }
    
    return true;
  } catch (error) {
    console.error('❌ Failed to get documents:', error.message);
    return false;
  }
}

async function testDocumentsV2List() {
  console.log('\n📋 Testing Documents V2 List...');
  
  try {
    const documents = await makeRequest('/v2/documents');
    console.log(`✅ Successfully retrieved ${documents.length} documents from V2 API`);
    return true;
  } catch (error) {
    console.error('❌ Failed to get V2 documents:', error.message);
    return false;
  }
}

async function testQuery() {
  console.log('\n❓ Testing Document Query...');
  
  try {
    const response = await makeRequest('/query', {
      method: 'POST',
      body: JSON.stringify({
        question: 'What documents are available?',
        document_ids: []
      })
    });
    
    console.log('✅ Query successful');
    console.log('🤖 Answer:', response.answer ? response.answer.substring(0, 100) + '...' : 'No answer provided');
    console.log('📊 Success:', response.success);
    return true;
  } catch (error) {
    // No documents to query is expected when database is empty
    if (error.message.includes('No documents found to query')) {
      console.log('✅ Query endpoint working (no documents available to query)');
      return true;
    } else {
      console.error('❌ Query failed:', error.message);
      return false;
    }
  }
}

async function testInvalidAuth() {
  console.log('\n🚫 Testing Invalid Authentication...');
  
  try {
    await makeRequest('/documents', {
      headers: {
        'Authorization': 'Bearer invalid-key-12345'
      }
    });
    console.error('❌ Should have failed with invalid key');
    return false;
  } catch (error) {
    if (error.message.includes('Invalid API key')) {
      console.log('✅ Correctly rejected invalid API key');
      return true;
    } else {
      console.error('❌ Unexpected error:', error.message);
      return false;
    }
  }
}

async function runAllTests() {
  console.log('🧪 NotebookBobu API Integration Tests\n');
  console.log('🔗 API URL:', API_BASE);
  console.log('🔑 Using API Key:', API_KEY.substring(0, 10) + '...\n');
  
  const tests = [
    { name: 'Basic Authentication', fn: testBasicAuth },
    { name: 'Documents List', fn: testDocumentsList },
    { name: 'Documents V2 List', fn: testDocumentsV2List },
    { name: 'Document Query', fn: testQuery },
    { name: 'Invalid Authentication', fn: testInvalidAuth }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    try {
      const result = await test.fn();
      if (result) {
        passed++;
      } else {
        failed++;
      }
    } catch (error) {
      console.error(`❌ Test "${test.name}" threw error:`, error.message);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('🏁 Test Results:');
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`📊 Success Rate: ${Math.round((passed / (passed + failed)) * 100)}%`);
  
  if (passed === tests.length) {
    console.log('\n🎉 All tests passed! NotebookBobu API is ready for inbox-zero integration.');
    return true;
  } else {
    console.log('\n⚠️  Some tests failed. Please check the API configuration.');
    return false;
  }
}

// Run tests
runAllTests().catch(console.error);