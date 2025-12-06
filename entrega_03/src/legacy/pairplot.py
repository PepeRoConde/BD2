import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("listings.csv")

#n = 15
#df_subset = df.iloc[:, :n]

sns.pairplot(df, diag_kind="hist")
plt.show()

