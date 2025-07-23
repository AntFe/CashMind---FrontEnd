//  // Função para converter string em array de bytes (opcional, para hash)
//  async function stringToArrayBuffer(str) {
//     return new TextEncoder().encode(str);
//   }

//   // Função para gerar hash SHA-256 (opcional)
//   async function generateSHA256Hash(message) {
//     const msgBuffer = await stringToArrayBuffer(message);
//     const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
//     const hashArray = Array.from(new Uint8Array(hashBuffer));
//     const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
//     return hashHex;
//   }

// Configuração da API
const API_BASE_URL = 'http://localhost:5000/api';

// Manipula o envio do formulário de login
document.getElementById('loginForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const email = document.getElementById('nameInput').value;
  const password = document.getElementById('passwInput').value;
  
  const errorHandler = document.getElementById('submitError');
  errorHandler.style.display = "none";

  if (!email || !password) {
    errorHandler.innerHTML = "Preencha todos os campos";
    errorHandler.style.display = "block";
    return;
  }

  try {
    // Mostra loading (opcional)
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Entrando...';
    submitButton.disabled = true;

    // Envia os dados para o backend
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || 'Erro na autenticação');
    }

    // Armazena os tokens
    localStorage.setItem('access_token', result.access_token);
    localStorage.setItem('refresh_token', result.refresh_token);
    localStorage.setItem('user', JSON.stringify(result.user));

    console.log('Login bem-sucedido!');

    // Limpa o formulário
    document.getElementById('loginForm').reset();

    // Redireciona para o dashboard
    window.location.href = '../pages/dashboard.html';

  } catch (error) {
    console.error('Erro ao fazer login:', error);
    errorHandler.innerHTML = error.message || "Email ou senha incorretos";
    errorHandler.style.display = "block";
  } finally {
    // Restaura botão
    const submitButton = event.target.querySelector('button[type="submit"]');
    submitButton.textContent = 'Entrar';
    submitButton.disabled = false;
  }
});

// Função para fazer requisições autenticadas
async function makeAuthenticatedRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    console.error('Nenhum token encontrado');
    window.location.href = '/index.html';
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (response.status === 401) {
      // Token expirado, tentar renovar
      const refreshed = await refreshToken();
      if (refreshed) {
        // Tentar novamente com novo token
        return makeAuthenticatedRequest(endpoint, options);
      } else {
        // Falha ao renovar, fazer logout
        logout();
        return;
      }
    }

    if (!response.ok) {
      throw new Error('Erro na requisição');
    }

    return await response.json();
  } catch (error) {
    console.error('Erro na requisição:', error);
    throw error;
  }
}

// Função para renovar token
async function refreshToken() {
  const refresh_token = localStorage.getItem('refresh_token');
  
  if (!refresh_token) {
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refresh_token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return false;
    }

    const result = await response.json();
    localStorage.setItem('access_token', result.access_token);
    return true;
  } catch (error) {
    console.error('Erro ao renovar token:', error);
    return false;
  }
}

// Função de logout
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.location.href = '/index.html';
}