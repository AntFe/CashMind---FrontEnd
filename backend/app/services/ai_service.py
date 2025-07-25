import os
from datetime import datetime, timedelta
import google.generativeai as genai
from app.models import Transaction, TransactionType

class AIService:
    """Serviço para análise financeira com IA"""
    
    def __init__(self):
        # Configurar API do Gemini
        api_key = os.environ.get('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.enabled = True
        else:
            self.model = None
            self.enabled = False
    
    def analyze_expenses(self, user_id, month=None, year=None):
        """Analisa as despesas do usuário e gera recomendações"""
        
        if not self.enabled:
            return {
                'analysis': 'Análise com IA não disponível. Configure a API Key do Google Gemini.',
                'recommendations': []
            }
        
        # Usar mês atual se não especificado
        if not month or not year:
            now = datetime.now()
            month = month or now.month
            year = year or now.year
        
        # Buscar transações do mês
        from app import db
        transactions = Transaction.query.filter_by(user_id=user_id).filter(
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        ).all()
        
        if not transactions:
            return {
                'analysis': 'Não há transações suficientes para análise neste período.',
                'recommendations': []
            }
        
        # Preparar dados para análise
        analysis_data = self._prepare_analysis_data(transactions, month, year)
        
        # Gerar prompt para o Gemini
        prompt = self._create_analysis_prompt(analysis_data)
        
        try:
            # Fazer a análise com Gemini
            response = self.model.generate_content(prompt)
            
            # Processar resposta
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            print(f"Erro na análise com IA: {str(e)}")
            return {
                'analysis': 'Erro ao gerar análise. Tente novamente mais tarde.',
                'recommendations': []
            }
    
    def _prepare_analysis_data(self, transactions, month, year):
        """Prepara os dados das transações para análise"""
        
        # Calcular totais
        total_income = sum(t.amount for t in transactions if t.transaction_type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in transactions if t.transaction_type == TransactionType.EXPENSE)
        
        # Agrupar despesas por categoria
        expenses_by_category = {}
        for t in transactions:
            if t.transaction_type == TransactionType.EXPENSE:
                if t.category not in expenses_by_category:
                    expenses_by_category[t.category] = 0
                expenses_by_category[t.category] += t.amount
        
        # Separar fixas e variáveis
        fixed_expenses = sum(t.amount for t in transactions 
                           if t.transaction_type == TransactionType.EXPENSE 
                           and t.recurrence_type.value == 'fixed')
        
        variable_expenses = sum(t.amount for t in transactions 
                              if t.transaction_type == TransactionType.EXPENSE 
                              and t.recurrence_type.value == 'variable')
        
        return {
            'month': month,
            'year': year,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'expense_percentage': (total_expense / total_income * 100) if total_income > 0 else 0,
            'fixed_expenses': fixed_expenses,
            'variable_expenses': variable_expenses,
            'expenses_by_category': expenses_by_category,
            'transactions_count': len(transactions)
        }
    
    def _create_analysis_prompt(self, data):
        """Cria o prompt para o Gemini analisar os gastos"""
        
        # Formatar categorias
        categories_text = "\n".join([
            f"- {cat}: R$ {value:.2f} ({value/data['total_expense']*100:.1f}%)" 
            for cat, value in sorted(data['expenses_by_category'].items(), 
                                    key=lambda x: x[1], reverse=True)
        ])
        
        prompt = f"""
        Você é um consultor financeiro pessoal analisando os gastos de um usuário.
        
        Dados do mês {data['month']}/{data['year']}:
        - Receita total: R$ {data['total_income']:.2f}
        - Despesas totais: R$ {data['total_expense']:.2f}
        - Saldo: R$ {data['balance']:.2f}
        - Porcentagem gasta: {data['expense_percentage']:.1f}%
        - Despesas fixas: R$ {data['fixed_expenses']:.2f}
        - Despesas variáveis: R$ {data['variable_expenses']:.2f}
        
        Despesas por categoria:
        {categories_text}
        
        Por favor, forneça:
        1. Uma análise geral da saúde financeira (2-3 parágrafos)
        2. Pontos positivos identificados
        3. Pontos de atenção
        4. 3-5 recomendações específicas e práticas para melhorar as finanças
        
        Seja direto, prático e motivador. Use linguagem simples e amigável.
        Formate a resposta em JSON com as chaves: "analise_geral", "pontos_positivos", "pontos_atencao", "recomendacoes" (array de strings).
        """
        
        return prompt
    
    def _parse_ai_response(self, response_text):
        """Processa a resposta da IA"""
        import json
        
        try:
            # Tentar extrair JSON da resposta
            # O Gemini às vezes retorna com markdown, então vamos limpar
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            data = json.loads(cleaned_response)
            
            return {
                'analysis': data.get('analise_geral', ''),
                'positive_points': data.get('pontos_positivos', ''),
                'attention_points': data.get('pontos_atencao', ''),
                'recommendations': data.get('recomendacoes', [])
            }
            
        except:
            # Se falhar, retornar resposta simples
            return {
                'analysis': response_text,
                'positive_points': '',
                'attention_points': '',
                'recommendations': []
            }
    
    def get_spending_insights(self, user_id):
        """Gera insights rápidos sobre padrões de gastos"""
        
        if not self.enabled:
            return []
        
        # Buscar transações dos últimos 3 meses
        three_months_ago = datetime.now() - timedelta(days=90)
        
        from app import db
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.date >= three_months_ago
        ).all()
        
        if len(transactions) < 10:
            return ["Adicione mais transações para receber insights personalizados"]
        
        # Analisar padrões
        insights = []
        
        # Maior categoria de gasto
        expenses_by_cat = {}
        for t in transactions:
            if t.transaction_type == TransactionType.EXPENSE:
                if t.category not in expenses_by_cat:
                    expenses_by_cat[t.category] = 0
                expenses_by_cat[t.category] += t.amount
        
        if expenses_by_cat:
            top_category = max(expenses_by_cat.items(), key=lambda x: x[1])
            insights.append(f"Sua maior categoria de gastos é '{top_category[0]}' com R$ {top_category[1]:.2f} nos últimos 3 meses")
        
        # Tendência de gastos
        current_month_expenses = sum(
            t.amount for t in transactions 
            if t.transaction_type == TransactionType.EXPENSE 
            and t.date.month == datetime.now().month
        )
        
        last_month_expenses = sum(
            t.amount for t in transactions 
            if t.transaction_type == TransactionType.EXPENSE 
            and t.date.month == (datetime.now().month - 1 or 12)
        )
        
        if last_month_expenses > 0:
            change = ((current_month_expenses - last_month_expenses) / last_month_expenses) * 100
            if change > 10:
                insights.append(f"Seus gastos aumentaram {change:.1f}% em relação ao mês passado")
            elif change < -10:
                insights.append(f"Parabéns! Seus gastos diminuíram {abs(change):.1f}% em relação ao mês passado")
        
        return insights[:3]  # Retornar no máximo 3 insights