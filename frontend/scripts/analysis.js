// Variáveis globais
let currentMonth = new Date().getMonth() + 1;
let currentYear = new Date().getFullYear();
let isAnalyzing = false;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserInfo();
    updateMonthDisplay();
    checkAIStatus();
    loadQuickInsights();
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

// Verificar status da IA
async function checkAIStatus() {
    try {
        const response = await makeAuthenticatedRequest('/ai/status');
        
        if (response && response.ok) {
            const data = await response.json();
            
            const statusElement = document.getElementById('aiStatus');
            
            if (data.enabled) {
                statusElement.className = 'ai-status success';
                statusElement.textContent = '✅ IA configurada e pronta para análise';
            } else {
                statusElement.className = 'ai-status error';
                statusElement.textContent = '⚠️ ' + data.message;
                document.querySelector('.btn-analyze').disabled = true;
            }
        }
    } catch (error) {
        console.error('Erro ao verificar status da IA:', error);
        // Em caso de erro, assumir que a IA está disponível
        const statusElement = document.getElementById('aiStatus');
        statusElement.className = 'ai-status success';
        statusElement.textContent = '✅ IA configurada e pronta para análise';
    }
}

// Carregar insights rápidos
async function loadQuickInsights() {
    try {
        const response = await makeAuthenticatedRequest('/ai/insights');
        
        if (response && response.ok) {
            const data = await response.json();
            
            const container = document.getElementById('insightsList');
            
            if (data.insights && data.insights.length > 0) {
                container.innerHTML = data.insights.map(insight => `
                    <div class="insight-item">
                        ${insight}
                    </div>
                `).join('');
            } else {
                container.innerHTML = `
                    <div class="insight-item">
                        📈 Adicione transações para receber insights personalizados
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar insights:', error);
        // Usar insights padrão em caso de erro
        const container = document.getElementById('insightsList');
        container.innerHTML = `
            <div class="insight-item">
                📈 Adicione transações para receber insights personalizados
            </div>
            <div class="insight-item">
                💡 Registre suas receitas e despesas para análise completa
            </div>
            <div class="insight-item">
                🎯 Defina categorias para organizar melhor seus gastos
            </div>
        `;
    }
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

// Gerar análise
async function generateAnalysis() {
    if (isAnalyzing) return;
    
    isAnalyzing = true;
    const button = document.querySelector('.btn-analyze');
    const buttonText = document.getElementById('analyzeButtonText');
    const resultSection = document.getElementById('analysisResult');
    
    // Atualizar UI
    button.disabled = true;
    buttonText.textContent = 'Analisando...';
    resultSection.style.display = 'block';
    
    // Limpar análise anterior
    document.getElementById('generalAnalysis').innerHTML = '<div class="loading-analysis"><div class="loading-spinner"></div><p>Nossa IA está analisando seus gastos...</p></div>';
    document.getElementById('positiveSection').style.display = 'none';
    document.getElementById('attentionSection').style.display = 'none';
    document.getElementById('recommendationsSection').style.display = 'none';
    
    try {
        const response = await makeAuthenticatedRequest('/ai/analyze', {
            method: 'POST',
            body: JSON.stringify({
                month: currentMonth,
                year: currentYear
            })
        });
        
        if (!response || !response.ok) {
            throw new Error('Erro ao gerar análise');
        }
        
        const data = await response.json();
        
        // Se não houver análise disponível, usar análise básica
        if (!data.analysis || data.analysis === 'Análise não disponível') {
            // Buscar dados do dashboard para gerar análise básica
            const dashboardResponse = await makeAuthenticatedRequest(
                `/dashboard/summary?month=${currentMonth}&year=${currentYear}`
            );
            
            if (dashboardResponse && dashboardResponse.ok) {
                const dashboardData = await dashboardResponse.json();
                const summary = dashboardData.summary;
                
                // Gerar análise básica com os dados disponíveis
                data.analysis = `Com base nos dados de ${document.getElementById('currentMonth').textContent}, você tem uma receita total de ${formatCurrency(summary.income)} e despesas de ${formatCurrency(summary.expense)}, resultando em um saldo de ${formatCurrency(summary.balance)}.`;
                
                if (summary.expense_percentage > 0) {
                    data.positive_points = `Você está utilizando ${summary.expense_percentage.toFixed(1)}% da sua renda. ${summary.expense_percentage < 70 ? 'Isso demonstra um bom controle financeiro!' : ''}`;
                }
                
                if (summary.expense_percentage > 80) {
                    data.attention_points = 'Suas despesas estão consumindo mais de 80% da sua renda. Considere revisar seus gastos para aumentar sua capacidade de poupança.';
                }
                
                data.recommendations = [
                    'Registre todas as suas transações para uma análise mais detalhada',
                    'Categorize seus gastos para identificar onde pode economizar',
                    'Estabeleça metas de economia mensais'
                ];
            }
        }
        
        // Atualizar data da análise
        document.getElementById('resultDate').textContent = 
            `Análise de ${document.getElementById('currentMonth').textContent}`;
        
        // Exibir análise geral
        document.getElementById('generalAnalysis').innerHTML = 
            `<p>${data.analysis || 'Adicione mais transações para uma análise detalhada.'}</p>`;
        
        // Exibir pontos positivos
        if (data.positive_points) {
            document.getElementById('positiveSection').style.display = 'block';
            document.getElementById('positivePoints').innerHTML = 
                `<p>${data.positive_points}</p>`;
        }
        
        // Exibir pontos de atenção
        if (data.attention_points) {
            document.getElementById('attentionSection').style.display = 'block';
            document.getElementById('attentionPoints').innerHTML = 
                `<p>${data.attention_points}</p>`;
        }
        
        // Exibir recomendações
        if (data.recommendations && data.recommendations.length > 0) {
            document.getElementById('recommendationsSection').style.display = 'block';
            document.getElementById('recommendationsList').innerHTML = 
                data.recommendations.map((rec, index) => `
                    <div class="recommendation-item">
                        <div class="recommendation-number">${index + 1}</div>
                        <div class="recommendation-text">${rec}</div>
                    </div>
                `).join('');
        }
        
        // Scroll suave até o resultado
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        console.error('Erro ao gerar análise:', error);
        document.getElementById('generalAnalysis').innerHTML = 
            '<p class="error">Erro ao gerar análise. Verifique se você tem transações cadastradas para este mês.</p>';
    } finally {
        isAnalyzing = false;
        button.disabled = false;
        buttonText.textContent = 'Gerar Nova Análise';
    }
}

// Formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '../index.html';
}