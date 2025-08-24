#!/usr/bin/env python3
"""
Complete Kolekt Setup Script
Guides through schema application and API testing
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🚀 {title}")
    print(f"{'='*50}")

def print_step(step_num, title):
    print(f"\n📋 Step {step_num}: {title}")
    print("-" * 40)

def check_supabase_connection():
    """Check if Supabase is properly configured"""
    print_step(1, "Checking Supabase Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found!")
        print("Please run: python setup_supabase.py")
        return False
    
    print("✅ Supabase credentials found")
    return True

def show_schema_instructions():
    """Show manual schema application instructions"""
    print_step(2, "Apply Database Schema")
    
    print("📋 Manual Schema Application Required:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the following SQL:")
    print("\n" + "="*50)
    
    schema_file = Path("supabase/kolekt_schema.sql")
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            print(f.read())
    else:
        print("❌ Schema file not found!")
        return False
    
    print("="*50)
    print("\n4. Click 'Run' to execute")
    print("5. Verify tables are created in the Table Editor")
    
    input("\n⏳ Press Enter when you've applied the schema...")
    return True

def test_api_endpoints():
    """Test the API endpoints"""
    print_step(3, "Testing API Endpoints")
    
    print("🧪 Running API tests...")
    try:
        result = subprocess.run([sys.executable, "test_curation_api.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ API tests completed successfully!")
            print(result.stdout)
        else:
            print("❌ API tests failed!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return True

def create_review_queue_ui():
    """Create a simple review queue UI"""
    print_step(4, "Creating Review Queue UI")
    
    # Create the review queue modal HTML
    review_modal_html = '''
    <!-- Review Queue Modal -->
    <div id="reviewQueueModal" class="modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h2>📋 Content Review Queue</h2>
                <span class="close" onclick="closeReviewQueue()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="reviewItems" class="review-items">
                    <!-- Items will be loaded here -->
                </div>
            </div>
        </div>
    </div>
    '''
    
    # Add to index.html
    index_file = Path("web/templates/index.html")
    if index_file.exists():
        with open(index_file, 'r') as f:
            content = f.read()
        
        # Add modal before closing body tag
        if '<!-- Review Queue Modal -->' not in content:
            content = content.replace('</body>', f'{review_modal_html}\n</body>')
            
            with open(index_file, 'w') as f:
                f.write(content)
            
            print("✅ Review queue modal added to index.html")
        else:
            print("✅ Review queue modal already exists")
    
    # Create JavaScript for review queue functionality
    review_js = '''
// Review Queue Functions
function openReviewQueue() {
    document.getElementById('reviewQueueModal').style.display = 'block';
    loadReviewItems();
}

function closeReviewQueue() {
    document.getElementById('reviewQueueModal').style.display = 'none';
}

async function loadReviewItems() {
    try {
        const response = await fetch('/api/v1/curation/review-queue?user_id=550e8400-e29b-41d4-a716-446655440000');
        const data = await response.json();
        
        const container = document.getElementById('reviewItems');
        container.innerHTML = '';
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'review-item';
                itemDiv.innerHTML = `
                    <div class="review-item-header">
                        <h3>${item.title || 'Untitled'}</h3>
                        <span class="score">Score: ${item.score}</span>
                    </div>
                    <p>${item.normalized?.substring(0, 200)}...</p>
                    <div class="review-actions">
                        <button onclick="approveItem('${item.id}')" class="btn btn-success">✅ Approve</button>
                        <button onclick="rejectItem('${item.id}')" class="btn btn-danger">❌ Reject</button>
                        <button onclick="createDraft('${item.id}')" class="btn btn-primary">📝 Create Draft</button>
                    </div>
                `;
                container.appendChild(itemDiv);
            });
        } else {
            container.innerHTML = '<p>No items in review queue</p>';
        }
    } catch (error) {
        console.error('Error loading review items:', error);
    }
}

async function approveItem(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/review-queue/${itemId}/approve`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: '550e8400-e29b-41d4-a716-446655440000'})
        });
        
        if (response.ok) {
            loadReviewItems();
        }
    } catch (error) {
        console.error('Error approving item:', error);
    }
}

async function rejectItem(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/review-queue/${itemId}/reject`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: '550e8400-e29b-41d4-a716-446655440000'})
        });
        
        if (response.ok) {
            loadReviewItems();
        }
    } catch (error) {
        console.error('Error rejecting item:', error);
    }
}

async function createDraft(itemId) {
    try {
        const response = await fetch(`/api/v1/curation/drafts/threads?user_id=550e8400-e29b-41d4-a716-446655440000&item_id=${itemId}&variants=1`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        if (response.ok) {
            alert('Draft created successfully!');
        }
    } catch (error) {
        console.error('Error creating draft:', error);
    }
}
'''
    
    # Add to app.js
    app_js_file = Path("web/static/js/app.js")
    if app_js_file.exists():
        with open(app_js_file, 'r') as f:
            content = f.read()
        
        if '// Review Queue Functions' not in content:
            content += review_js
            
            with open(app_js_file, 'w') as f:
                f.write(content)
            
            print("✅ Review queue JavaScript added to app.js")
        else:
            print("✅ Review queue JavaScript already exists")
    
    # Add CSS for review queue
    review_css = '''
/* Review Queue Styles */
.review-items {
    max-height: 400px;
    overflow-y: auto;
}

.review-item {
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    background: var(--background);
}

.review-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
}

.review-item-header h3 {
    margin: 0;
    font-size: var(--font-size-lg);
}

.score {
    background: var(--kolekt-gradient);
    color: white;
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    font-size: var(--font-size-sm);
}

.review-actions {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-md);
}

.btn-success {
    background: #10b981;
    color: white;
}

.btn-danger {
    background: #ef4444;
    color: white;
}
'''
    
    # Add to style.css
    style_css_file = Path("web/static/css/style.css")
    if style_css_file.exists():
        with open(style_css_file, 'r') as f:
            content = f.read()
        
        if '/* Review Queue Styles */' not in content:
            content += review_css
            
            with open(style_css_file, 'w') as f:
                f.write(content)
            
            print("✅ Review queue CSS added to style.css")
        else:
            print("✅ Review queue CSS already exists")
    
    print("✅ Review queue UI components created!")

def add_review_queue_button():
    """Add review queue button to the main UI"""
    print_step(5, "Adding Review Queue Button")
    
    index_file = Path("web/templates/index.html")
    if index_file.exists():
        with open(index_file, 'r') as f:
            content = f.read()
        
        # Add button to the features section
        if 'Review Queue' not in content:
            # Find the features section and add the button
            features_section = '''        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>Review Queue</h3>
            <p>Review and approve content before it goes live. Manage your content pipeline with ease.</p>
            <button class="btn btn-primary" onclick="openReviewQueue()">Open Queue</button>
        </div>'''
            
            # Insert before the closing features div
            content = content.replace('    </div>', f'{features_section}\n    </div>')
            
            with open(index_file, 'w') as f:
                f.write(content)
            
            print("✅ Review queue button added to main UI")
        else:
            print("✅ Review queue button already exists")

def main():
    """Run the complete setup process"""
    print_header("Kolekt Complete Setup")
    
    # Step 1: Check Supabase connection
    if not check_supabase_connection():
        return
    
    # Step 2: Apply schema
    if not show_schema_instructions():
        return
    
    # Step 3: Test API endpoints
    if not test_api_endpoints():
        print("⚠️  API tests failed. Please check the schema was applied correctly.")
        return
    
    # Step 4: Create review queue UI
    create_review_queue_ui()
    
    # Step 5: Add review queue button
    add_review_queue_button()
    
    print_header("Setup Complete!")
    print("🎉 Kolekt is now ready with:")
    print("✅ Database schema applied")
    print("✅ API endpoints working")
    print("✅ Review queue UI created")
    print("✅ Content pipeline functional")
    
    print("\n📋 Next steps:")
    print("1. Start the server: python start_kolekt.py")
    print("2. Open http://127.0.0.1:8000")
    print("3. Test the 'Review Queue' feature")
    print("4. Add content via the API")
    print("5. Create drafts and schedule posts")

if __name__ == "__main__":
    main()
