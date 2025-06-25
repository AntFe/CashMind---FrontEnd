function senhaTemLetraMaiuscula(senha) {
    return /[A-Z]/.test(senha);
}

function senhaTemCaractereEspecial(senha) {
    return /[#%&*!?]/.test(senha);
}

function senhaTemNumero(senha) {
    return /\d/.test(senha);
}

function senhaTemNumerosSequenciais(senha) {
    // Extraí todos os números da senha
    const numeros = senha.match(/\d/g);
    if (!numeros || numeros.length < 2) return false;

    for (let i = 0; i < numeros.length - 1; i++) {
        let atual = parseInt(numeros[i]);
        let proximo = parseInt(numeros[i + 1]);
        if (proximo === atual + 1) {
            return true; // Encontrou sequência
        }
    }
    return false;
}

document.getElementById("signupForm").addEventListener("submit", function (e) {
    e.preventDefault();

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
        document.getElementById('usernameError').style.display = 'block';
        isValid = false;
    }

    // Validar e-mail
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailPattern.test(email)) {
        document.getElementById('emailError').style.display = 'block';
        isValid = false;
    }

    if (
        !password ||
        !senhaTemLetraMaiuscula(password) ||
        !senhaTemCaractereEspecial(password) ||
        !senhaTemNumero(password) ||
        senhaTemNumerosSequenciais(password) || (password.length < 8)
    ) {
        switch (true) {
            case !password:
                senhaErro = "Por favor digite sua senha";
                break;
            case !senhaTemLetraMaiuscula(password):
                senhaErro = "Sua senha deve conter no mínimo uma letra maiúscula";
                break;
            case !senhaTemCaractereEspecial(password):
                senhaErro = "Sua senha deve conter um carectere especial como:(#%&*!?)";
                break;
            case !senhaTemNumero(password):
                senhaErro = "Sua senha deve conter um ou mais números";
                break;
            case senhaTemNumerosSequenciais(password):
                senhaErro = "Sua senha não deve conter números sequênciais";
                break;
            case (password.length < 8):
                senhaErro = "Sua senha deve ter um tamanho mínimo de 8";
                break;
            default:
                senhaErro = "tamanho minimo 8 | A senha deve conter: 1 letra maiúscula, 1 caractere especial (#%&*!?) e 1 número (não sequencial).";
                break;
        }

        passwordError.textContent = senhaErro;
        passwordError.style.display = 'block';
        isValid = false;
    }else{
        alert("Senha válida");
    }


    // Validação da confirmação de senha
    if (password !== confirmPassword || !confirmPassword) {
        document.getElementById('confirmPasswError').style.display = 'block';
        isValid = false;
    }

    // Se todos os campos forem válidos, prosseguir com o cadastro
    if (isValid) {
        document.getElementById('loginForm').reset();
    }

});