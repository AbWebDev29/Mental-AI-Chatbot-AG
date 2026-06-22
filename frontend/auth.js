// Looks for the variable injected by your environment, otherwise falls back to localhost
const API_BASE_URL = (typeof process !== 'undefined' && process.env.VITE_API_BASE_URL) 
  ? process.env.VITE_API_BASE_URL 
  : (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
      ? "http://localhost:10000" 
      : "https://mirraai-ln7e.onrender.com");
function getUser() {
  return {
    id: localStorage.getItem('user_id'),
    name: localStorage.getItem('user_name') || 'Friend',
    email: localStorage.getItem('user_email') || ''
  };
}
function isLoggedIn() { return !!localStorage.getItem('user_id'); }
function logout() {
  // Save avatar before clearing so it restores on next login
  const email = localStorage.getItem('user_email');
  const avatar = localStorage.getItem('user_avatar');
  if (email && avatar) localStorage.setItem('saved_avatar_' + email, avatar);
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_name');
  localStorage.removeItem('user_email');
  window.location.href = 'index.html';
}
function getInitial(name) { return (name || 'F').charAt(0).toUpperCase(); }
function injectProfileDropdown() {
  const existing = document.getElementById('profileDropdown');
  if (existing) existing.remove();
  const dropdown = document.createElement('div');
  dropdown.id = 'profileDropdown';
  dropdown.style.cssText = 'position:fixed;top:68px;right:40px;width:240px;background:rgba(255,255,255,0.92);backdrop-filter:blur(20px);border:1.5px solid rgba(255,255,255,0.85);border-radius:20px;box-shadow:0 16px 48px rgba(180,120,160,0.22);z-index:9999;overflow:hidden;';
  const user = getUser();
  const savedAvatar = localStorage.getItem('user_avatar');
  const avatarHtml = (savedAvatar && (savedAvatar.startsWith('data:image') || savedAvatar.startsWith('http')))
    ? `<img src="${savedAvatar}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;flex-shrink:0;">`
    : `<div class="pd-avatar">${savedAvatar || getInitial(user.name)}</div>`;
  dropdown.innerHTML = `<style>.pd-header{padding:20px;background:linear-gradient(135deg,rgba(249,168,212,0.25),rgba(192,132,252,0.2));border-bottom:1px solid rgba(255,255,255,0.7);display:flex;align-items:center;gap:12px}.pd-avatar{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#f9a8d4,#c084fc);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white;font-family:'Outfit',sans-serif;flex-shrink:0}.pd-name{font-family:'Outfit',sans-serif;font-weight:600;font-size:0.95rem;color:#4a3a5c}.pd-email{font-family:'Outfit',sans-serif;font-size:0.75rem;color:#b0a0c0;margin-top:2px}.pd-menu{padding:8px}.pd-item{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:12px;font-family:'Outfit',sans-serif;font-size:0.87rem;color:#7a6a8c;cursor:pointer;transition:all 0.18s ease;text-decoration:none}.pd-item:hover{background:rgba(249,168,212,0.18);color:#4a3a5c}.pd-divider{height:1px;background:rgba(180,120,160,0.12);margin:4px 8px}.pd-logout{color:#e07a7a!important}.pd-logout:hover{background:rgba(224,122,122,0.1)!important}</style><div class="pd-header">${avatarHtml}<div><div class="pd-name">${user.name}</div><div class="pd-email">${user.email||'Mirra AI User'}</div></div></div><div class="pd-menu"><a href="profile.html" class="pd-item">👤 My Profile</a><a href="chat.html" class="pd-item">💬 My Chats</a><div class="pd-divider"></div><div class="pd-item pd-logout" onclick="logout()">🚪 Sign Out</div></div>`;
  document.body.appendChild(dropdown);
  setTimeout(() => {
    document.addEventListener('click', function closeDropdown(e) {
      const profile = document.querySelector('.navbar-profile');
      if (!dropdown.contains(e.target) && e.target !== profile) {
        dropdown.remove();
        document.removeEventListener('click', closeDropdown);
      }
    });
  }, 10);
}
function updateNavbar() {
  const profileBtn = document.querySelector('.navbar-profile');
  const signinLink = document.querySelector('.navbar-links a[href="signin.html"]');
  if (!profileBtn) return;
  if (isLoggedIn()) {
    const user = getUser();
    const savedAvatar = localStorage.getItem('user_avatar');
    if (savedAvatar && (savedAvatar.startsWith('data:image') || savedAvatar.startsWith('http'))) {
      profileBtn.innerHTML = `<img src="${savedAvatar}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;">`;
      profileBtn.style.background = 'none';
      profileBtn.style.padding = '0';
      profileBtn.style.overflow = 'hidden';
    } else {
      profileBtn.textContent = savedAvatar || getInitial(user.name);
      profileBtn.style.background = 'linear-gradient(135deg,#f9a8d4,#c084fc)';
      profileBtn.style.color = 'white';
      profileBtn.style.fontWeight = '700';
      profileBtn.style.fontSize = '15px';
      profileBtn.style.overflow = '';
    }
    if (signinLink) { signinLink.style.display = 'none'; }
    profileBtn.onclick = (e) => { e.stopPropagation(); const ex = document.getElementById('profileDropdown'); if (ex) { ex.remove(); return; } injectProfileDropdown(); };
  } else {
    profileBtn.innerHTML = '👤';
    profileBtn.style.background = '';
    profileBtn.style.overflow = '';
    profileBtn.onclick = () => window.location.href = 'signin.html';
  }
}
<<<<<<< HEAD

function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = saved === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
}

function injectThemeToggle() {
  if (document.getElementById('themeToggle')) return;
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  const btn = document.createElement('button');
  btn.id = 'themeToggle';
  btn.className = 'theme-toggle';
  btn.textContent = '🌙';
  btn.onclick = toggleTheme;
  const profile = navbar.querySelector('.navbar-profile');
  if (profile) navbar.insertBefore(btn, profile);
}

document.addEventListener('DOMContentLoaded', () => { initTheme(); injectThemeToggle(); updateNavbar(); });
=======
document.addEventListener('DOMContentLoaded', updateNavbar);

// Authentication helper functions using API_BASE_URL
async function handleSignIn(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/signin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Sign in failed');

  localStorage.setItem('user_id', data.user_id);
  localStorage.setItem('user_name', data.full_name || 'Friend');
  localStorage.setItem('user_email', email);
  return data;
}

async function handleSignUp(email, password, full_name) {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name })
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Sign up failed');

  // Optionally store user info or prompt to sign in
  localStorage.setItem('user_id', data.user_id);
  localStorage.setItem('user_name', full_name || 'Friend');
  localStorage.setItem('user_email', email);
  return data;
}

// Expose helpers globally for inline HTML scripts
window.handleSignIn = handleSignIn;
window.handleSignUp = handleSignUp;
>>>>>>> 6baa45fc7117179ed2a67591c923ad4a10cf1f48
