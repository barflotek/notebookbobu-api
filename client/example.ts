/**
 * NotebookBobu API Client Usage Examples
 * 
 * This file demonstrates how to integrate NotebookBobu with inbox-zero
 */

import { 
  NotebookBobuClient, 
  createInboxZeroClient, 
  processEmailAttachment,
  getDocumentInsights,
  askQuestion 
} from './notebookbobu-client';

// Example 1: Basic client setup
async function basicExample() {
  console.log('🚀 Basic NotebookBobu API Example');
  
  // Create client with inbox-zero API key
  const client = createInboxZeroClient();
  
  // Check if API is working
  const health = await client.healthCheck();
  console.log('API Health:', health);
  
  // Get existing documents
  const documents = await client.getDocumentsV2();
  console.log(`Found ${documents.length} documents`);
}

// Example 2: Process an email attachment
async function processAttachmentExample() {
  console.log('📎 Processing Email Attachment Example');
  
  const client = createInboxZeroClient();
  
  // Simulate processing a PDF attachment from an email
  // In real inbox-zero integration, you'd get this from the email
  const mockPdfContent = Buffer.from('Mock PDF content');
  const filename = 'important-document.pdf';
  const emailSubject = 'Q4 Financial Report';
  
  try {
    const result = await processEmailAttachment(
      client,
      mockPdfContent,
      filename,
      emailSubject
    );
    
    console.log('Processing result:', result);
    console.log('Document ID:', result.document.id);
    console.log('Status:', result.document.status);
    
    // Wait for processing to complete (in real app, you might poll or use webhooks)
    setTimeout(async () => {
      const insights = await getDocumentInsights(client, result.document.id);
      console.log('Document insights:', insights);
    }, 5000);
    
  } catch (error) {
    console.error('Failed to process attachment:', error);
  }
}

// Example 3: Query documents with natural language
async function queryExample() {
  console.log('❓ Document Query Example');
  
  const client = createInboxZeroClient();
  
  try {
    // Ask questions about processed documents
    const questions = [
      'What are the key findings from recent financial reports?',
      'Summarize all meeting notes from this week',
      'What action items were mentioned in project documents?'
    ];
    
    for (const question of questions) {
      const answer = await askQuestion(client, question);
      console.log(`Q: ${question}`);
      console.log(`A: ${answer}\n`);
    }
    
  } catch (error) {
    console.error('Failed to query documents:', error);
  }
}

// Example 4: Search and organize documents
async function searchExample() {
  console.log('🔍 Document Search Example');
  
  const client = createInboxZeroClient();
  
  try {
    // Search for specific topics
    const financialDocs = await client.searchDocuments('financial report budget', 5);
    console.log(`Found ${financialDocs.length} financial documents`);
    
    const meetingNotes = await client.searchDocuments('meeting notes agenda', 5);
    console.log(`Found ${meetingNotes.length} meeting documents`);
    
    // Get detailed document information
    for (const doc of financialDocs) {
      console.log(`- ${doc.title} (${doc.type}) - ${doc.confidence} confidence`);
      if (doc.topics) {
        console.log(`  Topics: ${doc.topics.join(', ')}`);
      }
    }
    
  } catch (error) {
    console.error('Failed to search documents:', error);
  }
}

// Example 5: Complete inbox-zero workflow
async function inboxZeroWorkflow() {
  console.log('📧 Complete Inbox-Zero Integration Workflow');
  
  const client = createInboxZeroClient();
  
  // Simulate processing multiple email attachments
  const emailAttachments = [
    { filename: 'contract.pdf', subject: 'New Partnership Agreement', content: Buffer.from('Contract content') },
    { filename: 'invoice.pdf', subject: 'Invoice #12345', content: Buffer.from('Invoice content') },
    { filename: 'report.docx', subject: 'Weekly Status Report', content: Buffer.from('Report content') }
  ];
  
  const processedDocs = [];
  
  // Process all attachments
  for (const attachment of emailAttachments) {
    try {
      console.log(`Processing: ${attachment.filename}`);
      
      const result = await processEmailAttachment(
        client,
        attachment.content,
        attachment.filename,
        attachment.subject
      );
      
      processedDocs.push(result.document);
      console.log(`✅ Processed: ${result.document.id}`);
      
    } catch (error) {
      console.error(`❌ Failed to process ${attachment.filename}:`, error);
    }
  }
  
  // Wait a bit for processing to complete
  console.log('⏳ Waiting for processing to complete...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Ask questions about all processed documents
  const documentIds = processedDocs.map(doc => doc.id);
  
  const insights = await askQuestion(
    client,
    'What are the main topics covered in these documents?',
    documentIds
  );
  
  console.log('🧠 Combined insights:', insights);
  
  // Get chat history
  const chatHistory = await client.getChatHistory();
  console.log(`💬 Chat history: ${chatHistory.length} conversations`);
  
  return {
    processedDocuments: processedDocs.length,
    insights,
    chatHistory: chatHistory.length
  };
}

// Main execution
async function main() {
  console.log('🤖 NotebookBobu API Integration Examples\n');
  
  try {
    // Run examples (comment out as needed)
    await basicExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    // await processAttachmentExample();
    // console.log('\n' + '='.repeat(50) + '\n');
    
    // await queryExample();
    // console.log('\n' + '='.repeat(50) + '\n');
    
    // await searchExample();
    // console.log('\n' + '='.repeat(50) + '\n');
    
    // await inboxZeroWorkflow();
    
  } catch (error) {
    console.error('Example failed:', error);
  }
}

// Export for use in inbox-zero
export {
  basicExample,
  processAttachmentExample,
  queryExample,
  searchExample,
  inboxZeroWorkflow
};

// Run examples if this file is executed directly
if (require.main === module) {
  main();
}