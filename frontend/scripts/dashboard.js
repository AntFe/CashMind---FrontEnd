// Variáveis globais
let currentMonth = new Date().getMonth() + 1;
let currentYear = new Date().getFullYear();
let categoryChart = null;
let trendChart = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserInfo();
    loadDashboardData();
    updateMonthDisplay();
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

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '../index.html';
}

// Mudar mês
function changeMonth(direction) {
    currentMonth += direction;
    
    if (currentMonth > 12) {
        currentMonth = 1;
        currentYear++;
    } else if (currentMonth < 1) {
        currentMonth = 12;
        currentYear--;
    }
    
    updateMonthDisplay();
    loadDashboardData();
}

// Atualizar display do mês
function updateMonthDisplay() {
    const months = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    document.getElementById('currentMonth').textContent = 
        `${months[currentMonth - 1]} ${currentYear}`;
}

// Carregar dados do dashboard
async function loadDashboardData() {
    try {
        const response = await makeAuthenticatedRequest(
            `/dashboard/analytics?month=${currentMonth}&year=${currentYear}`
        );

        if (!response.ok) {
            throw new Error('Erro ao carregar dados');
        }

        const data = await response.json();
        
        // Atualizar cards de resumo
        updateSummaryCards(data.summary);
        
        // Atualizar gráficos
        updateCategoryChart(data.expenses_by_category);
        updateTrendChart(data.monthly_trend);
        
        // Atualizar transações recentes
        updateRecentTransactions(data.recent_transactions);
        
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        // Se não houver dados, mostrar valores zerados
        updateSummaryCards({ income: 0, expense: 0, balance: 0 });
        updateCategoryChart([]);
        updateTrendChart([]);
        updateRecentTransactions([]);
    }
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    document.getElementById('totalIncome').textContent = formatCurrency(summary.income);
    document.getElementById('totalExpense').textContent = formatCurrency(summary.expense);
    document.getElementById('balance').textContent = formatCurrency(summary.balance);
    
    // Atualizar barra de saldo
    const balanceFill = document.getElementById('balanceFill');
    const percentage = summary.income > 0 ? (summary.expense / summary.income) * 100 : 0;
    balanceFill.style.width = `${Math.min(percentage, 100)}%`;
    
    // Mudar cor baseado na porcentagem
    if (percentage > 80) {
        balanceFill.style.backgroundColor = '#E74C3C';
    } else if (percentage > 60) {
        balanceFill.style.backgroundColor = '#F39C12';
    } else {
        balanceFill.style.backgroundColor = '#27AE60';
    }
}

// Atualizar gráfico de categorias
function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    // Se não houver dados, mostrar mensagem
    if (!categories || categories.length === 0) {
        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Sem dados'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#666666']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        return;
    }
    
    const labels = categories.map(c => c.category);
    const data = categories.map(c => c.amount);
    const backgroundColors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#9B59B6', '#F39C12', '#E74C3C', '#95A5A6'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#999',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Atualizar gráfico de tendência
function updateTrendChart(monthlyData) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    // Se não houver dados, mostrar gráfico vazio
    if (!monthlyData || monthlyData.length === 0) {
        const emptyLabels = ['Sem dados'];
        const emptyData = [0];
        
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: emptyLabels,
                datasets: [{
                    label: 'Sem transações',
                    data: emptyData,
                    borderColor: '#666666',
                    backgroundColor: 'rgba(102, 102, 102, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        return;
    }
    
    const labels = monthlyData.map(d => `${d.month}/${d.year}`);
    const incomeData = monthlyData.map(d => d.income);
    const expenseData = monthlyData.map(d => d.expense);
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Receitas',
                data: incomeData,
                borderColor: '#27AE60',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.4
            }, {
                label: 'Despesas',
                data: expenseData,
                borderColor: '#E74C3C',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#999'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#3B3B3B'
                    },
                    ticks: {
                        color: '#999'
                    }
                },
                x: {
                    grid: {
                        color: '#3B3B3B'
                    },
                    ticks: {
                        color: '#999'
                    }
                }
            }
        }
    });
}

// Atualizar transações recentes
function updateRecentTransactions(transactions) {
    const container = document.getElementById('recentTransactionsList');
    
    if (transactions.length === 0) {
        container.innerHTML = '<p class="loading-text">Nenhuma transação encontrada</p>';
        return;
    }
    
    container.innerHTML = transactions.map(transaction => `
        <div class="transaction-item">
            <div class="transaction-info">
                <div class="transaction-icon ${transaction.type}">
                    ${transaction.type === 'income' ? '↑' : '↓'}
                </div>
                <div class="transaction-details">
                    <h4>${transaction.name}</h4>
                    <p>${transaction.category} • ${formatDate(transaction.date)}</p>
                </div>
            </div>
            <div class="transaction-amount ${transaction.type}">
                ${transaction.type === 'income' ? '+' : '-'} ${formatCurrency(transaction.amount)}
            </div>
        </div>
    `).join('');
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