import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import os

class FraudDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Card Fraud Detection System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f4f8')
        
        # Data storage
        self.transactions = []
        self.stats = {'total': 0, 'fraud': 0, 'safe': 0}
        self.data_file = 'fraud_transactions.json'
        
        # Load existing data
        self.load_transactions()
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f4f8')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🛡️ Real-Time Credit Card Fraud Detection System",
                               font=('Arial', 18, 'bold'), bg='white', fg='#2563eb', pady=15)
        title_label.pack()
        
        # Statistics Dashboard
        stats_frame = tk.Frame(main_frame, bg='#f0f4f8')
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_stat_card(stats_frame, "Total Transactions", self.stats['total'], '#3b82f6', 0)
        self.create_stat_card(stats_frame, "Fraudulent", self.stats['fraud'], '#ef4444', 1)
        self.create_stat_card(stats_frame, "Safe", self.stats['safe'], '#10b981', 2)
        
        # Main content area (two columns)
        content_frame = tk.Frame(main_frame, bg='#f0f4f8')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Input Form
        self.create_input_form(content_frame)
        
        # Right column - Transaction History
        self.create_transaction_history(content_frame)
        
    def create_stat_card(self, parent, title, value, color, column):
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        card.grid(row=0, column=column, padx=5, sticky='ew')
        parent.columnconfigure(column, weight=1)
        
        title_label = tk.Label(card, text=title, font=('Arial', 10), bg='white', fg='#6b7280')
        title_label.pack(pady=(10, 0))
        
        value_label = tk.Label(card, text=str(value), font=('Arial', 24, 'bold'), 
                              bg='white', fg=color)
        value_label.pack(pady=(0, 10))
        
        # Store reference for updating
        if title == "Total Transactions":
            self.total_label = value_label
        elif title == "Fraudulent":
            self.fraud_label = value_label
        else:
            self.safe_label = value_label
            
    def create_input_form(self, parent):
        form_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Title
        title = tk.Label(form_frame, text="Enter Transaction Details", 
                        font=('Arial', 14, 'bold'), bg='white', fg='#1f2937')
        title.pack(pady=10)
        
        # Scrollable form
        canvas = tk.Canvas(form_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        self.entries = {}
        
        fields = [
            ('Transaction ID', 'transaction_id', 'text', 'Auto-generated if empty'),
            ('Amount ($) *', 'amount', 'number', '0.00'),
            ('Card ID *', 'card_id', 'text', '****1234'),
            ('Merchant Name *', 'merchant_name', 'text', 'Store Name'),
            ('Merchant Category', 'merchant_category', 'combo', 
             ['Retail', 'Restaurant', 'Gas', 'Grocery', 'Entertainment', 'Travel', 'Online', 'Other']),
            ('Hour (0-23)', 'hour', 'number', str(datetime.now().hour)),
            ('Distance from Home (km)', 'distance_home', 'number', '0'),
            ('Distance from Last TX (km)', 'distance_last', 'number', '0'),
            ('Time Since Last TX (min)', 'time_since_last', 'number', '0'),
            ('TX Count (1 hour)', 'tx_count_1h', 'number', '1'),
            ('Avg Amount 7 Days ($)', 'avg_amount_7d', 'number', '0'),
            ('Card Present', 'card_present', 'combo', ['Yes', 'No']),
            ('Online Transaction', 'online_transaction', 'combo', ['No', 'Yes'])
        ]
        
        for label_text, field_name, field_type, default in fields:
            frame = tk.Frame(scrollable_frame, bg='white')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            label = tk.Label(frame, text=label_text, font=('Arial', 9), 
                           bg='white', fg='#374151', anchor='w')
            label.pack(fill=tk.X)
            
            if field_type == 'combo':
                widget = ttk.Combobox(frame, values=default, state='readonly')
                widget.set(default[0] if isinstance(default, list) else default)
            else:
                widget = tk.Entry(frame, font=('Arial', 10))
                widget.insert(0, default)
            
            widget.pack(fill=tk.X, ipady=5)
            self.entries[field_name] = widget
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Submit button
        submit_btn = tk.Button(form_frame, text="🛡️ Analyze Transaction", 
                              font=('Arial', 12, 'bold'), bg='#2563eb', fg='white',
                              relief=tk.RAISED, bd=0, pady=10, cursor='hand2',
                              command=self.analyze_transaction)
        submit_btn.pack(fill=tk.X, padx=20, pady=10)
        
    def create_transaction_history(self, parent):
        history_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Title bar
        title_bar = tk.Frame(history_frame, bg='white')
        title_bar.pack(fill=tk.X, pady=10, padx=10)
        
        title = tk.Label(title_bar, text="Recent Transactions", 
                        font=('Arial', 14, 'bold'), bg='white', fg='#1f2937')
        title.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(title_bar, text="Clear History", 
                             font=('Arial', 9), bg='#ef4444', fg='white',
                             relief=tk.FLAT, cursor='hand2',
                             command=self.clear_history)
        clear_btn.pack(side=tk.RIGHT)
        
        # History display
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                       font=('Courier', 9),
                                                       bg='#f9fafb', relief=tk.FLAT)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Display existing transactions
        self.refresh_history_display()
        
    def calculate_fraud_score(self, data):
        score = 0
        reasons = []
        
        try:
            amount = float(data.get('amount', 0))
            hour = int(data.get('hour', 12))
            distance_home = float(data.get('distance_home', 0))
            distance_last = float(data.get('distance_last', 0))
            time_since_last = float(data.get('time_since_last', 0))
            tx_count = int(data.get('tx_count_1h', 1))
            avg_amount = float(data.get('avg_amount_7d', 100))
            card_present = data.get('card_present', 'Yes')
            online = data.get('online_transaction', 'No')
            
            # High amount
            if amount > 1000:
                score += 25
                reasons.append('High transaction amount')
            
            # Unusual time
            if hour < 6 or hour > 23:
                score += 15
                reasons.append('Unusual transaction time (late night/early morning)')
            
            # Distance from home
            if distance_home > 100:
                score += 20
                reasons.append('Transaction far from home location')
            
            # Quick successive transactions
            if time_since_last < 5 and time_since_last > 0:
                score += 15
                reasons.append('Rapid successive transactions')
            
            # Multiple transactions
            if tx_count >= 3:
                score += 10
                reasons.append('Multiple transactions in 1 hour')
            
            # Distance from last transaction
            if distance_last > 50:
                score += 10
                reasons.append('Large distance from last transaction')
            
            # Card not present
            if card_present == 'No':
                score += 10
                reasons.append('Card not physically present')
            
            # Online transaction
            if online == 'Yes':
                score += 5
                reasons.append('Online transaction')
            
            # Amount deviation
            if avg_amount > 0 and amount > avg_amount * 3:
                score += 20
                reasons.append('Amount significantly higher than usual')
                
        except ValueError:
            pass
        
        return min(score, 100), reasons
    
    def assess_risk(self, score):
        if score >= 70:
            return {'level': 'HIGH', 'action': 'BLOCK', 'color': '#ef4444'}
        elif score >= 50:
            return {'level': 'MEDIUM', 'action': 'REVIEW', 'color': '#f97316'}
        elif score >= 30:
            return {'level': 'LOW', 'action': 'MONITOR', 'color': '#eab308'}
        else:
            return {'level': 'MINIMAL', 'action': 'APPROVE', 'color': '#10b981'}
    
    def analyze_transaction(self):
        # Get form data
        data = {}
        for field_name, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                data[field_name] = widget.get()
            else:
                data[field_name] = widget.get()
        
        # Validate required fields
        if not data.get('amount') or not data.get('card_id') or not data.get('merchant_name'):
            messagebox.showerror("Error", "Please fill in all required fields:\n- Amount\n- Card ID\n- Merchant Name")
            return
        
        # Calculate fraud score
        score, reasons = self.calculate_fraud_score(data)
        risk = self.assess_risk(score)
        is_fraud = score >= 50
        
        # Create transaction record
        transaction = {
            'id': data['transaction_id'] if data['transaction_id'] else f"TX{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'amount': float(data.get('amount', 0)),
            'card_id': data['card_id'],
            'merchant_name': data['merchant_name'],
            'merchant_category': data['merchant_category'],
            'result': {
                'is_fraud': is_fraud,
                'fraud_probability': score / 100,
                'risk_level': risk['level'],
                'recommended_action': risk['action'],
                'risk_color': risk['color'],
                'reasons': reasons
            }
        }
        
        # Add to transactions
        self.transactions.insert(0, transaction)
        
        # Update statistics
        self.stats['total'] += 1
        if is_fraud:
            self.stats['fraud'] += 1
        else:
            self.stats['safe'] += 1
        
        # Update UI
        self.update_stats_display()
        self.refresh_history_display()
        
        # Save to file
        self.save_transactions()
        
        # Clear form
        self.clear_form()
        
        # Show result
        result_color = "red" if is_fraud else "green"
        messagebox.showinfo("Analysis Complete", 
                           f"Transaction Analyzed!\n\n"
                           f"Risk Level: {risk['level']}\n"
                           f"Fraud Score: {score}%\n"
                           f"Action: {risk['action']}\n\n"
                           f"Transaction ID: {transaction['id']}")
    
    def clear_form(self):
        for field_name, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set(widget['values'][0] if widget['values'] else '')
            else:
                if field_name == 'hour':
                    widget.delete(0, tk.END)
                    widget.insert(0, str(datetime.now().hour))
                elif field_name in ['transaction_id', 'amount', 'card_id', 'merchant_name']:
                    widget.delete(0, tk.END)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, '0')
    
    def update_stats_display(self):
        self.total_label.config(text=str(self.stats['total']))
        self.fraud_label.config(text=str(self.stats['fraud']))
        self.safe_label.config(text=str(self.stats['safe']))
    
    def refresh_history_display(self):
        self.history_text.delete(1.0, tk.END)
        
        if not self.transactions:
            self.history_text.insert(tk.END, "\n\n   No transactions yet.\n   Enter a transaction to analyze.")
            return
        
        for tx in self.transactions:
            result = tx['result']
            
            # Color coding
            risk_symbol = "🚨" if result['is_fraud'] else "✅"
            
            self.history_text.insert(tk.END, f"\n{'='*60}\n")
            self.history_text.insert(tk.END, f"{risk_symbol} {tx['merchant_name']} - ${tx['amount']:.2f}\n", 'bold')
            self.history_text.insert(tk.END, f"ID: {tx['id']} | {tx['timestamp']}\n")
            self.history_text.insert(tk.END, f"{'-'*60}\n")
            self.history_text.insert(tk.END, f"Risk Level: {result['risk_level']} | ", 'info')
            self.history_text.insert(tk.END, f"Score: {result['fraud_probability']*100:.1f}%\n", 'info')
            self.history_text.insert(tk.END, f"Action: {result['recommended_action']}\n", 'action')
            
            if result['reasons']:
                self.history_text.insert(tk.END, f"\nRisk Factors:\n", 'info')
                for reason in result['reasons']:
                    self.history_text.insert(tk.END, f"  • {reason}\n")
            
            self.history_text.insert(tk.END, "\n")
        
        # Configure tags
        self.history_text.tag_config('bold', font=('Courier', 10, 'bold'))
        self.history_text.tag_config('info', foreground='#2563eb')
        self.history_text.tag_config('action', foreground='#dc2626', font=('Courier', 9, 'bold'))
    
    def clear_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all transaction history?"):
            self.transactions = []
            self.stats = {'total': 0, 'fraud': 0, 'safe': 0}
            self.update_stats_display()
            self.refresh_history_display()
            self.save_transactions()
    
    def save_transactions(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    'transactions': self.transactions,
                    'stats': self.stats
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_transactions(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    self.stats = data.get('stats', {'total': 0, 'fraud': 0, 'safe': 0})
        except Exception as e:
            print(f"Error loading data: {e}")

def main():
    root = tk.Tk()
    app = FraudDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()