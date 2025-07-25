// Variáveis globais
let allTransactions = [];
let filteredTransactions = [];
let editingTransactionId = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserInfo();
    loadTransactions();
    loadCategories();
    setupDefaultDate();
});

// Verificar autenticação
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '../index.html';
        return;
    }
}

// Carregar informações do usuário
function loadUserInfo() {
    try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const userName = user.full_name || user.name || user.email || 'Usuário';
        document.getElementById('userName').textContent = userName;
    } catch (error) {
        console.error('Erro ao carregar informações do usuário:', error);
        document.getElementById('userName').textContent = 'Usuário';
    }
}

// Configurar data padrão (hoje)
function setupDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('transactionDate').value = today;
    
    // Configurar filtro de mês para o mês atual
    const currentMonth = today.substring(0, 7);
    document.getElementById('filterMonth').value = currentMonth;
}

// Carregar transações
async function loadTransactions() {
    try {
        const response = await makeAuthenticatedRequest('/transactions/');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar transações');
        }
        
        const data = await response.json();
        allTransactions = data.transactions || [];
        
        filterTransactions();
        
    } catch (error) {
        console.error('Erro ao carregar transações:', error);
        allTransactions = [];
        filterTransactions();
    }
}

// Carregar categorias
async function loadCategories() {
    try {
        const response = await makeAuthenticatedRequest('/transactions/categories');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar categorias');
        }
        
        const data = await response.json();
        const categories = data.categories || [];
        
        const filterSelect = document.getElementById('filterCategory');
        filterSelect.innerHTML = '<option value="">Todas as categorias</option>' +
            categories.map(cat => 
                `<option value="${cat}">${cat}</option>`
            ).join('');
        
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
        // Usar categorias padrão em caso de erro
        const defaultCategories = ['Salário', 'Freelance', 'Alimentação', 'Transporte', 
                                  'Moradia', 'Lazer', 'Saúde', 'Educação', 'Outros'];
        
        const filterSelect = document.getElementById('filterCategory');
        filterSelect.innerHTML = '<option value="">Todas as categorias</option>' +
            defaultCategories.map(cat => 
                `<option value="${cat}">${cat}</option>`
            ).join('');
    }
}

// Filtrar transações
function filterTransactions() {
    const typeFilter = document.getElementById('filterType').value;
    const categoryFilter = document.getElementById('filterCategory').value;
    const monthFilter = document.getElementById('filterMonth').value;
    const searchFilter = document.getElementById('searchInput').value.toLowerCase();
    
    filteredTransactions = allTransactions.filter(transaction => {
        // Filtro de tipo
        if (typeFilter && transaction.type !== typeFilter) {
            return false;
        }
        
        // Filtro de categoria
        if (categoryFilter && transaction.category !== categoryFilter) {
            return false;
        }
        
        // Filtro de mês
        if (monthFilter) {
            const transactionMonth = transaction.date.substring(0, 7);
            if (transactionMonth !== monthFilter) {
                return false;
            }
        }
        
        // Filtro de busca
        if (searchFilter) {
            const searchableText = `${transaction.name} ${transaction.category} ${transaction.description || ''}`.toLowerCase();
            if (!searchableText.includes(searchFilter)) {
                return false;
            }
        }
        
        return true;
    });
    
    renderTransactions();
}

// Renderizar transações
function renderTransactions() {
    const tbody = document.getElementById('transactionsTableBody');
    const count = document.getElementById('transactionCount');
    
    count.textContent = `${filteredTransactions.length} transações`;
    
    if (filteredTransactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">Nenhuma transação encontrada</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredTransactions.map(transaction => `
        <tr>
            <td class="transaction-date">${formatDate(transaction.date)}</td>
            <td class="transaction-name">${transaction.name}</td>
            <td><span class="category-badge">${transaction.category}</span></td>
            <td>
                <span class="type-badge ${transaction.type}">
                    ${transaction.type === 'income' ? 'Receita' : 'Despesa'}
                </span>
            </td>
            <td class="transaction-value ${transaction.type}">
                ${transaction.type === 'income' ? '+' : '-'} ${formatCurrency(transaction.amount)}
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editTransaction(${transaction.id})">
                        ✏️
                    </button>
                    <button class="action-btn delete" onclick="deleteTransaction(${transaction.id})">
                        🗑️
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Abrir modal de transação
function openTransactionModal() {
    editingTransactionId = null;
    document.getElementById('modalTitle').textContent = 'Nova Transação';
    document.getElementById('submitButtonText').textContent = 'Adicionar';
    document.getElementById('transactionForm').reset();
    setupDefaultDate();
    document.getElementById('transactionModal').classList.add('active');
}

// Fechar modal de transação
function closeTransactionModal() {
    document.getElementById('transactionModal').classList.remove('active');
    document.getElementById('transactionForm').reset();
    editingTransactionId = null;
}

// Atualizar estilo do modal baseado no tipo
function updateModalStyle() {
    const type = document.getElementById('transactionType').value;
    const modalContent = document.querySelector('.modal-content');
    
    modalContent.classList.remove('income', 'expense');
    if (type) {
        modalContent.classList.add(type);
    }
}

// Salvar transação
async function saveTransaction(event) {
    event.preventDefault();
    
    const transactionData = {
        name: document.getElementById('transactionName').value,
        amount: parseFloat(document.getElementById('transactionAmount').value),
        date: document.getElementById('transactionDate').value,
        type: document.getElementById('transactionType').value,
        recurrence: 'variable', // O backend espera 'recurrence', não usado na UI
        category: document.getElementById('transactionCategory').value,
        description: document.getElementById('transactionDescription').value
    };
    
    try {
        let response;
        
        if (editingTransactionId) {
            // Editar transação existente
            response = await makeAuthenticatedRequest(`/transactions/${editingTransactionId}`, {
                method: 'PUT',
                body: JSON.stringify(transactionData)
            });
        } else {
            // Criar nova transação
            response = await makeAuthenticatedRequest('/transactions/', {
                method: 'POST',
                body: JSON.stringify(transactionData)
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao salvar transação');
        }
        
        closeTransactionModal();
        await loadTransactions(); // Recarregar transações
        
        // Mostrar mensagem de sucesso
        alert(editingTransactionId ? 'Transação atualizada!' : 'Transação criada!');
        
    } catch (error) {
        console.error('Erro ao salvar transação:', error);
        alert(error.message);
    }
}

// Editar transação
function editTransaction(id) {
    const transaction = allTransactions.find(t => t.id === id);
    if (!transaction) return;
    
    editingTransactionId = id;
    
    // Preencher o formulário
    document.getElementById('modalTitle').textContent = 'Editar Transação';
    document.getElementById('submitButtonText').textContent = 'Salvar';
    document.getElementById('transactionName').value = transaction.name;
    document.getElementById('transactionAmount').value = transaction.amount;
    document.getElementById('transactionDate').value = transaction.date;
    document.getElementById('transactionType').value = transaction.type;
    document.getElementById('transactionCategory').value = transaction.category;
    document.getElementById('transactionDescription').value = transaction.description || '';
    
    updateModalStyle();
    document.getElementById('transactionModal').classList.add('active');
}

// Deletar transação
async function deleteTransaction(id) {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) return;
    
    try {
        const response = await makeAuthenticatedRequest(`/transactions/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erro ao deletar transação');
        }
        
        await loadTransactions(); // Recarregar transações
        alert('Transação excluída com sucesso!');
        
    } catch (error) {
        console.error('Erro ao deletar transação:', error);
        alert('Erro ao deletar transação');
    }
}

// Formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Formatar data
function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '../index.html';
}

// Tornar funções acessíveis globalmente
window.openTransactionModal = openTransactionModal;
window.closeTransactionModal = closeTransactionModal;
window.saveTransaction = saveTransaction;
window.editTransaction = editTransaction;
window.deleteTransaction = deleteTransaction;
window.filterTransactions = filterTransactions;
window.updateModalStyle = updateModalStyle;