// Nota: API_BASE_URL já está definido em auth.js

// Funções de validação
function senhaTemLetraMaiuscula(senha) {
    return /[A-Z]/.test(senha);
}

function senhaTemCaractereEspecial(senha) {
    return /[#%&*!?]/.test(senha);
}

function senhaTemNumero(senha) {
    return /\d/.test(senha);
}

document.getElementById("signupForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Limpa erros anteriores
    document.querySelectorAll(".error").forEach(function (span) {
        span.style.display = "none";
    });

    let isValid = true;
    let senhaErro = "";
    
    // Obter valores dos campos
    const username = document.getElementById('usernameInput').value.trim();
    const email = document.getElementById('nameInput').value.trim();
    const password = document.getElementById('passwInput').value.trim();
    const confirmPassword = document.getElementById('passwConfirm').value.trim();

    // Validar nome completo
    if (!username) {
        document.getElementById('usernameError').innerHTML = "Nome completo é obrigatório";
        document.getElementById('usernameError').style.display = 'block';
        isValid = false;
    }

    // Validar e-mail
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailPattern.test(email)) {
        document.getElementById('emailError').innerHTML = "Insira um email válido";
        document.getElementById('emailError').style.display = 'block';
        isValid = false;
    }

    // Validar senha
    if (
        !password ||
        password.length < 8 ||
        !senhaTemLetraMaiuscula(password) ||
        !senhaTemCaractereEspecial(password) ||
        !senhaTemNumero(password)
    ) {
        switch (true) {
            case !password:
                senhaErro = "Por favor digite sua senha";
                break;
            case password.length < 8:
                senhaErro = "Sua senha deve ter no mínimo 8 caracteres";
                break;
            case !senhaTemLetraMaiuscula(password):
                senhaErro = "Sua senha deve conter no mínimo uma letra maiúscula";
                break;
            case !senhaTemCaractereEspecial(password):
                senhaErro = "Sua senha deve conter um caractere especial como: (#%&*!?)";
                break;
            case !senhaTemNumero(password):
                senhaErro = "Sua senha deve conter um ou mais números";
                break;
            default:
                senhaErro = "Senha inválida";
                break;
        }

        document.getElementById('passwordError').textContent = senhaErro;
        document.getElementById('passwordError').style.display = 'block';
        isValid = false;
    }

    // Validação da confirmação de senha
    if (password !== confirmPassword || !confirmPassword) {
        document.getElementById('confirmPasswError').innerHTML = "As senhas não coincidem";
        document.getElementById('confirmPasswError').style.display = 'block';
        isValid = false;
    }

    // Se todos os campos forem válidos, fazer o cadastro
    if (isValid) {
        try {
            // Mostra loading
            const submitButton = e.target.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Criando conta...';
            submitButton.disabled = true;

            // Envia dados para o backend
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: username,
                    email: email,
                    password: password
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Erro ao criar conta');
            }

            // Armazena os tokens
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('refresh_token', result.refresh_token);
            localStorage.setItem('user', JSON.stringify(result.user));

            console.log('Cadastro realizado com sucesso!');

            // Limpa o formulário
            document.getElementById('signupForm').reset();

            // Mostra mensagem de sucesso e redireciona
            alert('Conta criada com sucesso! Você será redirecionado para o dashboard.');
            
            // Redireciona direto para o dashboard
            window.location.href = 'dashboard.html';

        } catch (error) {
            console.error('Erro ao criar conta:', error);
            
            // Mostra erro genérico
            document.getElementById('usernameError').innerHTML = error.message;
            document.getElementById('usernameError').style.display = 'block';
        } finally {
            // Restaura botão
            const submitButton = e.target.querySelector('button[type="submit"]');
            submitButton.textContent = 'Criar conta';
            submitButton.disabled = false;
        }
    }
});