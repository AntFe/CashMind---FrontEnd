// Funções compartilhadas de autenticação

// Fazer requisições autenticadas
async function makeAuthenticatedRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        console.error('Nenhum token encontrado');
        window.location.href = '../index.html';
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

        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Renovar token
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