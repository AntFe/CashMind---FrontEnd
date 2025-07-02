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

  // Manipula o envio do formulário
  document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const email = document.getElementById('nameInput').value;
    const password = document.getElementById('passwInput').value;
    
    const errorHandler = document.getElementById('submitError');
  
    if(!email || !password){
      errorHandler.innerHTML = "Preencha os campos corretamente";
      errorHandler.style.display = "block";
      return;
    }

    try {
      // Comente a linha abaixo se quiser enviar a senha em texto puro
      //   const hashedPassword = await generateSHA256Hash(password);
      
      // Dados para enviar ao backend
      const data = {
        email: email,
        password: password
      };

      // Envia os dados para o backend
      const response = await fetch('https://seu-backend.com/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error('Erro na autenticação');
      }

      const result = await response.json();
      const token = result.token; // Assume que o backend retorna o JWT

      // Armazena o JWT no localStorage (use HttpOnly cookies em produção)
      localStorage.setItem('jwt', token);

     // retirar essa linha em Release
      console.log('Login bem-sucedido! JWT:', token);

      // Limpa o formulário
      document.getElementById('loginForm').reset();

      // (Descomentar) redireciona para outra página
      // window.location.href = '/dashboard';
    } catch (error) {
      // retirar em Release
        console.error('Erro ao fazer login:', error);
        errorHandler.innerHTML = "Login e senha estão incorretos";
        
    }
  });

  // Função para fazer requisições autenticadas
  async function makeAuthenticatedRequest() {
    const token = localStorage.getItem('jwt');
    if (!token) {
      console.error('Nenhum token encontrado');
    //   window.location.href = '/login'
      return;
    }

    try {
      const response = await fetch('https://seu-backend.com/api/protected', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Acesso não autorizado, Faça login para continuar');
      }

      /// Retirar em release
      const data = await response.json();
      console.log('Dados protegidos:', data);
    } catch (error) {
      console.error('Erro na requisição:', error);
    }
  }