/**
 * Simple upload test using the v1 API
 */

const https = require('https');

const API_BASE = 'https://notebookbobu-49fa1qs32-sentinel-io.vercel.app';
const API_KEY = 'inbox-zero-api-key-2024';

function createMultipartBody(fields, file) {
  const boundary = '----formdata-boundary-' + Math.random().toString(36);
  let body = '';
  
  // Add form fields
  for (const [key, value] of Object.entries(fields)) {
    body += `--${boundary}\r\n`;
    body += `Content-Disposition: form-data; name="${key}"\r\n\r\n`;
    body += `${value}\r\n`;
  }
  
  // Add file
  if (file) {
    body += `--${boundary}\r\n`;
    body += `Content-Disposition: form-data; name="file"; filename="${file.filename}"\r\n`;
    body += `Content-Type: ${file.contentType}\r\n\r\n`;
    body += file.content;
    body += `\r\n`;
  }
  
  body += `--${boundary}--\r\n`;
  
  return { body, boundary };
}

function uploadDocument(endpoint, title, filename, content, contentType = 'text/plain') {
  return new Promise((resolve, reject) => {
    const { body, boundary } = createMultipartBody(
      { title }, 
      { filename, content, contentType }
    );
    
    const url = `${API_BASE}/api${endpoint}`;
    const options = {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': Buffer.byteLength(body)
      }
    };

    console.log('📤 Uploading to:', url);
    console.log('📋 Headers:', options.headers);

    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log('📥 Response status:', res.statusCode);
        console.log('📄 Response data:', data);
        
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

    req.on('error', (error) => {
      console.error('📡 Request error:', error);
      reject(error);
    });
    
    console.log('📨 Sending body length:', Buffer.byteLength(body));
    req.write(body);
    req.end();
  });
}

async function testV1Upload() {
  console.log('🧪 Testing V1 API Upload\n');
  
  const testContent = 'This is a simple test document for NotebookBobu API integration.';
  
  try {
    const result = await uploadDocument(
      '/process',
      'Simple Test Document',
      'test.txt',
      testContent,
      'text/plain'
    );
    
    console.log('✅ V1 Upload successful:', result);
    return true;
  } catch (error) {
    console.error('❌ V1 Upload failed:', error.message);
    return false;
  }
}

async function testV2Upload() {
  console.log('\n🧪 Testing V2 API Upload\n');
  
  const testContent = 'This is a simple test document for NotebookBobu V2 API integration.';
  
  try {
    const result = await uploadDocument(
      '/v2/process',
      'Simple Test Document V2',
      'test-v2.txt',
      testContent,
      'text/plain'
    );
    
    console.log('✅ V2 Upload successful:', result);
    return true;
  } catch (error) {
    console.error('❌ V2 Upload failed:', error.message);
    return false;
  }
}

async function main() {
  console.log('🚀 Simple Upload Test for NotebookBobu API\n');
  
  const v1Result = await testV1Upload();
  const v2Result = await testV2Upload();
  
  console.log('\n📊 Results:');
  console.log(`${v1Result ? '✅' : '❌'} V1 API Upload`);
  console.log(`${v2Result ? '✅' : '❌'} V2 API Upload`);
  
  if (v1Result || v2Result) {
    console.log('\n🎉 At least one API version is working!');
  } else {
    console.log('\n⚠️  Both API versions failed. Check server configuration.');
  }
}

main().catch(console.error);