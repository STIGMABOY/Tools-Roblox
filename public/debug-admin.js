// debug-admin.js - Debug utilities for admin panel
(function() {
    console.log('🔧 Admin Debug Tools Loaded');
    
    // Add debug button to login page
    function addDebugButton() {
        const loginForm = document.querySelector('.login-form');
        if (!loginForm) return;
        
        const debugBtn = document.createElement('button');
        debugBtn.innerHTML = '<i class="fas fa-bug"></i> Debug Login';
        debugBtn.style.cssText = `
            margin-top: 10px;
            padding: 8px 16px;
            background: #f39c12;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        `;
        
        debugBtn.onclick = async function() {
            console.group('🔍 DEBUG LOGIN');
            
            const username = document.getElementById('adminUsername').value;
            const password = document.getElementById('adminPassword').value;
            
            console.log('Username:', username);
            console.log('Password length:', password.length);
            console.log('Full URL:', window.location.href);
            
            try {
                // Test 1: Check API endpoint
                console.log('\n1. Testing API endpoint...');
                const testRes = await fetch('/api/admin/login', { method: 'GET' });
                console.log('GET Status:', testRes.status, testRes.statusText);
                
                // Test 2: Try login
                console.log('\n2. Attempting login...');
                const loginRes = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                console.log('POST Status:', loginRes.status, loginRes.statusText);
                
                const text = await loginRes.text();
                console.log('Raw Response:', text);
                
                try {
                    const json = JSON.parse(text);
                    console.log('Parsed JSON:', json);
                } catch(e) {
                    console.log('Not valid JSON');
                }
                
            } catch(error) {
                console.error('Error:', error);
            }
            
            console.groupEnd();
            
            // Show alert with summary
            alert('Check console (F12) for debug info');
        };
        
        loginForm.appendChild(debugBtn);
    }
    
    // Auto-fill for testing
    function addTestCredentials() {
        const testBtn = document.createElement('button');
        testBtn.innerHTML = '<i class="fas fa-vial"></i> Fill Test Credentials';
        testBtn.style.cssText = `
            margin-top: 5px;
            padding: 6px 12px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            width: 100%;
        `;
        
        testBtn.onclick = function() {
            document.getElementById('adminUsername').value = 'admin';
            document.getElementById('adminPassword').value = 'admin12345';
            console.log('✅ Test credentials filled');
        };
        
        const loginForm = document.querySelector('.login-form');
        if (loginForm) {
            loginForm.appendChild(testBtn);
        }
    }
    
    // Run when page loads
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            addDebugButton();
            addTestCredentials();
            console.log('✅ Debug tools installed');
        }, 1000);
    });
})();
