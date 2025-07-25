// Nota: API_BASE_URL já está definido em auth.js

// Manipula o envio do formulário de login
document.getElementById('loginForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const email = document.getElementById('emailInput').value;
  const password = document.getElementById('passwordInput').value;
  
  const errorHandler = document.getElementById('submitError');
  errorHandler.style.display = "none";

  if (!email || !password) {
    errorHandler.innerHTML = "Preencha todos os campos";
    errorHandler.style.display = "block";
    return;
  }

  try {
    // Mostra loading
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