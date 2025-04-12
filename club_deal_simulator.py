import taipy.gui as gui
import math

# --- Variabili di Stato (Inputs e Outputs) ---
# Input - Valutazione e Struttura Iniziale
ebitda_target = 1.5  # Milioni di €
ev_multiple_entry = 6.5
acquisition_percentage = 70.0 # %
debt_multiple_entry = 3.0
transaction_costs_percentage = 3.0 # % dell'EV

# Input - Performance e Exit
holding_period_years = 5
ebitda_exit = 2.5 # Milioni di € (Alternativa: crescita annua)
ev_multiple_exit = 7.0
net_debt_exit = 4.0 # Milioni di € (Assumiamo un valore fisso per semplicità)

# Input - Struttura Ritorno Investitori
hurdle_rate_percentage = 8.0 # % annuo
carried_interest_percentage = 20.0 # %

# Output - Calcolati
ev_entry = 0.0
debt_entry = 0.0
equity_value_entry = 0.0
equity_needed_for_stake = 0.0
transaction_costs_value = 0.0
total_equity_required = 0.0

ev_exit = 0.0
equity_value_exit = 0.0
club_proceeds_exit = 0.0

preferred_return_amount = 0.0
profit_after_pref = 0.0
carried_interest_amount = 0.0
investor_total_return = 0.0
investor_moic = 0.0

# --- Funzione di Calcolo ---
def calculate_deal_metrics(state):
    print("Calculating metrics...")
    try:
        # Calcoli all'Entrata
        state.ev_entry = state.ebitda_target * state.ev_multiple_entry
        state.debt_entry = state.ebitda_target * state.debt_multiple_entry
        state.equity_value_entry = state.ev_entry - state.debt_entry
        state.equity_needed_for_stake = state.equity_value_entry * (state.acquisition_percentage / 100.0)
        state.transaction_costs_value = state.ev_entry * (state.transaction_costs_percentage / 100.0)
        # Equity totale = Equity per la quota + Costi transazione
        state.total_equity_required = state.equity_needed_for_stake + state.transaction_costs_value

        # Calcoli all'Uscita
        state.ev_exit = state.ebitda_exit * state.ev_multiple_exit
        state.equity_value_exit = state.ev_exit - state.net_debt_exit
        state.club_proceeds_exit = state.equity_value_exit * (state.acquisition_percentage / 100.0)

        # Calcoli Waterfall e Carry
        hurdle_rate = state.hurdle_rate_percentage / 100.0
        capital_invested = state.total_equity_required

        # Return of Capital (implicito nel calcolo dei profitti)
        # Preferred Return
        preferred_return_amount = capital_invested * (math.pow(1 + hurdle_rate, state.holding_period_years) - 1)
        state.preferred_return_amount = preferred_return_amount

        total_profit = max(0, state.club_proceeds_exit - capital_invested - preferred_return_amount)

        # Carried Interest
        carried_interest_amount = total_profit * (state.carried_interest_percentage / 100.0)
        state.carried_interest_amount = carried_interest_amount

        # Ritorno Investitori
        investor_share_of_profit = total_profit * (1 - (state.carried_interest_percentage / 100.0))
        investor_total_return = capital_invested + preferred_return_amount + investor_share_of_profit
        state.investor_total_return = min(investor_total_return, state.club_proceeds_exit)

        # MoIC Investitori
        if capital_invested > 0:
            moic_investitori = investor_total_return / capital_invested
            state.investor_moic = moic_investitori

    except Exception as e:
        print(f"Errore nel calcolo: {e}")

# --- Definizione Pagina HTML/Markdown con Taipy ---
# Usiamo Markdown esteso di Taipy per creare l'interfaccia
# <|{variable}|component_type|properties...|>

# --- Definizione Pagina HTML/Markdown con Taipy ---
page = """
# Club Deal Simulator - Stima Fabbisogno Equity e Carry

---
## Ipotesi Chiave

<|layout|columns=1 1 1|gap=1.5rem|
<|part id=part1_card class_name="card card-bg"|
### Target & Struttura Iniziale {: .h5 .mt-0 .mb-2}
**Target EBITDA (M€):**<br/>
<|{ebitda_target}|input|label="Target EBITDA (M€)"|class_name=fullwidth|>
<br/>
**Mult. EV/EBITDA Ingresso:**<br/>
<|{ev_multiple_entry}|slider|min=4|max=12|step=0.5|continuous=false|> <|{int(ev_multiple_entry) if ev_multiple_entry.is_integer() else ev_multiple_entry}|>x
<br/>
**Quota Acquisita (%):**<br/>
<|{acquisition_percentage}|slider|min=10|max=100|step=5|continuous=false|> <|{int(acquisition_percentage)}|>%
<br/>
**Mult. Debito/EBITDA Ingresso:**<br/>
<|{debt_multiple_entry}|slider|min=0|max=6|step=0.5|continuous=false|> <|{int(debt_multiple_entry) if debt_multiple_entry.is_integer() else debt_multiple_entry}|>x
<br/>
**Costi Transazione (% EV):**<br/>
<|{transaction_costs_percentage}|slider|min=0|max=5|step=0.5|continuous=false|> <|{transaction_costs_percentage}|>%
|>

<|part id=part2_card class_name="card card-bg"|
### Performance & Exit {: .h5 .mt-0 .mb-2}
**Holding Period (Anni):**<br/>
<|{holding_period_years}|input|label="Holding Period (Anni)"|class_name=fullwidth|>
<br/>
**EBITDA alla Exit (M€):**<br/>
<|{ebitda_exit}|input|label="EBITDA alla Exit (M€)"|class_name=fullwidth|>
<br/>
**Mult. EV/EBITDA Uscita:**<br/>
<|{ev_multiple_exit}|slider|min=4|max=12|step=0.5|continuous=false|> <|{int(ev_multiple_exit) if ev_multiple_exit.is_integer() else ev_multiple_exit}|>x
<br/>
**Debito Netto alla Exit (M€):**<br/>
<|{net_debt_exit}|input|label="Debito Netto alla Exit (M€)"|class_name=fullwidth|>
|>

<|part id=part3_card class_name="card card-bg"|
### Struttura Ritorno & Azione {: .h5 .mt-0 .mb-2}
**Hurdle Rate Annuale (%):**<br/>
<|{hurdle_rate_percentage}|slider|min=0|max=15|step=1|continuous=false|> <|{int(hurdle_rate_percentage)}|>%
<br/>
**Carried Interest (%):**<br/>
<|{carried_interest_percentage}|slider|min=0|max=30|step=5|continuous=false|> <|{int(carried_interest_percentage)}|>%
<br/>
<br/>
<|Calcola|button|on_action=calculate_deal_metrics|class_name=plain|>
|>
|>

---
## Risultati Stimati

<|layout|columns=1 1|gap=1.5rem|
<|part id=results1_card class_name="card card-bg"|
### Fabbisogno di Equity {: .h5 .mt-0 .mb-2}
**Enterprise Value Ingresso:** <|{ev_entry}|text|format=%.2f M€|>
**Debito Ingresso:** <|{debt_entry}|text|format=%.2f M€|>
**Equity Value Totale Ingresso:** <|{equity_value_entry}|text|format=%.2f M€|>
**Equity per Quota ({int(acquisition_percentage)}%):** <|{equity_needed_for_stake}|text|format=%.2f M€|>
**Costi Transazione:** <|{transaction_costs_value}|text|format=%.2f M€|>
**==> Fabbisogno Totale Equity:** <|{total_equity_required}|text|format=%.2f M€|raw|>
|>

<|part id=results2_card class_name="card card-bg"|
### Ritorno & Carried Interest {: .h5 .mt-0 .mb-2}
**Enterprise Value Uscita:** <|{ev_exit}|text|format=%.2f M€|>
**Equity Value Totale Uscita:** <|{equity_value_exit}|text|format=%.2f M€|>
**Proventi Lordi Club ({int(acquisition_percentage)}%):** <|{club_proceeds_exit}|text|format=%.2f M€|>
**Ritorno Preferenziale Investitori:** <|{preferred_return_amount}|text|format=%.2f M€|>
**==> Carried Interest Promotore:** <|{carried_interest_amount}|text|format=%.2f M€|raw|>
**Ritorno Totale Investitori:** <|{investor_total_return}|text|format=%.2f M€|>
**MoIC Investitori:** <|{investor_moic}|text|format=%.2f x|>
|>
|>

"""

# --- Avvio dell'Applicazione ---
if __name__ == "__main__":
    # Calcola i valori iniziali al caricamento
    # # Creiamo uno stato iniziale fittizio per il primo calcolo
    # class InitialState:
    #     pass
    # initial_state = InitialState()
    # for var in ['ebitda_target', 'ev_multiple_entry', 'acquisition_percentage',
    #             'debt_multiple_entry', 'transaction_costs_percentage', 'holding_period_years',
    #             'ebitda_exit', 'ev_multiple_exit', 'net_debt_exit', 'hurdle_rate_percentage',
    #             'carried_interest_percentage', 'ev_entry', 'debt_entry', 'equity_value_entry',
    #             'equity_needed_for_stake', 'transaction_costs_value', 'total_equity_required',
    #             'ev_exit', 'equity_value_exit', 'club_proceeds_exit', 'preferred_return_amount',
    #             'profit_after_pref', 'carried_interest_amount', 'investor_total_return', 'investor_moic']:
    #     setattr(initial_state, var, globals()[var])

    # calculate_deal_metrics(initial_state)

    # # Aggiorniamo le variabili globali con i risultati iniziali
    # for var in ['ev_entry', 'debt_entry', 'equity_value_entry', 'equity_needed_for_stake',
    #             'transaction_costs_value', 'total_equity_required', 'ev_exit', 'equity_value_exit',
    #             'club_proceeds_exit', 'preferred_return_amount', 'profit_after_pref',
    #             'carried_interest_amount', 'investor_total_return', 'investor_moic']:
    #      globals()[var] = getattr(initial_state, var)

    gui.Gui(page=page).run(use_reloader=True, title="Club Deal Simulator", port=5001)
