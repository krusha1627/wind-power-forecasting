import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np 


from sklearn.preprocessing import StandardScaler
train_df = pd.read_csv("train.csv")

X = train_df.drop(columns=['production'])
y = train_df['production']


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)



from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

print("Before conversion:", train_df.dtypes)
train_df['date'] = pd.to_datetime(train_df['date'], errors='coerce')
print("After conversion:", train_df.dtypes)
print("Missing values in date column:", train_df['date'].isnull().sum())
train_df = train_df.dropna(subset=['date'])

train_df['hour'] = train_df['date'].dt.hour
train_df['day'] = train_df['date'].dt.day
train_df['month'] = train_df['date'].dt.month
train_df['year'] = train_df['date'].dt.year

train_df['wind_speed_10m'] = np.sqrt(train_df['u10']**2 + train_df['v10']**2)
train_df['wind_speed_100m'] = np.sqrt(train_df['u100']**2 + train_df['v100']**2)

train_df['wind_dir_10m'] = np.arctan2(train_df['v10'], train_df['u10']) * 180 / np.pi
train_df['wind_dir_100m'] = np.arctan2(train_df['v100'], train_df['u100']) * 180 / np.pi




print(train_df.isnull().sum())



train_df['wind_speed_10m'] = np.sqrt(train_df['u10']**2 + train_df['v10']**2)
train_df['wind_speed_100m'] = np.sqrt(train_df['u100']**2 + train_df['v100']**2)

plt.figure(figsize=(12, 6))
plt.scatter(train_df['wind_speed_100m'], train_df['production'], alpha=0.5)
plt.title('Wind Speed Magnitude (100m) vs. Production')
plt.xlabel('Wind Speed Magnitude (100m)')
plt.ylabel('Production')
plt.show()





corr_matrix = train_df[['u10', 'v10', 'u100', 'v100', 'production']].corr()


plt.figure(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()










train_df['date'] = pd.to_datetime(train_df['date'])

plt.figure(figsize=(12, 6))
plt.plot(train_df['date'], train_df['production'], label='Production')
plt.title('Wind Power Production Over Time')
plt.xlabel('Date')
plt.ylabel('Production')
plt.legend()
plt.xticks(rotation=45)  
plt.tight_layout()
plt.show()



plt.figure(figsize=(10, 6))
sns.histplot(train_df['production'], kde=True, bins=50)
plt.title('Distribution of Wind Power Production')
plt.xlabel('Production')
plt.ylabel('Frequency')
plt.show()

