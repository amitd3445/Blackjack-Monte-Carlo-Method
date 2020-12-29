import blackjack_actions as ba
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

decision_matrix = pd.read_csv('../Blackjack Monte Carlo Method/Blackjack_Decision_Matrix.csv', index_col=0)

blackjack_game = ba.Game(decision_matrix=decision_matrix, number_of_decks=6, minimum_number_of_cards=20, dealer_max_total_to_hit=17)

df_blackjack_results = pd.DataFrame(columns=['game_result', 'number_of_cards_played', 'count'])

for _ in range(250000):
    blackjack_game.one_round()
    df_blackjack_results = df_blackjack_results.append({'game_result':blackjack_game.result,
                                                        'number_of_cards_played':len(blackjack_game.deck.cards), 
                                                        'count':blackjack_game.count}, ignore_index=True)
    blackjack_game.restart_table()

# expected retun with a basis of one is equal to the total sum of results divided by the absolute sum

df_total_sum = pd.pivot_table(df_blackjack_results, values='game_result', index='count', columns='number_of_cards_played', aggfunc=np.sum)

bin_number_of_cards = np.linspace(start=df_total_sum.columns.values[0], stop=df_total_sum.columns.values[-1], num=11, endpoint=True).round(decimals=0)
label_number_of_cards = [f'{int(bin_number_of_cards[i])}-{int(bin_number_of_cards[i+1])}' for i in range(len(bin_number_of_cards)-1)]
bin_count = np.round(np.linspace(start=df_total_sum.index.values[0], stop=df_total_sum.index.values[-1], num=11, endpoint=True),0)
label_count = [f'({int(bin_count[i])})-({int(bin_count[i+1])})' for i in range(len(bin_count)-1)]

df_total_sum = df_total_sum.groupby(pd.cut(df_total_sum.index, bins=bin_count, labels=label_count), axis=0).sum()
df_total_sum = df_total_sum.groupby(pd.cut(df_total_sum.columns, bins=bin_number_of_cards, labels=label_number_of_cards), axis=1).sum()

df_blackjack_results['game_result'] = df_blackjack_results['game_result'].apply(np.absolute)
df_absolute_sum = pd.pivot_table(df_blackjack_results, values='game_result', index='count', columns='number_of_cards_played', aggfunc=np.sum)
df_absolute_sum = df_absolute_sum.groupby(pd.cut(df_absolute_sum.index, bins=bin_count, labels=label_count), axis=0).sum()
df_absolute_sum = df_absolute_sum.groupby(pd.cut(df_absolute_sum.columns, bins=bin_number_of_cards, labels=label_number_of_cards), axis=1).sum()

df_expected_return = df_total_sum.div(df_absolute_sum)

sns.heatmap(df_expected_return, fmt="g", cmap='viridis', annot=True, annot_kws={"size":8})
plt.xticks(rotation=45)
plt.xlabel('Cards Played')
plt.yticks(rotation=-45)
plt.ylabel('Count')
plt.show()