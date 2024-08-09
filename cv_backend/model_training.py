#%% md
# 
#%%
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

df = pd.read_csv('/Users/Tommy Anthony/OneDrive - Liberty University/Documents/cv_webapp/cv-app/cv_backend/chile_verde3.csv')
df = df[df['Net_Sales'] >= 2100]
#%%
#Date parsing
df['Date'] = pd.to_datetime(df['Date'])
df['year'] = df['Date'].dt.year
df['month'] = df['Date'].dt.month
df['day'] = df['Date'].dt.day
df['day_of_week'] = df['Date'].dt.dayofweek
df = df.drop(columns=['Date'])
#%%
categorical_columns = ['holiday', 'is_gameday', 'is_pride_festival', 'is_arnold', 'Common Weather Description']
df = df.fillna(0)
df = pd.get_dummies(df, columns= categorical_columns)
#%%
#Target variable definition
X = df.drop(columns=['Net_Sales', 'Orders', 'Guests'])
y_sales = df['Net_Sales']
y_orders = df['Orders']
y_guests = df['Guests']
feature_names = X.columns.tolist()
X.to_csv('X.csv', index=False)
#%%
#Training and testing groups
X_train, X_test, y_sales_train, y_sales_test = train_test_split(X, y_sales, test_size=0.2, random_state=42)
_, _, y_orders_train, y_orders_test = train_test_split(X, y_orders, test_size=0.2, random_state=42)
_, _, y_guests_train, y_guests_test = train_test_split(X, y_guests, test_size=0.2, random_state=42)
#%%
def testing(x_train, y_train, x_test, y_test):
    gbr = GradientBoostingRegressor(random_state=42)
    gbr.fit(x_train, y_train)
    y_pred = gbr.predict(x_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"Mean Squared Error: {mse}")
    print(f"Mean Absolute Error: {mae}")
    print(f"R² Score: {r2}")
    
    return gbr

final_sales = testing(X_train, y_sales_train, X_test, y_sales_test)
final_orders = testing(X_train, y_orders_train, X_test, y_orders_test)
final_guests = testing(X_train, y_guests_train, X_test, y_guests_test)
#%%
final_model = {
    'model_sales': final_sales,
    'model_orders': final_orders,
    'model_guests': final_guests,
    'feature_names': feature_names
}

with open('/Users/Tommy Anthony/OneDrive - Liberty University/Documents/cv_webapp/cv-app/cv_backend/cv_model.pkl', 'wb') as file:
    pickle.dump(final_model, file)
# %%
